# WikiGen

Generates a DeepWiki-style wiki for a codebase, for humans and coding agents. The agent work is done by OpenAI's Codex coding agent, running read-only inside the repository.

## Run

```bash
git clone --filter=blob:none https://github.com/cocoindex-io/cocoindex.git repos/cocoindex
```

```bash
.venv/bin/python -m wikigen repos/cocoindex --out out/cocoindex
```

Needs the Codex CLI installed. With `OPENAI_API_KEY` in `.env`, Codex bills that key and keeps its settings in `.codex-home/`, leaving your normal Codex login untouched. Without a key, it uses your Codex login (`codex login status`). A rerun reuses `toc.json` and only writes pages that are missing.

## Browse

```bash
.venv/bin/python -m wikigen.serve out --port 8766
```

Opens every wiki under `out/` in a DeepWiki-style viewer: page tree on the left, citations as chips that open the cited lines on GitHub at the pinned commit, and rendered diagrams.

## How it works

| Step | File | What happens |
|---|---|---|
| 1 | `wikigen/index.py` | No LLM. Graphify extracts code references, git history gives co-change; both become one file graph, which is clustered and scored, then saved as plain files. |
| 2 | `wikigen/plan.py` | The planner agent explores and answers with a table-of-contents tree, organised by how a reader learns the project. Checks send problems back to it. |
| 3 | `wikigen/write.py` (`shape_section`) | One writer agent per first-level section explores its section and decides the final sub-pages: it may keep, split, merge, rename or add them. |
| 4 | `wikigen/write.py` (`write_section`) | The same writers write their pages one at a time, sections in parallel. |
| 5 | `wikigen/write.py` (`write_overview_and_glossary`) | The planner writes the overview and glossary from every page's summary and terms. |
| 6 | `wikigen/write.py` (`assemble`) | Writes the index, `file_map.json` and `report.json`. |

Step 3 finishes for every section before step 4 starts, so writers link to the final page list.

Supporting files:

- `wikigen/agent.py`: one Codex conversation as `agent.ask(prompt, schema=None) -> str`, plus `ask_checked`, which sends an answer's problems back to the agent.
- `wikigen/serve.py` and `wikigen/viewer.html`: the local viewer.

## Graph files

Step 1 writes three files to `<out>/graph/`. The agents are told where they are and read them with ordinary shell tools; there are no custom tools.

| File | One row per | Columns |
|---|---|---|
| `clusters.md` | cluster (as a section) | its main folders, then every file, most important first |
| `files.tsv` | code file | path, cluster, importance rank |
| `links.tsv` | linked pair of files | file_a, file_b, references, co_change; strongest first |

## Output

- `<page-id>.md`: one page per table-of-contents node, with `[path:start-end]` citations.
- `README.md` / `llms.txt`: the index, with a one-line scope per page.
- `toc.json`: the tree. `file_map.json`: source file to the pages that cite it.
- `report.json`: page count, words, citations per page, coverage of important files, token usage, estimated cost (API key only), minutes. `usage.json` holds the running token count during a run.

## Not done yet

- Mermaid diagrams are not syntax-checked, and writers rarely produce them.
- One planner only; very large repos would need planning to be split across several planners.
- There is no cap on how much an agent explores per page.
