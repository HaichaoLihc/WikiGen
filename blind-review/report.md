# Blind review: `wiki-7d0f1c.md` vs `wiki-e1c69c.md`

Both wikis document `repos/cocoindex` at commit `f7078f01`. Nothing outside the two wiki files and that repository was read.

## Verdict

**`wiki-7d0f1c.md` is the better wiki overall, and clearly the better one for a coding agent.** Every one of its 1,651 citations resolves to a real file and a valid line range, 29 of 30 sampled citations support their statement, all 36 sampled claims checked out against the code, and none of its 562 distinct code identifiers is missing from the repo. It explains mechanisms (ordering, retries, failure handling, Python and Rust differences) instead of listing parts.

**`wiki-e1c69c.md` cannot be trusted without re-checking.** It documents features that do not exist in this codebase: a whole page on an "auth registry" (`add_auth_entry`, `ref_auth_entry`, `TransientAuthEntryReference`), a whole page on "query handlers" (`QueryOutput`, `QueryInfo`, a "CocoIndex HTTP Server"), an `app.setup()` method and an `app_namespace` setting. 31 of its citations point at missing files or out-of-range lines, only 14 of 30 sampled citations support their statement, and on some pages the line numbers are wrong throughout.

For an engineer new to the project the gap is narrower. `wiki-e1c69c.md` has the onboarding material `wiki-7d0f1c.md` lacks (installation, a first pipeline, a CLI command reference, eight example pages), and those example-driven pages were accurate in the sample. But a newcomer cannot tell its real pages from its invented ones, so I still rank `wiki-7d0f1c.md` first for that reader, with the caveat that it has no getting-started path at all.

| Dimension | `wiki-7d0f1c.md` | `wiki-e1c69c.md` | Better |
|---|---|---|---|
| Accuracy (36 sampled claims each) | 36 correct, 0 incorrect | 31 correct, 5 incorrect | `wiki-7d0f1c.md` |
| Fabricated features found | none | 2 whole pages plus several APIs | `wiki-7d0f1c.md` |
| Citations that resolve (all) | 1,651 of 1,651 | 1,700 of 1,731 | `wiki-7d0f1c.md` |
| Citations that support the statement (30 sampled) | 29 | 14 | `wiki-7d0f1c.md` |
| Identifiers absent from the repo | 0 of 562 | 21 of 884 | `wiki-7d0f1c.md` |
| Contents outline for onboarding | no install, CLI or examples section | has all three | `wiki-e1c69c.md` |
| Contents outline for internals | one page per mechanism | overlapping pages | `wiki-7d0f1c.md` |
| Explanation depth (6 shared topics) | deeper on 6 of 6 | better file-role lists on 1 | `wiki-7d0f1c.md` |
| Diagrams | 57, none flagged | 124, 6 likely fail to parse | mixed |
| Code excerpts verbatim from source | 51 of 54 | 7 of 25 | `wiki-7d0f1c.md` |

## 1. Accuracy

Method: a seeded script drew 9 pages per wiki. On each page the checker took the first specific, checkable claim at or after each quarter of the page (4 per page, 36 per wiki), chosen before verification, and checked it against the implementation, not only against the lines the wiki cites. Per-claim tables are in Appendix A.

| | `wiki-7d0f1c.md` | `wiki-e1c69c.md` |
|---|---|---|
| Sampled pages | Live Component Lifecycle; Live Maps and Change Feeds; Cloud File Sources; PostgreSQL Source and Target; SQLite and Doris Targets; Context, Resources, and Identity; Environment Configuration and Lifecycle; LMDB Transactions and Write Batching; Execution Runners and GPU Pools | Overview; Getting Started; Functions, Memoization, and Change Detection; Memoization Keys and Memo States; Configuration, Environments, and Internal Storage; UpdateHandle and Progress Monitoring; Command Line Interface; Knowledge Graph and Structured Extraction; Cloud Storage and Streaming Integration |
| Correct | 36 | 31 |
| Incorrect | 0 | 5 (2 minor) |
| Unsupported | 0 | 0 |

The five incorrect claims in `wiki-e1c69c.md`:

| Wiki line | Claim | What the code shows |
|---|---|---|
| 175 | `app.setup()` is a key App operation | `python/cocoindex/_internal/app.py:271-386` defines only `update`, `update_blocking`, `drop`, `drop_blocking`. No `setup` exists in the Python SDK. |
| 4446 | `app.drop()` returns a `DropHandle` without blocking | `app.py:372` is `async def drop(self) -> None`; it awaits completion and returns nothing. |
| 2691 | `context_initial_states` is read on a cache miss "to verify if cached results are still valid" | `rust/core/src/engine/environment.rs:23-25`: it is read on a cache miss to populate a new memo entry's `context_memo_states`. It verifies nothing. |
| 4472 | `num_adds` counts "items resulting in new target state creation" | `rust/core/src/engine/component.rs:1405-1411`: it counts component runs with no previous state, not target states (minor). |
| 2447 | `fingerprint_call(obj)` | `python/cocoindex/_internal/memo_fingerprint.py:432-440`: the signature is `fingerprint_call(func, args, kwargs, state_methods, ...)`; the one-object function is `memo_fingerprint(obj)` (minor). |

The random draw missed the worst pages of `wiki-e1c69c.md`, so 31 of 36 overstates it. Errors I found outside the sample, each confirmed by search over the repo:

