# Native Rust SDK

## Summary

The `cocoindex` Rust crate exposes a context-based pipeline API that calls the shared Rust engine directly. An `Environment` supplies resources, an `App` runs a closure with a `Ctx`, and macros add logic tracking, memoization, and component mounts. Optional Cargo features select connectors and operations. [rust/sdk/cocoindex/src/app.rs:9-14] [rust/sdk/cocoindex/src/lib.rs:41-54] [rust/sdk/cocoindex/Cargo.toml:8-31]

## Building a pipeline

The crate root re-exports common types, while `cocoindex::prelude::*` collects pipeline types, macros, and Serde derives. Connector and operation modules remain available through their module paths. [rust/sdk/cocoindex/src/lib.rs:3-6] [rust/sdk/cocoindex/src/prelude.rs:45-54]

The quickstart provides a database and embedder under typed keys, opens an app, and runs its main function:

```rust
    let app = Environment::builder()
        .db_path(".cocoindex_db")
        .provide_key(&DB, database)
        .provide_key(&EMBEDDER, embedder)
        .build()
        .await?
        .app("RustTextEmbeddingQuickstart")
        .await?;

    let stats = app.run(move |ctx| app_main(ctx, sourcedir)).await?;
```

[docs/src/content/docs/getting_started/rust_quickstart.mdx:217-226]

`Ctx` carries the current core component context and app state into pipeline code. `get_key` retrieves a named resource; for a change-detecting key, it also records the resource fingerprint as a dependency of the current function and component. A missing key returns an error. [rust/sdk/cocoindex/src/ctx.rs:323-335] [rust/sdk/cocoindex/src/ctx.rs:562-585]

The quickstart walks Markdown files, mounts `process_file` for each item, and declares resulting rows in a table. Its file paths identify separate components, allowing unchanged files to reuse prior work. See [Declarative Processing Model](declarative-processing-model.md) and [Component Mounting and Identity](component-mounting-and-identity.md) for the execution model. [docs/src/content/docs/getting_started/rust_quickstart.mdx:178-194]

## Macros and component calls

The procedural macros connect ordinary Rust functions and types to engine tracking. [rust/sdk/cocoindex/src/lib.rs:98-100] [rust/sdk/cocoindex_macros/src/lib.rs:1027-1080]

| Macro | Purpose |
|---|---|
| `#[function]` | Tracks function logic; `memo` adds function memoization, and `batching` supports item-shaped calls to a batch-shaped body. |
| `use_mount!` | Runs a function in a foreground child component. |
| `mount_each!` | Mounts a function for each keyed item. |
| `#[derive(MemoInput)]` | Gives a struct or enum compositional memoization behavior; its fields must implement `MemoInput`. |
| `#[derive(SchemaFields)]` | Derives a connector-agnostic table schema from a struct. |

[rust/sdk/cocoindex_macros/src/lib.rs:14-22] [rust/sdk/cocoindex_macros/src/lib.rs:1329-1335] [rust/sdk/cocoindex_macros/src/lib.rs:1398-1407] [rust/sdk/cocoindex_macros/src/lib.rs:1679-1694]

Mount macros build a component memo identity from the entry function and its arguments. They prefer `MemoInput` for arguments that support it, including external-state validation; otherwise they use serialized values without that validation. `Ctx::scope` is the direct, always-run alternative. Outside a pipeline context, its closure runs directly. [rust/sdk/cocoindex/src/mount.rs:35-44] [rust/sdk/cocoindex/src/mount.rs:59-82] [rust/sdk/cocoindex/src/ctx.rs:1026-1058]

A bare `#[function]` tracks changes but does not itself enable function memoization. For `ctx.memo`, the closure body is not automatically logic-tracked; a key that must follow enclosing function edits needs the generated hash explicitly. See [Logic Change Detection](logic-change-detection.md). [rust/sdk/cocoindex_macros/src/lib.rs:1031-1045] [rust/sdk/cocoindex_macros/src/lib.rs:1060-1063]

## Core integration and features

The SDK supplies a private `RustProfile` to the shared engine. It adapts closures into `BoxedProcessor`, uses `ContextStore` for host resources, and represents persisted values as MessagePack bytes. The engine operates through those adapters; users program against `Ctx` and the public SDK types. [rust/sdk/cocoindex/src/profile.rs:24-61] [rust/sdk/cocoindex/src/profile.rs:90-105]

```mermaid
flowchart LR
    app["App::run"] --> ctx["Ctx"]
    ctx --> processor["BoxedProcessor"]
    processor --> engine["cocoindex_core"]
    engine --> profile["RustProfile"]
    profile --> sink["BoxedSink"]
```

[rust/sdk/cocoindex/src/ctx.rs:323-328] [rust/sdk/cocoindex/src/profile.rs:28-43] [rust/sdk/cocoindex/src/profile.rs:140-157]

Cargo features bring in optional dependencies for capabilities such as `fs_live`, `text`, `code_match`, `fastembed`, and individual connectors. For example, the quickstart enables `postgres`, `text`, and `fastembed`; select the features required by the pipeline. [rust/sdk/cocoindex/Cargo.toml:8-31] [docs/src/content/docs/getting_started/rust_quickstart.mdx:30-43]

## Terms

- **Ctx**: The Rust pipeline context used to access resources and engine-backed operations. [rust/sdk/cocoindex/src/ctx.rs:323-328]
- **ContextKey**: A typed, named key for a provided resource. [rust/sdk/cocoindex/src/ctx.rs:562-567]
- **RustProfile**: The SDK’s private implementation of the engine’s host-specific types. [rust/sdk/cocoindex/src/profile.rs:24-43]
- **MemoInput**: The trait used to supply memo identity and optional state validation. [rust/sdk/cocoindex/src/mount.rs:19-25]