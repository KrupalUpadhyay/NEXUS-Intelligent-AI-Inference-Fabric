# Phase 4: Semantic Cache

## Flow

```text
Prompt -> embedding -> nearest same-task vector -> threshold check
      -> cache hit: return saved output
      -> miss: execute inference, then store embedding + response
```

## Design

`HashingEmbeddingProvider` is deterministic and offline for development. Its
interface is intentionally compatible with a future Sentence Transformer
implementation. `PgvectorSemanticCacheRepository` contains the production SQL
for cosine similarity; the included migration creates the vector table/index.

Local development defaults to an in-memory repository so the API remains useful
without a running database. Docker selects `pgvector` and applies the migration
when its Postgres data volume is first initialized.

## Next phase

Replace the development executor with adapter-based Gemma/Ollama and realistic
mock backends.