| Where in `wiki-e1c69c.md` | Problem | Evidence |
|---|---|---|
| Page at line 4779 (auth and secrets) | Entire page describes an auth registry: `add_auth_entry`, `ref_auth_entry`, `AuthEntryReference`, `TransientAuthEntryReference` | Zero hits for `auth_entry`, `AuthRegistry` or `AuthEntryReference` anywhere in the repo. Its citations point at real files that contain none of this (`python/cocoindex/_internal/api.py:79-108` is a block of imports). |
| "Query Handlers and Search APIs" (line 5403) | `QueryOutput`, `QueryInfo`, `QueryHandlerResultFields`, `cocoindex.cli:run_cli`, a "CocoIndex HTTP Server" | Zero hits for `QueryOutput`, `QueryInfo`, `QueryHandler`, `query_handler` or `run_cli`. The table cites `app.py:184-214`, which is the `App` class header. |
| "Setup, Drop, and Resource Lifecycle" (line 4581) | Introduced as explaining `app.setup()` and `app.drop()` | No `setup` method exists. The drop half is sound: `App::drop_app` is at `rust/core/src/engine/app.rs:206`. |
| "Multiple Environments and Multi-tenancy" (line 4904) | `app_namespace` in `AppConfig` for logical isolation | Zero hits for `app_namespace`. |
| "Custom Target Connectors" (line 2169) | `register_root_target_states_provider` at `python/cocoindex/connectorkits/target.py:14`; examples `PgTableTarget`, `LocalFile`; `_TableKey` field `schema_name` | That file contains only the `ManagedBy` enum; the function is at `python/cocoindex/_internal/target_state.py:659`. `PgTableTarget` does not exist. The real field is `pg_schema_name` (`connectors/postgres/_target.py:1074`). |
| Same page, diagram at 2301 | A handler "returns ChildTargetDef" | `ChildTargetDef` belongs to the deprecated sink contract (`target_state.py:141`, `:250`), not to handlers. |
| "Exception Handling and Concurrency" (line 2499) | Global `inflight_semaphore` in `AppContext` | `AppContext` uses an `AdmissionPool` (`rust/core/src/engine/admission.rs:36`). `_inflight_semaphore` exists only in `python/cocoindex/ops/litellm.py:392`. |
| "Rust SDK Examples" (line 7276) | `cargo run -p code_embedding --features fastembed` | `examples/rust/code_embedding/Cargo.toml` has no `[features]` section. |
| Line 5240 | Default DB path is "typically `cocoindex.db`" | `python/cocoindex/_internal/setting.py:12-20` returns the `COCOINDEX_DB` value or `None`. |

For `wiki-7d0f1c.md` I checked 13 further claims myself on pages outside its sample and found no error. Examples: the 30-second live drain timeout (`rust/core/src/engine/live_component.rs:31`), entity-resolution retries of two in Python and five in Rust (`llm_resolver.py:72`, `rust/sdk/cocoindex/src/ops/api.rs:460`), `min_chunk_size` defaulting to half the target with overlap capped at it (`rust/ops_text/src/split/recursive.rs:642-643`), `recollect_after_run` rejected for memoized components (`function.py:1019-1023`), the release job graph (`.github/workflows/release.yml:45-242`). The only blemishes the checker noted were loose phrasings, such as "a synchronous or asynchronous `RowFetcher`" for a single object that supports both.

## 2. Citations

**All citations (script over the whole file).**

| | `wiki-7d0f1c.md` | `wiki-e1c69c.md` |
|---|---|---|
| Citations in `[path:START-END]` form | 1,651 | 1,731 |
| File missing | 0 | 29 |
| Line range outside the file | 0 | 2 |
| Distinct files cited | 266 | 261 |
| Median range length (lines) | 17 | 13 |
| 90th percentile range length | 39 | 71 |
| Longest range | 102 | 1,064 |
| Ranges over 100 lines | 1 | 111 |
| Ranges covering a whole file of more than 30 lines | 0 | 37 |
| Citations into `docs/` (prose, not code) | 93 | 207 |
| Citations per 1,000 words | 47 | 42 |

The 29 missing-file citations in `wiki-e1c69c.md` are path errors concentrated on two pages: `rust/state/db_schema.rs` (17 times; the real path is `rust/core/src/state/db_schema.rs`), `rust/state_store/{storage,app_store,submit_session}.rs`, `python/python/cocoindex/_internal/environment.py`, `cocoindex/ops/text.py`, `examples/image_search/main.py` and `rust/sdk/cocoindex/src/lancedb.rs`. The two bad ranges run one line past the end of the file.

**Sample of 30 per wiki (seeded script; a checker read the wiki context and the cited lines).** Per-citation tables are in Appendix B.

| Verdict | `wiki-7d0f1c.md` | `wiki-e1c69c.md` |
|---|---|---|
| Supports the statement | 29 | 14 |
| Partial (right area, evidence incomplete or range too broad) | 1 | 11 |
| Does not support | 0 | 3 |
| Missing file | 0 | 2 |

Patterns in `wiki-e1c69c.md`: module docstrings, import lines and test call sites cited as evidence for behaviour implemented elsewhere; 91 to 145 line ranges used as pointers; trailing "source lists" after diagrams that have nothing to do with the diagram (line 1574 cites `rust/core/src/engine/context.rs:37-93` under a progress-monitoring diagram; those lines are `AppContext` fields).

Some pages of `wiki-e1c69c.md` have line numbers that are wrong almost everywhere while the files are right. On "Custom Target Connectors" I checked seven by hand and all seven miss: `TargetHandler` is cited at `target_state.py:197-205` and is at line 526; `TargetReconcileOutput` at `188-195`, actually 508; the sink code at `connectors/postgres/_target.py:355-370`, which is `TableSchema.__init__`; the fingerprint check at `connectors/lancedb/_target.py:421-424`, which is a constructor; `attachments` at `rust/py/src/target_state.rs:167-184`, actually 550. The CLI page cites `ls` at `cli.py:168-183`, `update` at `321-382` and `drop` at `384-428`; they are at 562, 997 and 1122. For a coding agent these are worse than a missing citation, because they pass an existence check.

**Do the cited lines mention what the sentence names? (crude script check, whole file).** For each run of citations, I took the backticked identifiers in the text the run is attached to and tested whether they occur in the cited lines.

