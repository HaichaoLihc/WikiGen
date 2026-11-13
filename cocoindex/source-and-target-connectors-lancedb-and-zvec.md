# LanceDB and zvec Targets

## Summary

LanceDB reconciles keyed rows in tables; zvec reconciles documents in collections stored under a local directory. Both infer schemas from record types and skip unchanged records, but LanceDB supports additive column evolution while zvec rebuilds a managed collection on schema changes. [python/cocoindex/connectors/lancedb/_target.py:259-285] [python/cocoindex/connectors/lancedb/_target.py:1145-1187] [python/cocoindex/connectors/zvec/_target.py:477-513] [python/cocoindex/connectors/zvec/_target.py:840-844]

## Schemas and identity

| | LanceDB | zvec |
|---|---|---|
| Schema | `TableSchema` maps columns to PyArrow types. | `CollectionSchema` maps columns to scalar, dense, sparse, or FTS fields. |
| Primary key | One or more columns form the row key. | Exactly one scalar column becomes a string document ID. |
| Connection | A `LanceAsyncConnection` is provided through context. | `ManagedConnection` caches collection handles under a base directory. |

zvec caches handles because opening the same collection twice would conflict with its exclusive write lock. A collection needs at least one dense or sparse vector field. [python/cocoindex/connectors/lancedb/_target.py:223-257] [python/cocoindex/connectors/zvec/_target.py:111-116] [python/cocoindex/connectors/zvec/_target.py:444-475] [python/cocoindex/connectors/zvec/_target.py:961-968]

LanceDB’s example derives a schema from a dataclass whose embedding is annotated with a vector-schema provider, then mounts the table for downstream declarations: [examples/text_embedding_lancedb/main.py:46-53] [examples/text_embedding_lancedb/main.py:98-106]

```python
    target_table = await lancedb.mount_table_target(
        LANCE_DB,
        table_name=TABLE_NAME,
        table_schema=await lancedb.TableSchema.from_class(
            DocEmbedding, primary_key=["id"]
        ),
    )
```

[examples/text_embedding_lancedb/main.py:100-106]

## Indexes

LanceDB declares vector and full-text indexes as separate attachments to the row provider. Python supports IVF-PQ and HNSW-PQ vector indexes; FTS options include language and whether to retain positions for phrase queries. Changed index specifications create or replace the index, and removed declarations drop it. [python/cocoindex/connectors/lancedb/_target.py:669-675] [python/cocoindex/connectors/lancedb/_target.py:1322-1349] [python/cocoindex/connectors/lancedb/_target.py:1371-1404] [python/cocoindex/connectors/lancedb/_target.py:760-800]

zvec configures indexes in the collection schema instead. Dense vectors use HNSW with a metric and optional quantization; sparse vectors are explicitly marked. `ZvecFtsType` marks a string field for full-text indexing and requires zvec 0.5 or later. [python/cocoindex/connectors/zvec/_target.py:231-251] [python/cocoindex/connectors/zvec/_target.py:540-585]

## Record synchronization

```mermaid
flowchart LR
    schema["TableSchema / CollectionSchema"] --> target["TableTarget / CollectionTarget"]
    target --> row["declare_row"]
    row --> reconcile["reconcile"]
    reconcile --> apply["upsert / delete"]
```

LanceDB fingerprints declared rows, batches upserts through `merge_insert` on primary-key columns, and deletes by key. After mutations it may optimize the table. zvec converts each row into a document, batches upserts and deletes, checks operation statuses, and optimizes after mutations. [python/cocoindex/connectors/lancedb/_target.py:432-464] [python/cocoindex/connectors/lancedb/_target.py:597-636] [python/cocoindex/connectors/lancedb/_target.py:677-718] [python/cocoindex/connectors/zvec/_target.py:638-689]

LanceDB adds new columns in place as nullable, backfilling existing rows with null. When that null is the only apparent row change, it can advance the fingerprint without rewriting the row. Incompatible changes replace the table and invalidate its children; zvec has no in-place schema evolution and replaces a system-managed collection on any tracked schema change. [python/cocoindex/connectors/lancedb/_target.py:466-491] [python/cocoindex/connectors/lancedb/_target.py:1145-1187] [python/cocoindex/connectors/lancedb/_target.py:1233-1248] [python/cocoindex/connectors/zvec/_target.py:773-798] [python/cocoindex/connectors/zvec/_target.py:833-844]

The Rust SDK provides LanceDB table, vector-index, and FTS targets. Its index attachments belong to the row provider so destructive table replacement triggers their recreation. [rust/sdk/cocoindex/src/connectors/lancedb.rs:447-453] [rust/sdk/cocoindex/src/connectors/lancedb.rs:464-494] [rust/sdk/cocoindex/src/connectors/lancedb.rs:514-540]

## Terms

- **`TableSchema`**: LanceDB column definitions and primary-key columns. [python/cocoindex/connectors/lancedb/_target.py:223-228]
- **`CollectionSchema`**: zvec document fields, vectors, and single primary key. [python/cocoindex/connectors/zvec/_target.py:444-454]
- **Index attachment**: A separately declared LanceDB vector or FTS target associated with a table’s row provider. [python/cocoindex/connectors/lancedb/_target.py:669-675]