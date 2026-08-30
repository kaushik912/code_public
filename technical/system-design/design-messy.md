# one-click checkout
Happy Path (numbered 1-8):

Validate User & Check Cache (Checkout → Redis)
Reserve Inventory (Checkout → Inventory Service)
Fraud Check (Checkout → Fraud Service)
Authorize Payment (Checkout → Payment Service)
External Auth (Payment Service → Stripe/Adyen)
Create Order (Checkout → Order Service)
Capture Payment (Checkout → Payment Service)
Notify (Async) (Order → Message Broker → Notification)

---

# audio file upload

Client → API Gateway/Upload Service: "I want to upload audio file X"
Upload Service → S3: Generates pre-signed URL (with expiration, size limits, etc.)
Upload Service → Client: Returns the pre-signed URL + upload acknowledgment
Client → S3: Uploads directly to S3 using that URL
S3 → Message Queue: Triggers event after successful upload
Processing workers pick up from queue asynchronously

Why server-side generation for pre-signed URL?

Security: Server controls who can upload, enforces auth, sets constraints (file size, content type, expiration)
Validation: Server can check user quotas, rate limits before issuing URL
Tracking: Server logs the upload request and can tie it to user/session before processing starts
The client never has direct S3 credentials—just a time-limited, scoped URL for that specific upload. This keeps the low-latency acknowledgment (steps 1-3 are fast) while offloading the heavy 20MB transfer to a direct S3 path.


Low latency acknowledgment path means the client gets a fast "upload accepted" response without waiting for the actual file processing to complete.

Here's the contrast:

Without low latency path (slow):

Client uploads 20MB audio → Server
Server stores file
Server processes audio (transcoding, analysis, etc.) ← takes minutes
Server responds "done" → Client
Total wait time: 10+ minutes. Terrible UX.

With low latency path (fast):

Client requests upload → Upload Service
Upload Service generates pre-signed URL, logs request to DB
Upload Service responds immediately: "Here's your URL, upload ID: 12345" → Client ← ~100-200ms
Client uploads directly to S3 (in background)
Async workers process later (client doesn't wait)
Total acknowledgment time: sub-second. Client can move on.

Why use S3 instead of OTLP like Postgres?
- Cost efficiency ( S3 is cheaper than Postgres)
- Scale: S3 handles 100K uploads/day trivially, Postgres Blob storage hits performance walls quickly, limited by disk I/O, complex sharding needed
- Audio files are immutable blobs, you write once and ready many times. S3 is built for this.
- postgres excels at transactional updates - not quite useful here.
- S3 triggers events natively for async processing. 
- S3 provides pre-signed URLs for secure direct uploads
- S3 has 11 9s durability whereas Postgres you need to handle replication, backup, disaster recovery,etc.

Posgres usecases:
- Postgres is still useful for metadata around uploads, some fields could be:
    - upload_id
    - user_id
    - file_name
    - file_status
    - timestamps
    - processing_state
- Could help answer : "Show me all uploads by user X in last week"