| | `wiki-7d0f1c.md` | `wiki-e1c69c.md` |
|---|---|---|
| Named identifiers found in the cited lines, single citation | 109 of 122 (89%) | 1,058 of 1,568 (67%) |
| Same, runs of two or more citations (union of ranges) | 781 of 883 (88%) | 66 of 92 (72%) |

**Placement.** `wiki-e1c69c.md` attaches most citations to a single bullet or sentence (953 of 1,251 citation runs hold one citation). `wiki-7d0f1c.md` stacks them at paragraph ends (542 of 686 runs hold two or more, mean 2.4), so the reader must work out which citation backs which clause. In the sample every stacked citation did match an identifiable clause.

## 3. Names and paths

Checked by script: every inline code span outside fenced blocks (citations removed), classified as path-like or identifier-like. Identifiers pass if every dotted component occurs as a whole identifier somewhere in the repo's text files (`graphify-out/`, `.git`, lock files excluded). Paths pass on exact match, or as a suffix of a real path. I also scanned the whole file, diagrams included, for strings shaped like source file paths. Each flagged item was then reviewed by hand.

| | `wiki-7d0f1c.md` | `wiki-e1c69c.md` |
|---|---|---|
| Inline code spans (total / distinct) | 1,219 / 772 | 2,395 / 1,296 |
| Distinct identifier-like spans | 562 | 884 |
| Flagged as absent from the repo | 0 | 25 |
| Absent after review | 0 | 21 |
| Distinct path-like spans | 35 | 145 |
| Exact path match | 16 | 93 |
| Suffix or basename match | 7 | 25 |
| Unmatched, and a wrong repo path after review | 0 of 12 | 1 of 27 |
| Source-file paths anywhere in the file that do not exist | 0 of 12 | 6 of 113 |

The 21 absent identifiers in `wiki-e1c69c.md`: `AmazonS3`, `GoogleDrive`, `OCIObjectStorage`, `KafkaSource`, `amazon_s3.S3Source`, `AuthRegistry`, `add_auth_entry`, `ref_auth_entry`, `TransientAuthEntryReference`, `QueryOutput`, `QueryInfo`, `QueryHandlerResultFields`, `app_namespace`, `PgTableTarget`, `TurbopufferCollectionTarget`, `inflight_semaphore`, `commit_effects()`, `declare_dir`, `bench_metrics`, `engine_stats`, `total_duration_ms`. The other four flags were two diagram node names and two shortened example names. The script misses invented names whose parts exist separately; by reading I also found `app.setup()`, `PyAppOpHandle`, `cocoindex.cli:run_cli` and `core::_core`.

The unmatched path-like spans are mostly not repo paths (URL routes, MIME types, GitHub action names, model IDs, build outputs). Wrong repo paths in `wiki-e1c69c.md`: `python/cocoindex/app.py`, `python/cocoindex/connectorkits/statediff/__init__.py` (it is `statediff.py`), `rust/sdk/cocoindex/src/lancedb.rs`, and `rust/state_store/{app_store,storage,txn}.rs`.

**Commands.** I extracted command-like spans and shell blocks and checked them against `python/cocoindex/cli.py`, `.pre-commit-config.yaml`, `pyproject.toml`, the `Cargo.toml` files and `dev/`.

| | `wiki-7d0f1c.md` | `wiki-e1c69c.md` |
|---|---|---|
| Command-like spans and shell lines found | 28 | about 75 |
| CLI subcommands and flags | `cocoindex update main`, `-L`, `--full-reprocess`, `--preview`, `--reset`, `--force`: all exist | `init`, `ls`, `show --tree`, `update`, `drop -f`, `path:App@env`: all exist |
| Hook IDs named | all exist | all exist |
| Wrong | none found | `cargo run -p code_embedding --features fastembed` |
| Not checked | `npm --prefix docs ci`, `cargo update --workspace` | `python benchmark.py ...`, `cargo run --release -- --scenario ...`, the `uv pip install` lines |

## 4. Table of contents

| | `wiki-7d0f1c.md` | `wiki-e1c69c.md` |
|---|---|---|
| Pages | 58 | 55 |
| Top-level sections | 9 | 12 |
| Pages at depth 1 / depth 2 | 38 / 11 | 41 / 2 |
| Organising idea | by mechanism: architecture, execution, reconciliation, connectors, transformations, runtime, development | product-docs shape: overview, architecture, programming model, advanced, sources, functions, targets, state, configuration, tools, examples |
| Largest section | Source and Target Connectors: 14 pages, 6,807 words | Examples and Use Cases: 8 pages, 6,280 words |
| Smallest non-trivial section | System Architecture: 4 pages, 2,342 words | Configuration and Settings: 3 pages, 1,552 words |
| Page headings that differ from the outline | 0 | 2 ("PyO3 Integration and Establish System"; "Authentication andrypted Secrets Management") |

`wiki-7d0f1c.md` gives each mechanism one page, with titles that say what is inside ("Ownership, Submission, and Cleanup", "LMDB Transactions and Write Batching", "Deadlines, Cancellation, and Failures"). Connectors are grouped by kind and split to pairs at depth 2, so a reader looking for Doris or zvec finds a title. Two section names are vague ("Transformation and Intelligence", "Runtime and Shared Mechanisms"), and there is no entry point for someone who wants to install and run something.

`wiki-e1c69c.md` is easier to enter (Getting Started, a CLI page, eight example pages) but scatters topics. Memoization is split across "Functions, Memoization, and Change Detection" and "Memoization Keys and Memo States". Storage and environments are spread across "Configuration, Environments, and Internal Storage", "Incremental Processing and State Management", "Database Connection and Execution Options" and "Multiple Environments and Multi-tenancy". Twenty connectors are squeezed into five pages, and two outline entries lead to pages about things that do not exist.

