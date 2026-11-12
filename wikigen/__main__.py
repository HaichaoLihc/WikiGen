"""Generate a wiki for a repository:  python -m wikigen <repo> --out out/<name>"""
import argparse
import json
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from dotenv import load_dotenv

from . import agent as agents
from . import index as indexing
from . import plan as planning
from . import write as writing
from .agent import Agent


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("repo", help="path to a local git clone")
    parser.add_argument("--out", required=True, type=Path, help="folder for the generated wiki")
    parser.add_argument("--pages", type=int, help="target number of pages (default: scales with repo size)")
    parser.add_argument("--planner-model", help="default: gpt-6.1-sol on an API key, Codex's own default on a login")
    parser.add_argument("--writer-model", help="default: gpt-6.1-terra on an API key, Codex's own default on a login")
    parser.add_argument("--workers", type=int, default=4, help="writer agents running at once")
    args = parser.parse_args()
    out = args.out.resolve()
    started = time.time()

    load_dotenv(".env")
    if agents.api_key_home():  # OPENAI_API_KEY is set: bill the key, with models whose prices we know
        args.planner_model, args.writer_model = args.planner_model or "gpt-6.1-sol", args.writer_model or "gpt-6.1-terra"
        print("auth: OpenAI API key")
    else:
        print("auth: your Codex login")

    print("1/6 building the file graph (code structure + co-change)")
    index = indexing.build(args.repo)
    graph_note = indexing.save_graph(index, out / "graph")
    print(f"    {len(index.score)} code files, {index.graph.number_of_edges()} links, {len(index.clusters)} clusters")

    toc_file = out / "toc.json"
    saved = json.loads(toc_file.read_text()) if toc_file.exists() else {}
    planner_system, writer_system = f"{planning.SYSTEM}\n\n{graph_note}", f"{writing.SYSTEM}\n\n{graph_note}"

    def save(toc, shaped):
        source = {"url": indexing.git(index.repo, "remote", "get-url", "origin").strip().removesuffix(".git"),
                  "commit": indexing.git(index.repo, "rev-parse", "HEAD").strip()}
        toc_file.write_text(json.dumps({"planner_session": planner.session, "shaped": shaped,
                                        "source": source, "pages": toc}, indent=1))

    if saved:  # a rerun keeps the table of contents and only does what is missing
        toc = saved["pages"]
        planner = Agent(planner_system, index.repo, args.planner_model, saved["planner_session"])
        print(f"2/6 reusing the table of contents in {toc_file} ({len(toc)} pages)")
    else:
        print("2/6 planning the table of contents")
        planner = Agent(planner_system, index.repo, args.planner_model)
        # Pages grow with the square root of the code size: about 20 for 100 files, 48 for 570, capped at 60.
        target = args.pages or max(8, min(60, round(2 * len(index.score) ** 0.5)))
        toc = planning.plan(planner, index, target)
        save(toc, shaped=False)
        (out / "toc_planner.json").write_text(json.dumps(toc, indent=1))  # kept as the planner wrote it
        print(f"    {len(toc)} pages")

    # One writer agent per first-level section. It keeps its conversation from shaping through writing.
    sections = [p for p in toc if not p["parent"] and p["id"] not in ("overview", "glossary")]
    writers = {s["id"]: Agent(writer_system, index.repo, args.writer_model) for s in sections}
    with ThreadPoolExecutor(args.workers) as pool:
        if not saved.get("shaped"):
            print(f"3/6 {len(sections)} writers shape their sections")
            shaped = pool.map(lambda s: writing.shape_section(toc, index, writers[s["id"]], s), sections)
            toc = [toc[0], *[page for pages in shaped for page in pages], toc[-1]]
            save(toc, shaped=True)
            print(f"    {len(toc)} pages")
        wiki = writing.Wiki(index, toc, out)
        print(f"4/6 writing {len(sections)} sections, {args.workers} at a time")
        list(pool.map(lambda s: writing.write_section(wiki, writers[s["id"]], s), sections))

    print("5/6 writing overview and glossary")
    writing.write_overview_and_glossary(wiki, planner)

    print("6/6 assembling")
    report = writing.assemble(wiki)
    report["minutes"] = round((time.time() - started) / 60, 1)
    report["estimated_cost_usd"] = agents.estimated_cost()
    (out / "report.json").write_text(json.dumps(report, indent=1))
    print(json.dumps(report, indent=1))


if __name__ == "__main__":
    main()
