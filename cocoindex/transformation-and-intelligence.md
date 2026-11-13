# Transformation and Intelligence

## Summary

CocoIndex operations turn source content into values that a pipeline can store or use in later processing: position-tracked chunks, code matches, vectors, transcripts, and resolved entity names. A typical retrieval pipeline reads a file, splits it, embeds each chunk, and declares rows containing the vectors and source positions. The operations are independently composable; applications choose which stages they need. [docs/src/content/docs/ops/index.mdx:8-22] [examples/code_embedding/main.py:71-106]

## From source to searchable data

The code-embedding example connects the operations in a complete pipeline: [examples/code_embedding/main.py:71-106] [examples/code_embedding/main.py:109-137]

```mermaid
flowchart LR
    files["localfs.walk_dir"] --> process["process_file"]
    process --> detect["detect_code_language"]
    detect --> splitter["RecursiveSplitter"]
    splitter --> chunk["Chunk"]
    chunk --> embed["SentenceTransformerEmbedder"]
    embed --> row["CodeEmbedding"]
    row --> target["TableTarget"]
```

[examples/code_embedding/main.py:71-106] [examples/code_embedding/main.py:109-137]

1. **Read and split.** `process_file` reads a file, detects its language from the filename, and calls `RecursiveSplitter`. For supported grammars, the splitter uses syntax boundaries; otherwise it falls back to regex boundaries. Each `Chunk` carries its text and original positions. [examples/code_embedding/main.py:91-104] [rust/ops_text/src/split/recursive.rs:632-676] [python/cocoindex/resources/chunk.py:25-36]
2. **Embed each chunk.** `process_chunk` retrieves a `SentenceTransformerEmbedder` from context and embeds the chunk text. The local embedder memoizes individual calls and batches concurrent work. [examples/code_embedding/main.py:71-78] [python/cocoindex/ops/sentence_transformers.py:122-128] [python/cocoindex/ops/sentence_transformers.py:167-191]
3. **Declare the result.** The example declares a `CodeEmbedding` row containing the vector, code, filename, and line positions. Its embedding field carries an embedder context key as schema metadata, and the app declares a vector index. A query can then embed text and compare it with stored vectors. [examples/code_embedding/main.py:51-58] [examples/code_embedding/main.py:71-87] [examples/code_embedding/main.py:109-120] [examples/code_embedding/main.py:152-174]

The processing code is ordinary application code. The surrounding component and target APIs run it and reconcile declared rows; see [Declarative Processing Model](declarative-processing-model.md) for that lifecycle. [examples/code_embedding/main.py:91-106] [examples/code_embedding/main.py:109-137]

## Key interfaces

The Python modules are independently importable. Rust exposes corresponding operations behind features that avoid pulling in tree-sitter, ONNX, or HTTP dependencies unless needed. [docs/src/content/docs/ops/index.mdx:8-12] [rust/sdk/cocoindex/src/ops/mod.rs:1-25]

| Type or function | Role | Definition |
|---|---|---|
| `RecursiveSplitter`, `SeparatorSplitter` | Produce position-tracked chunks using syntax or regex boundaries. | [python/cocoindex/ops/text.py:40-54] [rust/sdk/cocoindex/src/ops/text.rs:104-110] |
| `CodeSource`, `CodePattern` | Share a parsed source and match reusable structural patterns. | [python/cocoindex/ops/code.py:30-38] [python/cocoindex/ops/code.py:115-120] |
| `Embedder`, `SentenceTransformerEmbedder` | Define single-text embedding and provide a local implementation. | [python/cocoindex/resources/embedder.py:14-25] [python/cocoindex/ops/sentence_transformers.py:53-57] |
| `VectorSchemaProvider`, `VectorSchema` | Supply vector element type and dimension for connector schemas. | [python/cocoindex/resources/schema.py:16-30] [rust/sdk/cocoindex/src/resources/schema.rs:28-34] |
| `LiteLLMEmbedder`, `LiteLLMTranscriber` | Call hosted embedding and transcription models from Python. | [python/cocoindex/ops/litellm.py:328-338] [python/cocoindex/ops/litellm.py:564-568] |
| `resolve_entities`, `PairResolver` | Select similar names and decide their canonical mapping. | [python/cocoindex/ops/entity_resolution/__init__.py:100-121] [python/cocoindex/ops/entity_resolution/__init__.py:491-501] |