| Part of the codebase | `wiki-7d0f1c.md` | `wiki-e1c69c.md` |
|---|---|---|
| Installation and first pipeline | missing (`pip install` appears 0 times) | "Getting Started" |
| CLI command reference (`ls`, `show`, `init`) | missing; only update flags, drop and the app specifier | "Command Line Interface" (line numbers stale) |
| Example apps (40 in `examples/`) | one page; 15 examples cited | eight pages; 25 examples cited |
| Agent skills (`skills/`) | missing (0 mentions) | "Agent Tooling and Skills" |
| CI workflows | folded into development pages | "CI/CD Pipeline" |
| `rust/py_utils` crate | missing (0 mentions) | covered (18 mentions) |
| Rust SDK (`rust/sdk`) | 180 citations, Rust notes on most pages | 34 citations, two pages |
| Submission protocol (precommit, apply, commit, ownership) | own page ("precommit" 31 times) | a paragraph ("precommit" 4 times) |
| Deadlines, cancellation, failure handling | own page | scattered |
| Telemetry | covered | missing (0 mentions) |
| User state (`use_state`), `auto_refresh` | covered | 1 mention, 0 mentions |
| Schema evolution and state diffs | own page | one paragraph |
| Python connectors with source citations (20 exist) | 20 | 18 (no `azure_blob`, no `zvec`) |
| Warehouse targets (BigQuery, Snowflake) | own page | rows in a table |

## 5. Explanation quality

I read six topics that both wikis cover, side by side.

| Topic | `wiki-7d0f1c.md` | `wiki-e1c69c.md` | Better |
|---|---|---|---|
| Memoization | Separates component-level and function-level reuse, what a hit requires (processor fingerprint, logic dependencies, provider generations), why a hit still retains target declarations, and what concurrent callers do. Cites engine code. | Paraphrases the user guide (most citations go to `docs/.../function.mdx`) and tests. The decision diagram is generic. Mixes in batching and GPU runners. | `wiki-7d0f1c.md` |
| Custom target connectors | States the contract and why: `reconcile()` runs in precommit and can be retried, so it must be free of side effects; sinks must be idempotent because a failed batch is split and retried. Marks the old child-slot contract as deprecated. | Readable walkthrough with a key-types table, but wrong line numbers throughout, invented class names, and a diagram that presents the deprecated contract as current. Says previous records come from "successful runs"; the engine keeps several because runs can be interrupted. | `wiki-7d0f1c.md` |
| Live components | Covers readiness in catch-up and live mode, serialisation of full passes, coalescing of queued keyed updates, the drain timeout on remount, and why mount calls are banned inside `process_live`. | Correct names and a usable protocol table, but stops at what each method is for. Two box diagrams with "calls", "triggers", "manages" arrows. | `wiki-7d0f1c.md` |
| Entity resolution | Gives the algorithm: partition by similarity threshold, greedy per-component resolution in sorted order, the FAISS boundary detail, policy effects, event ordering, differing retry defaults. | Lists classes and methods with one line each; accurate, with a benchmark note the other lacks. | `wiki-7d0f1c.md` |
| Persistent state | Names each record kind and its purpose, explains `use_state` lifetime rules and why it is rejected inside memoized functions. | The parent page cites files that do not exist on almost every line, and labels diagram nodes with bare "line 107" references. | `wiki-7d0f1c.md` |
| Text splitting | Explains how the recursive planner chooses boundaries, that `chunk_size` is a target and not a guarantee, how overlap is capped, byte versus character positions. | Less depth, but a useful "Key Files and Roles" list mapping five files to their job. One muddled sentence equates `PyChunk` with `PyCodeMatch`. | `wiki-7d0f1c.md` for depth; `wiki-e1c69c.md` for the file map |

`wiki-7d0f1c.md` routinely says why something is so and what happens on failure. `wiki-e1c69c.md` mostly says what exists and where; on core topics its "how" is taken from the project's own user docs, not from the implementation. It has seventeen "Purpose and Scope" sections that mostly restate the page title.

## 6. Form

| | `wiki-7d0f1c.md` | `wiki-e1c69c.md` |
|---|---|---|
| Words | 34,796 | 41,186 |
| Words per page (10th pct / median / 90th pct / max) | 440 / 564 / 741 / 2,726 | 616 / 747 / 915 / 1,125 |
| Headings (h2 / h3) | 193 / 0 | 294 / 301 |
| Bullet and numbered list items | 258 | 821 |
| Tables | 60 | 54 |
| Mermaid diagrams | 57 | 124 |
| Diagram types | flowchart 39, sequence 16, state 2 | graph/flowchart 112, sequence 10, class 2 |
| Pages without a diagram | 1 (Glossary) | 0 |
| Median diagram size (lines) | 8 | 19 |
| Diagrams flagged by static lint | 0 | 7 (6 likely parse failures, 1 possible) |
| Code blocks (non-Mermaid) | 55 | 39 |
| Code excerpts with at least 90% of lines found verbatim in the repo | 51 of 54 | 7 of 25 |

**Diagrams.** I did not render them; a script checked diagram type, block balance, quoting and unquoted special characters. In `wiki-e1c69c.md`, four diagrams (lines 400, 439, 474, 521) put a bare `title "..."` line before `graph TD`, which is not a diagram type, and two (lines 3898, 3969) use doubled quotes such as `UserRow[""User Dataclass Row""]`; I expect all six to fail. One edge label has unquoted parentheses (line 4976).

Arrow accuracy, checked by hand or by the claim checkers: for `wiki-7d0f1c.md`, seven diagrams checked and all match the code (handler, child-factory and sink ordering against `execution.rs:752-776`; precommit, apply, commit; GPU acquire and release; lazy environment states; the OCI live sequence; the entity-resolution flow; the release job graph). They are small and usually show only the default path. For `wiki-e1c69c.md`, of seven checked, three match (function decoration to the logic registry; the live feed flow; the update and drop flow, where `App::drop_app` exists at `rust/core/src/engine/app.rs:206`) and four do not: the query invocation diagram is fictional, the hierarchical target diagram shows the deprecated contract, the storage diagram shows fields `StorageInner` does not have, and the memo-state sequence names the wrong caller. Many of its diagrams use the same "Natural Language Space" and "Code Entity Space" template (36 and 56 occurrences) with arrows that carry little information.

