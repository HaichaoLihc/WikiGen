# cocoindex: our wiki (v5) against DeepWiki

Both wikis describe `cocoindex-io/cocoindex` at commit `f7078f01`. Ours is `out/cocoindex-v5`; DeepWiki's pages are saved in `out/deepwiki/cocoindex.json`. The earlier comparison of v3 is in `cocoindex-v3-vs-deepwiki.md`. A Go comparison was planned alongside this one and left out at the user's request.

Short version: on the five page pairs reviewed blind, ours was judged better every time, mainly because its statements and line citations were right and DeepWiki's often were not. DeepWiki is still broader, easier to read, has more diagrams, and covers the example pipelines, which we do not.

## Whole-wiki numbers

The v3 column was recomputed with the same script as the other two.

| | Ours (v5) | Ours (v3) | DeepWiki |
|---|---|---|---|
| Pages | 58 | 58 | 55 |
| Words (median per page) | 38,185 (610) | 34,014 (545) | 41,723 (754) |
| Shortest and longest page, in words | 422 and 2,574 | 386 and 2,701 | 271 and 1,130 |
| Citations per page | 35.9 | 30.7 | 31.5 |
| Citations that point to a real file and a valid line range | 100% | 100% | 98.2% |
| Citations into source code | 80% | 79% | 59% |
| Citations into docs | 8% | 7% | 17% |
| Citations into examples | 4% | 5% | 11% |
| Citations into tests and benchmarks | 3% | 4% | 6% |
| Citations into config, CI and dev scripts | 5% | 5% | 6% |
| Files cited | 267 | 302 | 253 |
| Most important files cited (top 57 by graph score) | 52 | 47 | 45 |
| Diagrams | 57 | 57 | 124 |
| Diagram types | 39 flowchart, 17 sequence, 1 state | 56 flowchart, 1 sequence | 112 flowchart, 10 sequence, 2 class |
| Tables | 61 | 46 | 54 |
| Code excerpts (pages that have one) | 62 (56) | 4 (3) | 39 (16) |
| Code names mentioned that occur nowhere in the repo | 1 of 427 | not measured | 19 of 569 |

Notes on the table:

- All page counts include the overview and the glossary. DeepWiki's `<details>` file lists and scraping leftovers are excluded.
- DeepWiki has 31 invalid citations: 29 point to 8 files that do not exist at this commit (for example `rust/state_store/storage.rs` and `rust/sdk/cocoindex/src/lancedb.rs`), and 2 run one line past the end of the file. Its 29 whole-file citations with no line range are not counted.
- DeepWiki's figures differ slightly from the v3 report (31.5 citations per page against 30.3, 98.2% against 98.3%) because this count also includes its citations written without the trailing `()`.
- The last row takes every snake_case or CamelCase name written in backticks outside code blocks and looks for it anywhere in the repo's files. Our one miss is the wildcard `*_by_name`, not an invented name. DeepWiki's 19 include `QueryOutput`, `QueryInfo`, `AuthRegistry`, `add_auth_entry`, `PgTableTarget` and `TurbopufferCollectionTarget`. The check only shows that a name exists, not that it is described correctly.
- Our pages follow one pattern: 57 of 58 have exactly one diagram, and 56 have a code excerpt. Every DeepWiki page has two to four diagrams; 16 have a code excerpt.
- Our glossary is 2,574 words with no citations. DeepWiki's is 849 words with 41.

### What changed from v3 to v5

Pages are about 12% longer, citations per page rose from 30.7 to 35.9, code excerpts went from 4 to 62, and a third of the diagrams are now sequence diagrams instead of nearly all flowcharts. Coverage of the most important files rose from 47 to 52 of 57, while the number of distinct files cited fell from 302 to 267. Every citation is still valid.

## Table of contents

Each cell lists a first-level section in bold with its page count, then its pages; third-level pages are in brackets after their parent. Rows group the sections by subject.