## Other transformation paths

Code analysis can reuse the same `CodeSource` for splitting, matching, and extracting index terms. `CodePattern` compiles a pattern and a prefilter for reuse across files; matching returns syntax-node ranges and captures. A `SourceView` can add enclosing context while retaining source-grounded segments. Read [Code Parsing and Context Views](code-parsing-and-context-views.md) for shared parsing and rendering, and [Structural Matching and Prefilters](structural-matching-and-prefilters.md) for pattern syntax and search acceleration. [python/cocoindex/ops/code.py:30-38] [python/cocoindex/ops/code.py:94-120] [python/cocoindex/ops/code.py:270-292]

Splitting is also useful without code parsing. `SeparatorSplitter` applies explicitly chosen regex separators, while `RecursiveSplitter` plans chunks around size and overlap settings. Its result preserves byte and character offsets as well as line and column positions; [Text Splitting and Provenance](text-splitting-and-provenance.md) explains the boundary choices and fallback behavior. [python/cocoindex/ops/text.py:40-54] [python/cocoindex/ops/text.py:155-180] [python/cocoindex/resources/chunk.py:8-22]

Embedding can run locally or through a hosted service. Python’s `SentenceTransformerEmbedder` and `LiteLLMEmbedder` both provide vector schema information; Rust’s `fastembed` feature includes local text and image embedders. The image-search example embeds image bytes and text queries with CLIP, storing image vectors in Qdrant. See [Embedding Models and Vector Types](embedding-models-and-vector-types.md) for interfaces, batching, and schema metadata. [docs/src/content/docs/ops/index.mdx:49-55] [rust/sdk/cocoindex/src/ops/mod.rs:11-24] [examples/image_search/pipeline.py:61-75] [examples/image_search/pipeline.py:88-115]

Model calls can also produce text or structured data. Python’s `LiteLLMTranscriber` reads audio from a `FileLike`; Rust’s `ApiTranscriber` sends multipart audio to an OpenAI-compatible endpoint, and `ApiChatClient` requests JSON-object responses. The paper metadata example demonstrates a direct chat call followed by model validation. [Model Calls and Multimodal Processing](model-calls-and-multimodal-processing.md) covers these paths and their request behavior. [python/cocoindex/ops/litellm.py:604-609] [rust/sdk/cocoindex/src/ops/api.rs:264-278] [rust/sdk/cocoindex/src/ops/api.rs:384-392] [examples/paper_metadata/main.py:130-158]

Entity resolution composes embedding with a separate decision step: it embeds names, partitions the similarity graph, then runs a `PairResolver` within each component to build a canonical map. Existing-canonical policies can override which matched name wins. [Entity Resolution](entity-resolution.md) explains candidate selection, policies, and events. [python/cocoindex/ops/entity_resolution/__init__.py:491-514] [python/cocoindex/ops/entity_resolution/__init__.py:45-67]

## Terms

- **Chunk**: Text with start and end positions in its source. [python/cocoindex/resources/chunk.py:25-36]
- **CodeSource**: Text with a lazily parsed AST shared by code operations. [python/cocoindex/ops/code.py:30-38]
- **VectorSchema**: Element type and dimension needed for a vector column. [python/cocoindex/resources/schema.py:23-30]
- **PairResolver**: Callable that decides whether an entity matches a candidate canonical name. [python/cocoindex/ops/entity_resolution/__init__.py:100-108]