**Code excerpts.** `wiki-7d0f1c.md` quotes real code and cites the exact lines (the other three excerpts are 80 to 86% verbatim). `wiki-e1c69c.md` often shows composed or simplified code followed by a citation, which reads as a quotation but is not; for example the sink example at line 2267 is cited to `postgres/_target.py:355-370`, which contains nothing like it.

**Readability.** `wiki-7d0f1c.md` is dense: long paragraphs packed with qualifications, no sub-headings below h2, every page close to the same length with exactly one diagram whatever the size of the subject. It reads as reference, not tutorial. Its glossary is 2,726 words with no citations. `wiki-e1c69c.md` is easier to skim, with more headings, bullets and tables, but carries boilerplate, a stray LaTeX `$\Delta$`, and two garbled page headings.

## Strengths and weaknesses

### `wiki-7d0f1c.md`

Strengths:

1. **Accurate.** 36 of 36 sampled claims correct, 13 further claims I checked correct, 0 of 562 identifiers missing, quoted code verbatim.
2. **Citations that work as evidence.** 1,651 of 1,651 resolve; 29 of 30 sampled support the statement; ranges are tight (median 17 lines, longest 102).
3. **Explains mechanisms and reasons.** Failure handling, retries, concurrency and Python versus Rust differences are stated on most pages, for example why `run_txn` takes `Fn` (the runner may call a body again after a map resize, `storage.rs:128-133`).

Weaknesses:

1. **No onboarding or reference surface.** No installation, no first pipeline, no `cocoindex init`, `ls` or `show`; one page for 40 examples; nothing on `skills/` or `rust/py_utils`.
2. **Dense, with stacked citations.** 79% of citation runs hold two or more citations, so claim-to-line mapping is left to the reader; one sampled citation (line 148) was only a loose pointer for a summary sentence.
3. **Uniform, flat pages.** Every page is 440 to 740 words with one small diagram and no sub-headings, so a 1,500-line connector gets the same space as a small helper; two section names are vague; the glossary is long and uncited.

### `wiki-e1c69c.md`

Strengths:

1. **Covers what a newcomer needs first.** Getting Started, a CLI command page, CI/CD, agent skills, benchmarks, testing, and eight example pages citing 25 of 40 examples.
2. **Example-driven pages are accurate.** The 12 sampled claims on Getting Started, Knowledge Graph and Cloud Storage and Streaming were all correct, and some citations hit the exact line (`environment.rs:18`, `stats.rs:51`).
3. **Navigation aids.** Concept-to-file tables, "Key Files and Roles" lists, and citations attached to individual bullets (76% of runs hold one citation).

Weaknesses:

1. **Documents things that do not exist.** Two full pages (auth registry, query handlers), `app.setup()`, `app_namespace`, 21 absent identifiers, six wrong source paths.
2. **Unreliable citations.** 31 broken; 111 ranges over 100 lines; 37 whole-file ranges; 14 of 30 sampled support the statement; line numbers wrong throughout "Custom Target Connectors" and the CLI page.
3. **Shallow on internals, and rough in form.** Core pages paraphrase the user docs (207 citations into `docs/`); 18 of 25 code excerpts are not verbatim; six diagrams likely fail to parse; four of seven checked diagrams do not match the code; overlapping pages and two garbled headings.

## Limits of this review

- **Sample size.** 36 claims from 9 pages and 30 citations per wiki. The perfect claim score for `wiki-7d0f1c.md` shows a low error rate, not zero errors across 58 pages. The draws differed in difficulty: engine-heavy pages for `wiki-7d0f1c.md`, more overview and example pages for `wiki-e1c69c.md`.
- **Who checked.** The four sampled checks were done by subagents given only the wiki and the repo. I re-verified about ten of their verdicts against the code and all agreed, but I did not re-verify every row.
- **Fabrications were found by reading, not by sampling,** so I cannot give a rate for them, and there may be more in pages I did not read in full. I read seven to ten pages of each wiki closely and covered the rest only by script and by the sampled checks.
- **Diagrams were not rendered.** "Likely fails to parse" is a judgement from static inspection. Arrow accuracy was checked for seven diagrams per wiki, not all 181.
- **The identifier check tests existence only,** not correct use, and misses invented names assembled from real parts. The identifier-in-cited-lines measure is crude; an earlier variant that credited a paragraph's last sentence to each stacked citation separately gave the opposite ordering (59% against 78%), which is why I report the per-unit version and rely mainly on the hand-checked sample.
- **No commands were run.** Commands were checked against configuration and source only; a few are listed as unchecked.
- **Blindness.** I read only the two wiki files and `repos/cocoindex` (excluding `graphify-out/`). I did not read the shared notes folder, because sibling notes could reveal where the wikis came from.

## Appendix A: sampled claims

### `wiki-7d0f1c.md` (36 correct)