| Subject | Ours (10 first-level entries) | DeepWiki (12 first-level entries) |
|---|---|---|
| Start | **Overview** (1)<br>**Architecture** (3): Getting Started; Repository Layout | **Overview** (3): Getting Started; Documentation Site<br>**Architecture Overview** (6): Python SDK Overview; Rust Engine Internals (PyO3 Integration and Build System, CI/CD Pipeline); Rust SDK |
| Writing a pipeline | **Pipeline Programming** (11): Apps and Environments; Processing Components; Context and User State; Functions (Batched Functions); Target States; Types and Serialization; Live Components (LiveMap and Live Feeds); Shared Resources | **Core Programming Model** (6): App and Processing Components; Functions, Memoization, and Change Detection; Context and Resource Sharing; Target States and Connectors; Live Mode and Live Components<br>**Advanced Topics** (6): Custom Target Connectors; Memoization Keys and Memo States; Exception Handling and Concurrency; Configuration, Environments, and Internal Storage; Structural Code Analysis (code_ast and code_match) |
| How the engine runs it | **Incremental Engine** (8): Component Execution; Memoization; Logic Change Detection; Target Reconciliation; State Storage; Submit Transactions; Scheduling and Failure Handling | **Incremental Processing and State Management** (3): UpdateHandle and Progress Monitoring; Setup, Drop, and Resource Lifecycle |
| Language bindings | **Language SDKs** (5): Python Bindings (Python Async Bridge and Callbacks); Rust SDK (Rust Functions and Memo Inputs) | under Architecture Overview |
| Connectors | **Connectors** (13): Local Filesystem; Cloud File Sources (OCI Object Storage); Postgres; SQL and Warehouse Targets (BigQuery and Snowflake Targets); Vector Targets (LanceDB and Zvec Targets); Graph Targets; Streaming Connectors; Valkey Targets; Custom Target Connectors | **Built-in Data Sources** (3): File System and Cloud Storage Sources; Database and Streaming Sources<br>**Storage Backends and Export Targets** (4): Vector Databases; Graph Databases; Relational and Other Targets |
| Built-in operations | **Processing Operations** (7): Text Splitting; Code AST and Source Views; Structural Code Matching; Embedding Models; Model API Operations; Entity Resolution | **Built-in Processing Functions** (4): Text Processing and Chunking; Embedding Functions; Entity Resolution |
| Running and configuring | **Runtime Operations** (5): Command Line Interface; State Inspection; Progress Monitoring; Usage Telemetry | **Configuration and Settings** (4): Authentication and Secrets Management; Multiple Environments and Multi-tenancy; Database Connection and Execution Options<br>**CLI and Development Tools** (7): Command Line Interface; Query Handlers and Search APIs; Development Environment Setup; Agent Tooling and Skills; Benchmarks; Testing Infrastructure |
| Working on the project | **Development** (4): Build and Release; Testing and Benchmarks; Documentation Site | spread over CLI and Development Tools, Overview and Rust Engine Internals |
| Examples | none | **Examples and Use Cases** (8): Text and Code Embedding; PDF and Document Processing; Knowledge Graph and Structured Extraction; Cloud Storage and Streaming Integration; Image Search and Multimodal; Advanced Pipeline Patterns; Rust SDK Examples |
| Reference | **Glossary** (1) | **Glossary** (1) |

How they differ:

- **Organisation.** Ours separates what a pipeline author writes (Pipeline Programming) from what the engine does with it (Incremental Engine), and groups connectors by the external system. DeepWiki follows the layout of the project's own docs site (programming guide, advanced topics, connectors, ops), splits connectors into sources and targets, and adds a section on the example pipelines. Some of its placements are odd: CI/CD Pipeline sits under Rust Engine Internals, Documentation Site under Overview, and Structural Code Analysis under Advanced Topics instead of with the processing functions.
- **Depth.** Both have three levels. We have 7 third-level pages, DeepWiki 2.
- **Section sizes.** Ours run from 3 to 13 pages (Connectors 13, Pipeline Programming 11). DeepWiki's are more even, 3 to 8.
- **Titles.** Ours are short and name one thing (18 characters on average; 13 of 58 join topics with "and" or a comma). DeepWiki's average 27 characters and 30 of 55 join two or three topics, such as "Configuration, Environments, and Internal Storage".
- **Only in DeepWiki.** The eight example pages (it cites 25 of the 39 example folders, we cite 14); Agent Tooling and Skills (we never mention `skills/cocoindex`); a page on multiple environments and multi-tenancy; a page on setting up a development environment.
- **Only in DeepWiki, and not in the code.** Query Handlers and Search APIs documents `QueryOutput`, `QueryInfo` and `QueryHandlerResultFields`; Authentication and Secrets Management documents `AuthRegistry`, `add_auth_entry` and `ref_auth_entry`. None of these names occurs anywhere in the repo at this commit.
- **Only in ours.** Engine pages for target reconciliation, state storage, submit transactions and scheduling; Types and Serialization; State Inspection; Usage Telemetry (the word "telemetry" does not appear in DeepWiki at all); separate pages for Valkey, OCI object storage, BigQuery and Snowflake, LanceDB and Zvec; Model API Operations; Repository Layout. We also go further into the Rust SDK: 36 files under `rust/sdk` cited against 12.

## Blind review of five matched pages

The pairs were chosen by matching titles before reading the pages: the overview, two section main pages, and two topic pages. Both pages of a pair were put in the same citation format, DeepWiki's file list and scraping leftovers were removed, and link targets were blanked in both. Which page was A was balanced (ours was A in two pairs). Each pair went to a separate reviewer that saw only the two files and the repo. Reviewers picked six claims per page to fact-check; the five citations per page were drawn at random by a script.

| Pair (ours / DeepWiki) | Kind | Words | Claims correct | Citations that support their statement | Verdict |
|---|---|---|---|---|---|
| Overview / Overview | Overview | 589 / 924 | 6 of 6 / 4 of 6 | 5 of 5 / 3 of 5 | Ours |
| Pipeline Programming / Core Programming Model | Section main | 892 / 624 | 6 of 6 / 5 of 6 | 5 of 5 / 1 of 5 | Ours |
| Processing Operations / Built-in Processing Functions | Section main | 758 / 715 | 6 of 6 / 4 of 6 | 5 of 5 / 4 of 5 | Ours |
| Custom Target Connectors / same title | Topic | 682 / 868 | 6 of 6 / 5 of 6 | 5 of 5 / 0 of 5 | Ours |
| Command Line Interface / same title | Topic | 637 / 1,010 | 6 of 6 / 4 of 6 | 5 of 5 / 2 of 5 | Ours |
| Total | | | 30 of 30 / 22 of 30 | 25 of 25 / 10 of 25 | Ours 5, DeepWiki 0 |

All 8 DeepWiki claims that failed were marked incorrect, none merely unsupported. Of its 15 citations that fell short, 12 were "partly" (right file, but the lines are imports, a docstring or a different function) and 3 were "no". Reviewers found 3 paths in DeepWiki's prose or diagrams that do not exist (`rust/utils/src/fingerprint/`, `core.py`, a default `cocoindex.db`) and none in ours.

| Average rating (1 to 5) | Ours | DeepWiki |
|---|---|---|
| Accuracy | 4.8 | 2.6 |
| Depth | 4.0 | 2.0 |
| Clarity | 4.0 | 3.0 |
| Useful to a newcomer | 3.6 | 3.0 |
| Useful to a coding agent | 4.0 | 2.0 |

The ratings barely vary between pairs (ours got 4 for depth, clarity and agent use in all five; DeepWiki got 2 for depth and agent use in all five), so read them as "better or worse", not as fine measurements.

## Where ours was better

