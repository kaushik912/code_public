# Streaming

**Streaming** means processing data as a continuous flow of small chunks, rather than loading the whole thing into memory and handling it all at once.

**Non-streaming (buffering):**
```
Read entire 4GB file into memory → transform it → write it out
```

**Streaming:**
```
Read a chunk → transform it → write it → read next chunk → ...
```

You only ever hold a small window of data in memory at a time. This lets you process datasets larger than RAM, and start producing output before you've finished reading input (lower latency to first byte).

The core mental model is a **pipeline** of connected stages:

```
[Producer] → [Transform] → [Transform] → [Consumer]
  (source)     (filter)      (map)        (sink)
```

Each stage pulls from the one before it and pushes to the one after.

---

# Back pressure

**The problem:** what happens when a producer is *faster* than a consumer?

Say a source reads from disk at 500 MB/s, but the consumer uploads to a slow network at 5 MB/s. Without any coordination, the fast producer keeps generating data that piles up in a buffer between them. That buffer grows unboundedly → memory balloons → the process crashes (OOM).

**Back pressure** is the mechanism by which a slow consumer signals upstream: *"stop, I'm not ready for more yet."* The producer then pauses until the consumer drains its buffer and says *"ok, resume."*

It flows *backward* through the pipeline (hence the name):

```
[Producer] ←── "slow down!" ←── [Consumer]
   pauses                         overwhelmed
```

Without back pressure, you have to choose between dropping data, unbounded memory growth, or crashing. Back pressure gives you a fourth option: the whole pipeline self-regulates to the speed of its slowest stage.

---

# Real-life analogies

**The restaurant kitchen.** Orders (data) come in from the dining room. If the kitchen (consumer) is slammed, the expediter tells the host to *stop seating tables*. That "stop seating" signal is back pressure — it propagates from the bottleneck (kitchen) back to the source (front door).

**The checkout line at a grocery store.** The conveyor belt is the buffer. When the cashier falls behind, groceries pile up at the end. Eventually there's no room, and you (the producer) physically *stop* putting items on the belt. You've been back-pressured.

**A funnel pouring into a bottle.** Pour too fast and the funnel overflows (buffer overrun / dropped data). You naturally slow your pour to match how fast the bottle drains. That's back pressure by observation.

**Water pipes / plumbing.** Literally where the term comes from — if a downstream valve is nearly closed, pressure builds *back up* the pipe toward the source.

---

# Where you meet this in real software

**Node.js streams** — the canonical example. `stream.pipe()` handles back pressure automatically:
```js
readableStream.pipe(writableStream); // pauses source when dest is full
```
When you write manually, `writable.write()` returns `false` when its buffer is full. The correct pattern is to *stop writing* and wait for the `'drain'` event:
```js
if (!dest.write(chunk)) {
  source.pause();                    // back off
  dest.once('drain', () => source.resume());
}
```

**TCP itself** has back pressure built in — the receive window (`rwnd`) in the TCP header tells the sender exactly how much more it's allowed to send. A slow receiver advertises a small window and the sender throttles.

**Kafka / message queues** — consumers pull at their own pace. If a consumer group lags, messages sit in the topic (bounded by retention) rather than overwhelming the consumer. The queue *is* the buffer, and consumer lag is the visible back-pressure signal you monitor.

**Reactive frameworks** — RxJS, Project Reactor, Akka Streams have back pressure as a first-class concept. Reactive Streams' `Subscription.request(n)` is explicit: the consumer literally requests *n* items, and the producer may only emit that many.

**gRPC / HTTP/2 streaming** — flow control per-stream, same idea as TCP but at the application layer.

**Video streaming (Netflix, YouTube)** — adaptive bitrate is back pressure in spirit: when your buffer runs low or your network slows, the client requests lower-quality (smaller) chunks so the consumer can keep up.

---

# The key trade-off to remember

| Approach | Memory | Latency to first byte | Complexity |
|---|---|---|---|
| Buffer everything | High (whole dataset) | High | Simple |
| Stream, no back pressure | Unbounded (can crash) | Low | Medium |
| Stream + back pressure | Bounded, predictable | Low | Higher |

Back pressure is what makes streaming *safe* at scale. Streaming without it is just deferring the memory explosion, not preventing it.

Want me to sketch a concrete code example in a specific language (Node, Go, Java/Reactor, Python asyncio), or walk through how a real system like Kafka handles a lagging consumer?