| # | Page | Wiki line | Claim | Verdict | Evidence |
|---|---|---|---|---|---|
| 1 | Live Component Lifecycle | 843 | In catch-up `mark_ready()` ends the live task; in live mode it only releases readiness | correct | `rust/core/src/engine/live_component.rs:819-838` |
| 2 | Live Component Lifecycle | 859 | `mark_ready()` is idempotent and suspends in catch-up | correct | `live_component.rs:822-824` |
| 3 | Live Component Lifecycle | 872 | A full pass serialises with other full passes and gates queued keyed operations | correct | `live_component.rs:582`, `:599`, `:1127` |
| 4 | Live Component Lifecycle | 888 | `auto_refresh` loop: full pass, ready, sleep, full pass | correct | `python/cocoindex/_internal/live_component.py:669-674`, verbatim |
| 5 | Live Maps and Change Feeds | 908 | `LiveMapFeed` delivers changes; `LiveMapView` adds a scan | correct | `live_component.py:471-495` |
| 6 | Live Maps and Change Feeds | 920 | `mount_each` builds an internal live component; subscriber maps keys to subpaths | correct | `api.py:497-504`; `live_component.py:519-539` |
| 7 | Live Maps and Change Feeds | 936 | Entries reach the map through reconciliation; removal follows ownership cleanup | correct | `resources/live_map.py:117-138`, `:168-187` |
| 8 | Live Maps and Change Feeds | 951 | `create()` mounts a container; `declare_entry()` declares a child state | correct | `live_map.py:276-282` |
| 9 | Cloud File Sources | 1412 | Object-store walkers use prefix-relative paths; OCI can add an event stream | correct | `amazon_s3/_source.py:309-314`; `oci_object_storage/_source.py:361-362` |
| 10 | Cloud File Sources | 1425 | Drive keys come from `info.name` with no parent folders | correct | `google_drive/_source.py:95`, `:218-231` |
| 11 | Cloud File Sources | 1441 | Drive example mounts `process_file` over `source.items()` | correct | `examples/gdrive_text_embedding/main.py:116-121` |
| 12 | Cloud File Sources | 1455 | `_LiveOCIItems`: watch, then `update_all()`, then `mark_ready()` | correct | `oci_object_storage/_source.py:425-429` |
| 13 | PostgreSQL Source and Target | 1533 | `fetch_rows()` reads in a read-only repeatable-read transaction | correct | `postgres/_source.py:111-137`, `:241-253` |
| 14 | PostgreSQL Source and Target | 1544 | Example mounts over `fetch_rows().items(lambda ...)` | correct | `examples/postgres_source/main.py:113-123` |
| 15 | PostgreSQL Source and Target | 1553 | Rust `read_table` fetches into a `Vec` | correct | `rust/sdk/cocoindex/src/connectors/postgres.rs:1937` |
| 16 | PostgreSQL Source and Target | 1568 | Row handler fingerprints values and skips unchanged rows | correct | `postgres/_target.py:1056-1061` |
| 17 | SQLite and Doris Targets | 1584 | SQLite uses a local transaction; Doris deletes before loading | correct | `sqlite/_target.py:467`; `doris/_target.py:883` |
| 18 | SQLite and Doris Targets | 1597 | Both row handlers fingerprint, skip unchanged, emit deletes | correct | `sqlite/_target.py:558-590`; `doris/_target.py:913-940` |
| 19 | SQLite and Doris Targets | 1612 | `Vec0TableDef`, `VectorIndexDef`, `InvertedIndexDef` roles | correct | `sqlite/_target.py:136-137`; `doris/_target.py:717-735` |
| 20 | SQLite and Doris Targets | 1627 | Doris test declares an HNSW `VectorIndexDef` | correct | `python/tests/connectors/test_doris_target.py:426-439` |
| 21 | Context, Resources, and Identity | 2622 | Python uses a `ContextVar`; Rust passes `Ctx` explicitly | correct | `component_ctx.py:45`; `rust/sdk/cocoindex/src/ctx.rs` |
| 22 | Context, Resources, and Identity | 2633 | Lifespan test sets `db_path` and calls `provide_async_with` | correct | `python/tests/core/test_default_env_async.py:33-39` |
| 23 | Context, Resources, and Identity | 2646 | Change detection is opt-in and fingerprints key name and value | correct | `context_keys.py:103`, `:181-186` |
| 24 | Context, Resources, and Identity | 2661 | `ComponentContext` fields and exit behaviour | correct | `component_ctx.py:76-79`, `:366-371` |
| 25 | Environment Configuration and Lifecycle | 2738 | Apps use a lazily started default environment | correct | `app.py:180`; `environment.py:492` |
| 26 | Environment Configuration and Lifecycle | 2752 | `Settings.from_env()` reads the LMDB variables | correct | `setting.py:121-142` |
| 27 | Environment Configuration and Lifecycle | 2773 | Lazy environment starts, stops, and can start again | correct | `environment.py:380-489` |
| 28 | Environment Configuration and Lifecycle | 2782 | Pass `Environment(Settings(...))` through `AppConfig` | correct | `environment.py:238-249`; `app.py:177-181` |
| 29 | LMDB Transactions and Write Batching | 2860 | Each `Storage` owns a batcher that coalesces transaction bodies | correct | `rust/core/src/state_store/storage.rs:120-123`, `:495` |
| 30 | LMDB Transactions and Write Batching | 2879 | The `run_txn` closure is `Fn` because it may run more than once | correct | `storage.rs:128-133`, `:473-480` |
| 31 | LMDB Transactions and Write Batching | 2887 | On map-full the runner retries after doubling the map size | correct | `storage.rs:246-254`, `:283-288` |
| 32 | LMDB Transactions and Write Batching | 2898 | Order: precommit, sink apply, commit | correct | `rust/core/src/engine/execution.rs:1780`, `:1919`, `:1948` |
| 33 | Execution Runners and GPU Pools | 3042 | GPU work runs in-process by default | correct | `runner.py:326-341` |
| 34 | Execution Runners and GPU Pools | 3058 | Test gathers two `_gpu_work` calls | correct | `python/tests/core/test_gpu_pool.py:132-141` |
| 35 | Execution Runners and GPU Pools | 3076 | Acquire returns a GPU id; runner releases it with the fraction | correct | `runner.py:343-355`; `rust/utils/src/gpu_pool.rs:121`, `:243` |
| 36 | Execution Runners and GPU Pools | 3097 | Outside a GPU context the accessors return `None`, `[]`, `None` | correct | `runner.py:219-238` |

### `wiki-e1c69c.md` (31 correct, 5 incorrect)

