# Testing and Performance

## Summary

Python tests use isolated CocoIndex environments and can start real services through testcontainers. CI combines a platform and interpreter matrix with separate type checks and Rust SDK feature checks. Benchmarks measure incremental pipeline behavior, entity resolution and state-store costs. [AGENTS.md:258-288] [.github/workflows/_test.yml:23-34] [benchmarks/file_summarization/README.md:53-71] [benchmarks/entity_resolution/README.md:1-13] [benchmarks/state_store/README.md:1-19]

## Test environments and Docker

Prefer end-to-end tests through user-facing APIs; use unit tests where internal edge cases warrant them. `create_test_env(__file__)` derives a temporary database path from the test file. For async resources, construct the environment inside an async fixture so it uses the same event loop, and supply a per-test suffix to avoid opening the same environment twice. [AGENTS.md:258-284] [python/tests/common/environment.py:9-34]

```python
@pytest_asyncio.fixture
async def pg_env(request: pytest.FixtureRequest) -> Any:
    pool = await asyncpg.create_pool(dsn)
    coco_env = common.create_test_env(__file__, suffix=request.node.name)
    coco_env.context_provider.provide(DB_KEY, pool)
    yield pool, coco_env
    await pool.close()
```

[AGENTS.md:275-281]

List every container image in `pytest.mark.requires_docker(...)`. Tests carrying that marker are skipped if Docker is unavailable. After deselection, pytest pre-pulls missing images for selected tests so a cold download does not consume the first test’s timeout; failed pre-pulls warn and leave the fixture to retry. [AGENTS.md:286-308] [python/tests/conftest.py:92-100] [python/tests/conftest.py:125-138] [python/tests/conftest.py:146-166]

## Test commands and CI

The usual local checks are `uv run pytest python/`, `uv run mypy`, and Rust tests after rebuilding the extension when Rust changes. `dev/run_cargo_test.sh` chooses a Python interpreter and supplies paths needed by embedded Python; use it when Cargo tests cannot find the Python standard library. [AGENTS.md:10-21] [dev/run_cargo_test.sh:8-25] [dev/run_cargo_test.sh:61-78]

The SDK has no default features. Its separate feature script checks all features and targets, then runs tests for a selected set that does not require an external server. Standalone Rust examples and benchmarks are checked with `cargo check --locked` in a shared target directory to catch SDK consumer breakage without full test builds. [dev/run_cargo_test_sdk_features.sh:1-22] [dev/run_cargo_test_rust_externs.sh:1-15] [dev/run_cargo_test_rust_externs.sh:21-29]

| CI workflow | Coverage |
|---|---|
| Build-test | Python 3.11 on Linux, macOS and Windows; free-threaded Python 3.14 on those platforms |
| E2E type check | Mypy on Python 3.11–3.14 |
| SDK feature check | All-feature type check plus selected feature tests; skipped on the macOS Intel build-test leg |

[.github/workflows/_test.yml:23-34] [.github/workflows/_test.yml:139-156] [.github/workflows/e2e_type_check.yml:23-47]

## Benchmark workflows

| Benchmark | What it measures | Useful starting run |
|---|---|---|
| `file_summarization` | Rust and Python pipelines across cold, warm, edit and shape phases | `./run.sh --scenario codebase --profile mixed --scale tiny` |
| `entity_resolution` | Resolution time, calls, candidates and concurrency with deterministic synthetic data | `--profile synthetic-fast` |
| `state_store` | Cold update, warm update and drop costs as component and target-state counts grow | `./run.sh --n 100` |

[benchmarks/file_summarization/README.md:53-71] [benchmarks/file_summarization/README.md:134-153] [benchmarks/entity_resolution/README.md:3-24] [benchmarks/state_store/README.md:3-10] [benchmarks/state_store/README.md:25-35]

The file-summarization runner builds Rust in release mode, creates fresh datasets per trial, runs both implementations through each phase, and compares output-tree hashes before reporting timings. Warm runs expose cache reuse; edit and shape runs exercise incremental changes. [benchmarks/file_summarization/README.md:115-132] [benchmarks/file_summarization/README.md:155-162]

```mermaid
flowchart LR
    cold --> warm
    warm --> edit
    edit --> shape
    shape --> compare["compare output hashes"]
```

[benchmarks/file_summarization/README.md:53-71] [benchmarks/file_summarization/README.md:155-162]

The entity-resolution benchmark offers simulated latency and component-parallelism profiles as well as OpenAI-backed runs. The state-store benchmark uses a no-op target to isolate engine bookkeeping from external I/O, with a fresh database for each component/target-count cell. [benchmarks/entity_resolution/README.md:15-50] [benchmarks/entity_resolution/README.md:69-77] [benchmarks/state_store/README.md:12-23]

## Terms

- **`requires_docker`**: Pytest marker listing images required by a Docker-backed test. [python/tests/conftest.py:146-150]
- **SDK feature check**: All-feature type check and selected optional-feature tests. [dev/run_cargo_test_sdk_features.sh:1-22]
- **`cold`, `warm`, `edit`, `shape`**: Successive file-summarization benchmark phases that exercise initial, unchanged and modified inputs. [benchmarks/file_summarization/README.md:53-71]