- **No sampled claim was wrong.** DeepWiki's eight wrong ones include an `app.setup()` method that does not exist, the LMDB store drawn in `rust/core/src/state/` when it is in `rust/core/src/state_store/`, a default database file `cocoindex.db` when the code returns nothing unless `COCOINDEX_DB` is set, and context change detection described as automatic when it is off by default. The first two are the same errors the v3 review found on the same DeepWiki page.
- **Citations land on the code they claim.** DeepWiki cites `update` at `cli.py:321-382`, which is `_load_app`; the command is at 997-1119. On Custom Target Connectors none of its five sampled citations fully supported its statement.
- **Pages explain how things work.** Reviewers described ours as walking a real example through ordered steps and stating rules and failure behaviour, and DeepWiki's as lists of names with diagrams that map phrases to file names.
- **Current API.** Our Custom Target Connectors page describes the present child-handler contract; DeepWiki's diagram shows the deprecated `ChildTargetDef` path.

## Where DeepWiki was better

- **Breadth on the overview.** It lists connectors and target stores, supported Python versions, the build tool and the CLI entry point. Ours has none of these, and both overviews scored 3 for newcomers.
- **Coverage inside a page.** Its CLI page covers `cocoindex init` and gives syntax examples. Ours never mentions `init`, which is a real command (`cli.py:1188-1196`).
- **Easier to read.** Reviewers called our pages dense, heavy on jargon and thick with citations; our Custom Target Connectors page has no worked example, and DeepWiki's has a data-flow diagram and short examples.
- **More diagrams and longer pages.** 2.3 diagrams per page against 1.0, and a median of 754 words against 610.
- **The example pipelines.** Eight pages; we have none.

## The three most useful things to fix in our generator

1. **Make the overview work for a newcomer.** It is the shortest of our five reviewed pages (589 words) and scored 3 for newcomers, level with a DeepWiki page that had two wrong claims. The reviewer's reasons: no install or run commands, no inventory of connectors and operations, and terms such as "tombstone" and "precommit" used without introduction. The overview prompt should ask for what the project is for, how to run it, a table of what ships with it, and plain definitions on first use.
2. **Check each page against the full list of things in its scope, and plan pages for user-facing material.** The CLI page left out one of five commands. The plan has no page for the 39 example folders or for `skills/cocoindex`, both of which DeepWiki covers. A writer could list the public commands, classes or folders in its scope and confirm each is mentioned; the planner could be told that examples and agent skills need a home.
3. **Loosen the page template.** 57 of 58 pages have exactly one diagram, which reads as a quota. Reviewers asked for a worked example on the how-to page, found the citation clusters heavy, and noted one of our diagrams shows `TargetStateProvider` as the caller where the engine drives the steps. Allow a second diagram when a page has both a structure and a flow, require a minimal example on how-to pages, and have the writer check each diagram's arrows against the code as it does for prose.

Two smaller points: two reviewers noted that we cite the project's docs pages for engine behaviour where engine code was available, and our glossary carries no citations.

## Limits

- Five pairs out of 58 pages, with 30 claims and 25 citations sampled per side.
- Reviewers chose which claims to check. Only the citations were drawn at random.
- Blinding hid which page was ours but not that the two came from different tools: DeepWiki's "Sources:" lines and our "Summary" sections remain. Blanking link targets also drew a complaint about placeholder links, mostly against our pages; that is an artefact of the review, not of either wiki.
- The pairs were matched by title, not drawn at random.
- The reviewers were AI models of one family. Five of their findings were spot-checked by hand against the repo and held; the rest were not.
- Diagrams were counted, not rendered, so a diagram that fails to draw is not penalised on either side.
- DeepWiki's pages were scraped; two garbled titles were repaired and stray payload text was removed.
- The v3 and v5 reviews used different pairs and different instructions, so their ratings are not directly comparable.
- Cost and speed are not compared. Our v5 run took 9.5 minutes and about $4.18; DeepWiki's are unknown.