| # | Page | Wiki line | Claim | Verdict | Evidence |
|---|---|---|---|---|---|
| 1 | Overview | 91 | LMDB-backed fingerprinting | correct | `rust/core/Cargo.toml:14` |
| 2 | Overview | 107 | `App` lives in `_internal/app.py` | correct | `app.py:184` |
| 3 | Overview | 140 | `coco.App`, `@coco.fn`, `coco.mount()` are exported | correct | `api.py:897-999` |
| 4 | Overview | 175 | Key operations include `app.setup()` | **incorrect** | no `setup` in `app.py:271-386` |
| 5 | Getting Started | 223 | Rust core with a PyO3 layer | correct | `pyproject.toml:59-65` |
| 6 | Getting Started | 261 | Walkthrough converts PDFs to Markdown with Docling | correct | `docs/.../quickstart.mdx:14-24` |
| 7 | Getting Started | 302 | Quoted converter setup code | correct | `quickstart.mdx:89-96` |
| 8 | Getting Started | 349 | Unchanged files are skipped | correct | `quickstart.mdx:111` |
| 9 | Functions, Memoization | 1589 | `@coco.fn` yields `SyncFunction` or `AsyncFunction` | correct | `function.py:681`, `:1232` |
| 10 | Functions, Memoization | 1603 | Sync or async nature is preserved | correct | `function.py:1981-1984` |
| 11 | Functions, Memoization | 1629 | A hit returns the stored value and carries target states | correct | `function.py:883-896` |
| 12 | Functions, Memoization | 1655 | `GPURunner (fraction=1.0)` | correct | `runner.py:313`, `:396` |
| 13 | Memoization Keys | 2369 | Default canonicalisation of containers and models | correct | `memo_fingerprint.py:347-373` |
| 14 | Memoization Keys | 2390 | `__coco_memo_state__` signature | correct | `typing.py:71-78` |
| 15 | Memoization Keys | 2415 | `_canonicalize()` and a pickle fallback | correct | `memo_fingerprint.py:283`, `:377` |
| 16 | Memoization Keys | 2447 | `fingerprint_call(obj)` | **incorrect** (minor) | `memo_fingerprint.py:432-440` |
| 17 | Configuration | 2605 | Settings passed at init or via `from_env()` | correct | `environment.py:121`, `:238-240` |
| 18 | Configuration | 2627 | `Storage` at `storage.rs:118` | correct | `storage.rs:116-118` |
| 19 | Configuration | 2659 | Environment holds a `Storage` | correct | `environment.rs:18` |
| 20 | Configuration | 2691 | `context_initial_states` verifies cached results | **incorrect** | `environment.rs:23-25` |
| 21 | UpdateHandle | 4446 | `app.drop()` returns a `DropHandle` | **incorrect** | `app.py:372-384` |
| 22 | UpdateHandle | 4472 | `num_adds` counts new target states | **incorrect** (minor) | `component.rs:1405-1411` |
| 23 | UpdateHandle | 4516 | `ProcessingStats` at `stats.rs:51` | correct | `stats.rs:51` |
| 24 | UpdateHandle | 4545 | Progress display captures output to a PTY | correct | `progress_display.rs:280-291` |
| 25 | Command Line Interface | 5199 | CLI built with `click` | correct | `cli.py:8` |
| 26 | Command Line Interface | 5249 | `ls` groups apps by environment | correct | `cli.py:227-272` |
| 27 | Command Line Interface | 5300 | `drop` clears state and reverts targets | correct | `cli.py:1140-1177` |
| 28 | Command Line Interface | 5350 | `load_user_app()` imports the module | correct | `user_app_loader.py:49`, `:104` |
| 29 | Knowledge Graph | 6544 | Extraction with instructor, DSPy or BAML | correct | example directories |
| 30 | Knowledge Graph | 6578 | `resolve_entities` output feeds SurrealDB | correct | `examples/conversation_to_knowledge/conv_knowledge/app.py:52`, `:263-288` |
| 31 | Knowledge Graph | 6614 | Phase 1 declares primary nodes and collects triples | correct | `examples/docs_to_knowledge_graph/main.py:219-233` |
| 32 | Knowledge Graph | 6652 | `extract_file_info` maps a file to `CodebaseInfo` | correct | `examples/multi_codebase_summarization/main.py:38-39` |
| 33 | Cloud Storage and Streaming | 6695 | Cloud connectors expose `FileLike` | correct | `amazon_s3/_source.py:103` |
| 34 | Cloud Storage and Streaming | 6733 | `topic_as_map()` gives a live keyed map | correct | `kafka/_source.py:484-511` |
| 35 | Cloud Storage and Streaming | 6770 | `_MessageHandler._apply_actions` | correct | `kafka/_target.py:63-137` |
| 36 | Cloud Storage and Streaming | 6812 | `LiveComponent` protocol methods | correct | `live_component.py:203-207` |

## Appendix B: sampled citations

### `wiki-7d0f1c.md` (29 supports, 1 partial)

