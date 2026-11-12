"""Step 1 (no LLM): file graph from code structure + co-change, clustered and scored."""
import json
import math
import os
import subprocess
import sys
from collections import Counter
from dataclasses import dataclass
from itertools import combinations
from pathlib import Path

import networkx as nx

CODE_EXT = {".py", ".rs", ".ts", ".tsx", ".js", ".jsx", ".go", ".java", ".kt", ".c", ".h", ".cc", ".cpp",
            ".hpp", ".cs", ".rb", ".php", ".swift", ".scala"}
MAX_COMMIT_FILES = 30  # bigger commits are sweeps (formatting, renames), not evidence of coupling
MAX_CLUSTER = 40       # clusters with more files than this are split again


@dataclass
class Index:
    repo: Path
    files: set[str]                # every tracked file
    graph: nx.Graph                # code files; edge attrs: weight, structure, cochange
    clusters: dict[str, list[str]] # cluster id -> files, a flat list with the largest cluster first
    score: dict[str, float]        # importance of each code file

    def top_files(self, files, n=8):
        return sorted(files, key=lambda f: -self.score.get(f, 0))[:n]


def git(repo, *args):
    return subprocess.run(["git", "-C", str(repo), *args], capture_output=True, text=True,
                          errors="replace", check=True).stdout


def structure_edges(repo, code):
    """Run Graphify (tree-sitter, no LLM) and roll its symbol-level edges up to file pairs."""
    env = {k: v for k, v in os.environ.items() if "KEY" not in k and "TOKEN" not in k}
    subprocess.run([Path(sys.executable).parent / "graphify", "update", ".", "--no-cluster"],
                   cwd=repo, env=env, check=True, capture_output=True)
    g = json.loads((repo / "graphify-out" / "graph.json").read_text())
    file_of = {n["id"]: n.get("source_file") for n in g["nodes"]}
    edges = Counter()
    for e in g["links"]:
        a, b = file_of.get(e["source"]), file_of.get(e["target"])
        if a in code and b in code and a != b:
            edges[tuple(sorted((a, b)))] += 1
    return edges


def cochange_edges(repo, code):
    """File pairs changed in the same commit at least twice, as a 0..1 strength."""
    # --no-renames: rename detection would download old file contents in a blobless clone.
    # Each commit prints "@@<hash>" then its files; the hash line is dropped by the `& code` filter below.
    log = git(repo, "log", "--no-merges", "--no-renames", "--name-only", "--format=@@%h", "-n", "20000")
    commits_of, together = Counter(), Counter()
    for commit in log.split("@@"):
        changed = sorted(set(commit.splitlines()) & code)
        if len(changed) > MAX_COMMIT_FILES:
            continue
        commits_of.update(changed)
        together.update(combinations(changed, 2))
    return {pair: n / math.sqrt(commits_of[pair[0]] * commits_of[pair[1]])
            for pair, n in together.items() if n >= 2}


def cluster(graph):
    """Louvain, run again inside any group that is still too large. Returns a flat list of file groups."""
    # Files are numbered before clustering: networkx walks sets internally, and a set of strings
    # changes order from one run to the next, which would change the clusters. Integers do not.
    names = sorted(graph)
    numbered = nx.relabel_nodes(graph, {name: number for number, name in enumerate(names)})
    return [[names[number] for number in sorted(group)] for group in _split(numbered)]


def _split(graph):
    parts = nx.community.louvain_communities(graph, weight="weight", seed=0)
    groups = []
    for part in parts:
        groups += _split(graph.subgraph(part)) if len(part) > MAX_CLUSTER and len(parts) > 1 else [part]
    return groups


def build(repo):
    repo = Path(repo).resolve()
    files = set(git(repo, "ls-files").splitlines())
    code = {f for f in files if Path(f).suffix in CODE_EXT}
    structure, cochange = structure_edges(repo, code), cochange_edges(repo, code)

    # Both signals are scaled to 0..1 and added; this mix scored best in our benchmark.
    top = math.log1p(max(structure.values(), default=1))
    graph = nx.Graph()
    for pair in sorted(structure.keys() | cochange.keys()):  # sorted so clustering is the same on every run
        s = math.log1p(structure.get(pair, 0)) / top
        c = cochange.get(pair, 0.0)
        graph.add_edge(*pair, weight=s + c, structure=structure.get(pair, 0), cochange=round(c, 2))

    rank = nx.pagerank(graph, weight="weight")
    score = {f: r * (0.3 if "test" in f.lower() else 1.0) for f, r in rank.items()}
    groups = sorted(cluster(graph), key=len, reverse=True)
    clusters = {str(number): group for number, group in enumerate(groups, 1)}
    return Index(repo, files, graph, clusters, score)


GRAPH_NOTE = """Precomputed graph files; read them with your normal shell tools:
- {folder}/clusters.md: clusters of code files that reference each other or change together. Each cluster \
lists all its files, most important first.
- {folder}/files.tsv: one row per code file: path, cluster, importance rank (1 = most important).
- {folder}/links.tsv: one row per linked pair of files: file_a, file_b, references (code references between \
them), co_change (0 to 1: how often they change in the same commit). Strongest links first.
  Example: rg "engine/component.rs" {folder}/links.tsv | head -20"""


def save_graph(index, folder):
    """Write the clusters, file ranks and links as plain text files. Returns a note describing them for the agents."""
    folder.mkdir(parents=True, exist_ok=True)
    ranked = index.top_files(index.score, len(index.score))
    cluster_of = {f: cid for cid, files in index.clusters.items() for f in files}

    lines = ["# Clusters of related code files", ""]
    for cid, files in index.clusters.items():
        folders = Counter(str(Path(f).parent) for f in files).most_common(3)
        lines += [f"## Cluster {cid} ({len(files)} files)",
                  "Main folders: " + ", ".join(f"{name} ({n})" for name, n in folders),
                  *[f"- {f}" for f in index.top_files(files, len(files))], ""]
    (folder / "clusters.md").write_text("\n".join(lines))

    (folder / "files.tsv").write_text("path\tcluster\timportance_rank\n" + "".join(
        f"{f}\t{cluster_of[f]}\t{rank}\n" for rank, f in enumerate(ranked, 1)))

    links = sorted(index.graph.edges(data=True), key=lambda edge: -edge[2]["weight"])
    (folder / "links.tsv").write_text("file_a\tfile_b\treferences\tco_change\n" + "".join(
        f"{a}\t{b}\t{d['structure']}\t{d['cochange']}\n" for a, b, d in links))
    return GRAPH_NOTE.format(folder=folder)
