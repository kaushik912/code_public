## Summary
Here's a consolidated reference — organized by category, with concrete examples and where each genuinely shines.

## Core database types

| Type | Examples | Best fit / reach for it when… | Avoid when… |
|---|---|---|---|
| **Relational (RDBMS)** | PostgreSQL, MySQL, SQL Server, Oracle | You need transactions, joins, data integrity, and flexible ad-hoc queries. The safe default for most apps. | Massive write scale beyond one big box; data doesn't fit a schema |
| **Document (NoSQL)** | MongoDB, Couchbase, Firestore | Flexible/evolving schemas, nested JSON-like objects, rapid product iteration | You need heavy joins or multi-record transactions across entities |
| **Key-Value** | Redis, DynamoDB, etcd, Riak | Ultra-fast lookups by a known key, huge scale, simple access patterns (carts, sessions, profiles) | Ad-hoc queries you didn't design keys for |
| **Wide-Column** | Cassandra, ScyllaDB, HBase, Bigtable | Massive write throughput, geo-distributed, time-series-ish, high availability with no single master | Complex queries, joins, low-volume apps (overkill) |
| **Graph** | Neo4j, Amazon Neptune, ArangoDB | Relationships *are* the query — social graphs, fraud rings, recommendations, knowledge graphs | Simple tabular data with few relationships |
| **Time-Series** | TimescaleDB, InfluxDB, Prometheus | Timestamped metrics/events, "how did this change over time," retention + downsampling | High-cardinality tag explosion; relational joins |
| **Vector** | Pinecone, Weaviate, Milvus, pgvector, Qdrant | Similarity search over embeddings — RAG, semantic search, recommendations, AI apps | Exact-match or transactional lookups |
| **Search engine** | Elasticsearch, OpenSearch, Solr | Full-text search, relevance ranking, fuzzy matching, log analytics | System of record (it's a search layer, not source of truth) |
| **Analytical / OLAP (columnar)** | ClickHouse, DuckDB, Snowflake, BigQuery, Redshift | Aggregations (`SUM`, `GROUP BY`) over billions of rows; dashboards, reporting, BI | Frequent single-row updates / OLTP |
| **In-memory / cache** | Redis, Memcached | Speed above all; caching, rate limiting, leaderboards, ephemeral data | Durable system of record (data lives in RAM) |
| **NewSQL / distributed SQL** | CockroachDB, Google Spanner, YugabyteDB, Vitess | SQL + strong consistency **and** horizontal scale, multi-region | Small apps where plain Postgres is simpler |
| **Object storage** | Amazon S3, GCS, Azure Blob, MinIO | Files, blobs, images, video, backups, data-lake storage, static assets | Anything needing querying/indexing of structured records |
| **Ledger / immutable** | Amazon QLDB, blockchain-style stores | Append-only, tamper-evident audit history (finance, compliance) | Normal mutable data |
| **Spatial / GIS** | PostGIS, (extensions on most DBs) | Geographic queries — "within 5km," routing, maps | Non-geographic data |
| **Embedded** | SQLite, RocksDB, LMDB, DuckDB | Runs inside the app, no server — mobile, desktop, edge, local files | Multi-user concurrent server workloads |
| **Message / streaming (log store)** | Apache Kafka, Pulsar | Durable event streams, pub/sub, decoupling services, event sourcing | Random-access querying of records |

## Same table, viewed by workload (often the more practical lens)

| Workload | What it means | Go-to picks |
|---|---|---|
| **OLTP** | Many small reads/writes, one record at a time | PostgreSQL, MySQL, MongoDB, DynamoDB |
| **OLAP** | Few queries, each scans huge data | ClickHouse, BigQuery, Snowflake, DuckDB |
| **Caching** | Throwaway, ultra-fast | Redis, Memcached |
| **Search** | Text + relevance | Elasticsearch, OpenSearch |
| **Similarity / AI** | Nearest-neighbor over vectors | Pinecone, pgvector, Weaviate |
| **Metrics / monitoring** | Timestamped series | Prometheus, InfluxDB, TimescaleDB |
| **Relationships** | Graph traversals | Neo4j, Neptune |
| **Bulk file storage** | Blobs & static assets | S3, GCS, Azure Blob |
| **Event streaming** | Ordered, durable event logs | Kafka, Pulsar |

## Two things to keep in mind

**1. PostgreSQL is a genuine "Swiss army knife."** With extensions it covers many of these boxes — relational + JSON documents (JSONB) + time-series (TimescaleDB) + vector (pgvector) + geospatial (PostGIS) + full-text search. For a lot of projects the honest answer is *"just use Postgres until something forces you off it."*

**2. Real systems mix several.** A typical production stack might be: **Postgres** (source of truth) + **Redis** (cache) + **Elasticsearch** (search) + **S3** (files) + **ClickHouse** (analytics) + **Kafka** (events between them). You pick the specialist only when a specific access pattern or scale outgrows your main database.

If you tell me your actual workload, I'll narrow this to the 2–3 rows that matter for you.