| # | Wiki line | Citation | Verdict | Note |
|---|---|---|---|---|
| 1 | 72 | `rust/core/src/engine/environment.rs:17-28` | supports | environment fields |
| 2 | 148 | `rust/core/src/state_store/submit_session.rs:36-60` | partial | illustrative pointer for a summary sentence |
| 3 | 364 | `rust/py/src/component.rs:86-97` | supports | processor trait impl |
| 4 | 518 | `python/cocoindex/_internal/live_component.py:562-612` | supports | `_MountEachLiveComponent` |
| 5 | 534 | `python/cocoindex/_internal/app.py:214-246` | supports | `App.__init__` |
| 6 | 588 | `rust/core/src/engine/app.rs:250-273` | supports | drain, delete root, drop store |
| 7 | 629 | `rust/core/src/state/stable_path.rs:5-16` | supports | `StableKey` enum |
| 8 | 721 | `rust/core/src/engine/component.rs:650-700` | supports | `lookup_component_memo` |
| 9 | 902 | `python/cocoindex/_internal/live_component.py:119-134` | supports | operator detach |
| 10 | 990 | `python/cocoindex/_internal/target_state.py:508-554` | supports | handler protocol |
| 11 | 1047 | `python/cocoindex/connectors/localfs/_target.py:267-273` | supports | root provider registration |
| 12 | 1207 | `docs/.../custom_target_connector.mdx:437-439` | supports | factory is sync and pure |
| 13 | 1275 | `rust/sdk/cocoindex/src/statediff.rs:126-139` | supports | composite tracking record |
| 14 | 1343 | `rust/sdk/cocoindex/src/connectors/kafka.rs:506-514` | supports | scan and watch |
| 15 | 1519 | `python/cocoindex/connectors/postgres/_target.py:1547-1559` | supports | SQL command attachment |
| 16 | 1697 | `python/cocoindex/connectors/bigquery/_target.py:431-460` | supports | query parameters |
| 17 | 1803 | `python/cocoindex/connectors/zvec/_target.py:833-844` | supports | rebuild on schema change |
| 18 | 1992 | `python/cocoindex/connectors/surrealdb/_target.py:1469-1485` | supports | derived edge id |
| 19 | 2286 | `rust/code_match/README.md:3-5` | supports | by-example patterns |
| 20 | 2428 | `rust/sdk/cocoindex/src/ops/api.rs:225-255` | supports | one of three clients |
| 21 | 2557 | `rust/sdk/cocoindex/src/app.rs:537-589` | supports | update with options |
| 22 | 2612 | `rust/core/src/state/db_schema.rs:270-291` | supports | component memo record |
| 23 | 2732 | `rust/core/src/engine/id_sequencer.rs:68-75` | supports | two-layer locking |
| 24 | 2798 | `rust/core/src/state/db_schema.rs:63-90` | supports | entry key enum |
| 25 | 3086 | `rust/utils/src/gpu_pool.rs:287-305` | supports | detection order |
| 26 | 3095 | `rust/utils/src/gpu_pool.rs:343-356` | supports | fallback rows |
| 27 | 3241 | `rust/core/src/telemetry/mod.rs:112-127` | supports | async send, failures logged |
| 28 | 3373 | `benchmarks/state_store/README.md:1-19` | supports | state-store benchmark |
| 29 | 3480 | `dev/run_cargo_test_sdk_features.sh:1-22` | supports | whole script |
| 30 | 3630 | `docs/package.json:6-13` | supports | Node version, build script |

### `wiki-e1c69c.md` (14 supports, 11 partial, 3 does not support, 2 missing file)

| # | Wiki line | Citation | Verdict | Note |
|---|---|---|---|---|
| 1 | 398 | `docs/astro.config.mjs:68-70` | supports | env prefixes |
| 2 | 1160 | `.github/workflows/release.yml:129-135` | supports | maturin action |
| 3 | 1177 | `.github/workflows/release.yml:159-176` | supports | free-threaded test job |
| 4 | 1257 | `rust/sdk/cocoindex_macros/src/lib.rs:22-30` | partial | evidence is in the doc comment above the range |
| 5 | 1550 | `python/cocoindex/_internal/app.py:52-159` | partial | 108 lines; nothing on tombstones or tracking |
| 6 | 1574 | `rust/core/src/engine/context.rs:37-93` | does not support | `AppContext` fields under a progress diagram |
| 7 | 1920 | `rust/py/src/target_state.rs:27-171` | partial | 145-line pointer |
| 8 | 1960 | `python/tests/core/test_live_component.py:61-64` | partial | a test call site, not semantics |
| 9 | 1974 | `python/cocoindex/resources/live_map.py:105-140` | partial | covers half the statement |
| 10 | 2066 | `docs/.../memoization_keys.mdx:4-6` | supports | frontmatter summary line |
| 11 | 2243 | `rust/py/src/target_state.rs:99-165` | does not support | sink registries, not `reconcile` |
| 12 | 3134 | `python/cocoindex/connectors/iggy/_source.py:1-7` | partial | module docstring only |
| 13 | 3549 | `python/cocoindex/ops/sentence_transformers.py:53-57` | supports | class docstring |
| 14 | 3554 | `python/cocoindex/ops/sentence_transformers.py:25-32` | supports | OOM detection |
| 15 | 3702 | `python/cocoindex/ops/entity_resolution/__init__.py:57-67` | supports | policy enum |
| 16 | 4047 | `python/cocoindex/connectors/neo4j/_target.py:16-18` | partial | driver details not shown |
| 17 | 4325 | `python/cocoindex/connectors/doris/_target.py:4-13` | partial | several table cells unsupported |
| 18 | 4344 | `rust/state_store/app_store.rs:50-54` | missing file | correct path is `rust/core/src/state_store/app_store.rs` |
| 19 | 4454 | `python/cocoindex/_internal/app.py:135-142` | supports | `result()` |
| 20 | 5052 | `rust/core/src/state_store/storage.rs:116` | supports | `Storage` struct |
| 21 | 5240 | `python/cocoindex/cli.py:24` | does not support | an import line; the claim contradicts `setting.py:12-20` |
| 22 | 5720 | `docs/.../ai_coding_agents.mdx:22-28` | supports | install command, verbatim |
| 23 | 5935 | `rust/sdk/cocoindex/benches/state_store_read.rs:37-41` | supports | imports naming the functions |
| 24 | 6294 | `examples/text_embedding_qdrant/main.py:46-106` | supports | pipeline body |
| 25 | 6340 | `examples/code_embedding/main.py:44-134` | partial | 91-line pointer |
| 26 | 6342 | `cocoindex/ops/text.py:48-49` | missing file | at the correct path those lines would not support it either |
| 27 | 6600 | `examples/patient_intake_extraction_dspy/main.py:16-25` | supports | signature class |
| 28 | 6966 | `examples/face_recognition/pyproject.toml:1-14` | partial | "Dlib" is not in the lines |
| 29 | 6967 | `examples/face_recognition/pyproject.toml:1-14` | partial | duplicate of #28 |
| 30 | 7025 | `examples/entire_session_search/main.py:53-53` | supports | context key definition |
