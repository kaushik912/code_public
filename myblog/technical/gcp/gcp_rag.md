> **Ingestion flow**

1. Store documents in GCS
2. Pub/Sub triggers Cloud Run ingestion
3. Documents are parsed, chunked, and embedded using Vertex AI
4. Embeddings are stored in AlloyDB (vector store)

> **Query flow**

5. User query is embedded and used for semantic search
6. Relevant chunks are added to the prompt
7. Prompt is sent to Vertex AI LLM and response is returned

That’s a **textbook RAG architecture on Google Cloud**.

## Key Google Cloud Services

| System Design Concept                | Google Cloud Service       | What it Does                                                                |
| ------------------------------------ | -------------------------- | --------------------------------------------------------------------------- |
| Asynchronous messaging & decoupling  | **Pub/Sub**                | Scalable event-driven messaging that decouples producers from consumers     |
| Serverless compute & autoscaling     | **Cloud Run**              | Runs containerized services with automatic scaling and no server management |
| Object storage for unstructured data | **Cloud Storage**          | Durable, low-cost storage for files, documents, and datasets                |
| Document parsing & data extraction   | **Document AI**            | Converts unstructured documents into structured data                        |
| Vector storage / high-performance DB | **AlloyDB for PostgreSQL** | Fully managed PostgreSQL-compatible DB optimized for demanding workloads    |
| Analytics & large-scale querying     | **BigQuery**               | Serverless data warehouse for analytics, ML, and BI                         |
| ML platform & LLM integration        | **Vertex AI**              | Train, deploy, and customize ML models and LLM-powered applications         |
| Centralized logging                  | **Cloud Logging**          | Collects, searches, and analyzes application and system logs                |
| Metrics, dashboards & alerting       | **Cloud Monitoring**       | Tracks performance, availability, and system health                         |
