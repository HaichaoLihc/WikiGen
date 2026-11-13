# Declarative Processing Model

## Summary

A CocoIndex app reads source state, transforms it, and declares the target states that should exist. Processing components give work and declarations stable identities, enabling the engine to reuse unchanged work and clean up outputs when inputs disappear. [docs/src/content/docs/programming_guide/core_concepts.mdx:31-33] [docs/src/content/docs/programming_guide/core_concepts.mdx:56-76]

## From files to declared outputs

The `files_transform` app turns Markdown files into HTML files:

```python
@coco.fn(memo=True)
async def process_file(file: FileLike, outdir: pathlib.Path) -> None:
    html = _markdown_it.render(await file.read_text())
    outname = "__".join(file.file_path.path.parts) + ".html"
    localfs.declare_file(outdir / outname, html, create_parent_dirs=True)


@coco.fn
async def app_main(sourcedir: pathlib.Path, outdir: pathlib.Path) -> None:
    files = localfs.walk_dir(
        sourcedir,
        path_matcher=PatternFilePathMatcher(included_patterns=["**/*.md"]),
        live=True,
    )
    await coco.mount_each(process_file, files.items(), outdir)
```

[examples/files_transform/main.py:11-25]

The `App` binds `app_main` to source and output directories. An update runs the main function as the root processing component; `mount_each` creates independent work for keyed source items. [examples/files_transform/main.py:28-33] [python/cocoindex/_internal/app.py:298-302] [python/cocoindex/_internal/api.py:450-466]

```mermaid
flowchart LR
    app["App"] --> main["app_main"]
    main --> walk["localfs.walk_dir"]
    walk --> mount["coco.mount_each"]
    mount --> process["process_file"]
    process --> declare["localfs.declare_file"]
    declare --> target["filesystem"]
```

[examples/files_transform/main.py:11-33] [docs/src/content/docs/programming_guide/core_concepts.mdx:58-66]

`declare_file` builds a keyed file specification and passes it to `declare_target_state`; it does not ask the caller to calculate an insert, update, or delete. The declaration is recorded in the current component context for reconciliation. [python/cocoindex/connectors/localfs/_target.py:449-460] [python/cocoindex/connectors/localfs/_target.py:481-496] [python/cocoindex/_internal/target_state.py:614-628]

## Components and identity

A processing component groups work with its declared outputs. Components can finish independently, so one file’s outputs can be applied without waiting for every other file. Backend atomicity depends on the target: a database, for example, can apply a batch within a transaction. [docs/src/content/docs/programming_guide/core_concepts.mdx:74-82]

| Call | Role |
|---|---|
| `mount` | Starts a background component and returns a readiness handle. |
| `use_mount` | Runs a dependent component and returns its result; refreshing it requires rerunning its parent. |
| `mount_each` | Creates one component per keyed item and returns a handle for their readiness. |

[python/cocoindex/_internal/api.py:234-253] [python/cocoindex/_internal/api.py:358-373] [python/cocoindex/_internal/api.py:450-471]

A stable path lets the engine associate a component with its previous work. For ordinary keyed iterables, `mount_each` appends each item key to the child path. The default subpath derives from the function name; an explicit `component_subpath` lets callers distinguish repeated uses or compose path parts. See [Component Mounting and Identity](component-mounting-and-identity.md). [python/cocoindex/_internal/api.py:481-494] [python/cocoindex/_internal/api.py:506-520] [python/cocoindex/_internal/component_ctx.py:312-339]

## Reuse and cleanup

`@coco.fn(memo=True)` on `process_file` allows unchanged work to be skipped when its inputs and logic remain valid. Memoization can also operate inside a component: the text-embedding example splits each file into chunks and calls the embedder for each chunk, allowing reuse at a finer granularity. See [Memoization and State Reuse](memoization-and-state-reuse.md). [examples/files_transform/main.py:11-15] [docs/src/content/docs/programming_guide/core_concepts.mdx:138-146] [examples/text_embedding/main.py:72-101]

| Source change | Result |
|---|---|
| New item | A component declares its outputs. |
| Changed item | Its new declarations are reconciled against its previous outputs. |
| Removed item | Its component’s associated target states are cleaned up. |

[docs/src/content/docs/programming_guide/core_concepts.mdx:86-105] [docs/src/content/docs/programming_guide/core_concepts.mdx:107-134]

`live=True` makes the directory’s `items()` a view that supports watching through `mount_each`; the example notes that the update must also run in live mode to continue watching. See [Live Component Lifecycle](live-component-lifecycle.md). [python/cocoindex/connectors/localfs/_source.py:362-380] [examples/text_embedding/main.py:117-123]

## Terms

- **App**: The top-level executable that reads sources, transforms data, and declares targets. [docs/src/content/docs/programming_guide/core_concepts.mdx:56-66]
- **Processing component**: A unit that groups processing with its target states. [docs/src/content/docs/programming_guide/core_concepts.mdx:74-76]
- **Component subpath**: Relative path parts used to identify a child component. [python/cocoindex/_internal/component_ctx.py:264-270]
- **Target state**: A keyed desired value declared through a provider. [python/cocoindex/_internal/target_state.py:571-576]