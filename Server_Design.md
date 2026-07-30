# System Architecture Design: High-Scale Multiplayer Matchmaking & Game Sharding

## Basic design
```text
                     +----------------------------+
                     |       Global Clients       |
                     +-------------+--------------+
                                   | (WSS / HTTP)
                                   v
                     +----------------------------+
                     |       Edge / CDN / LB      |
                     +-------------+--------------+
                                   |
         +-------------------------+-------------------------+
         |                                                   |
         v                                                   v
+------------------------+                        +------------------------+
|   API Gateway (REST)   |                        |  WebSocket Gateways    |
| (Auth, Rooms, History) |                        |  (State Updates, Live) |
+-----------+------------+                        +-----------+------------+
            |                                                   |
            +-------------------------+-------------------------+
                                      |
                                      v
                     +----------------------------+
                     |    Redis Distributed Bus   |
                     |  (Pub/Sub, Matchmaking Q)  |
                     +-------------+--------------+
                                   |
         +-------------------------+-------------------------+
         |                         |                         |
         v                         v                         v
+------------------+     +------------------+     +------------------+
|    Matchmaker    |     |  Game Allocator  |     |  Game Servers    |
| (Skill/Latency)  |     | (Shard Selector) |     |  (Sharded Pods)  |
+------------------+     +------------------+     +--------+---------+
                                                           |
                                      +--------------------+--------------------+
                                      | (In-Memory Buffer & Move Log)           |
                                      v                                         v
                            +--------------------+                    +--------------------+
                            |   Redis RAM List   |                    | Background Worker  |
                            | (Instant Replay)   |                    | (Async Batch Flush)|
                            +--------------------+                    +--------------------+
                                      |                                         |
                                      +--------------------+--------------------+
                                                           |
                                                           v
                                                  +------------------+
                                                  |  Observability   |
                                                  | (Metrics/Tracing)|
                                                  +------------------+
```
---

# Architectural Decisions & Explanations

### 1. Stateless API and WebSocket Gateways
* **Decision:** Decouple connection management from business logic by routing all persistent connections through dedicated WebSocket Gateway nodes.
* **Explanation:** To support 10 million concurrent users, connections are distributed across roughly 100 WebSocket gateway instances. These nodes act as proxies that translate raw socket messages into internal message bus events without executing game rules.

### 2. In-Memory Authoritative Game Shards & Move Logging
* **Decision:** Keep active match states entirely in-memory within isolated game server shards, appending actions instantly to a high-speed Redis list residing in RAM.
* **Explanation:** With short match durations (30 to 90 seconds) and high-frequency move updates, relying on a persistent database for active state is unviable. RAM operations take fractions of a millisecond, ensuring zero noticeable lag or blocking during move validation while completely eliminating remote database lookup penalties.

### 3. Instant Replay Recovery 
* **Decision:** Utilize board status taked in each move stored in memory rather than periodic time-based snapshots.
* **Explanation:** Because an entire 30-to-90-second match generates only 30 to 90 individual move records, Redis stores these tiny text strings effortlessly. If a server crashes, replaying a 90-move list takes less than 2 milliseconds, making complex snapshot intervals entirely redundant.

### 4.  20 Second Short TTL Grace Period & Crash Recovery
* **Decision:** Implement a tight  20 second Redis-backed TTL grace period alongside Redis AOF (Append-Only File) persistence.
* **Explanation:** For ultra-quick matches, a long grace period freezes opponents for too long. A 20-second window preserves disconnected player data briefly for instant reconnections without stalling the gameplay loop, while background disk persistence (AOF) ensures active match data survives unexpected server reboots.

### 5. Asynchronous Background Batching
* **Decision:** Decouple disk persistence from the active gameplay path using an asynchronous background worker.
* **Explanation:** A separate background worker periodically flushes accumulated move logs to disk in batches, completely removing disk I/O bottlenecks from the main game loop.

## Refactored High-Scale Multiplayer & Spectator Architecture Design
```text
                     +-------------------------------------------------+
                     |                 Global Clients                  |
                     +--------+-------------------------------+--------+
                              | (WSS / Active)                | (SSE / Spectators)
                              v                               v
                     +-------------------------------------------------+
                     |              Anycast Edge / CDN / LB            |
                     +--------+-------------------------------+--------+
                              |                               |
                              v                               v
                     +------------------+           +------------------+
                     | WebSocket Gateways|          |   SSE Gateways   |
                     |  (Active Players)|           |  (Spectators)    |
                     +--------+---------+           +--------+---------+
                              |                               |
                              +---------------+---------------+
                                              |
                                              v
                     +-------------------------------------------------+
                     |             Redis Distributed Bus               |
                     |         (Matchmaking Q & Shard Routing)         |
                     +--------+-------------------------------+--------+
                              |                               |
                              v                               v
                     +------------------+           +------------------+
                     |    Matchmaker    |           |  Game Allocator  |
                     | (Skill / Latency)|           | (Shard Selector) |
                     +------------------+           +--------+---------+
                                                             |
                                                             v
                     +-------------------------------------------------+
                     |          In-Memory Game Server Shards           |
                     |    (Authoritative Logic, RAM Move Logs, TTL)    |
                     +--------+-------------------------------+--------+
                              |                               |
                   (Asynchronous AOF Flush)         (Publish Match Events)
                              |                               |
                              v                               v
                     +------------------+           +------------------+
                     |   Background     |           |  NATS JetStream  |
                     |   Disk Worker    |           | (Event Broker &  |
                     +------------------+           |  Replay Buffer)  |
                                                    +--------+---------+
                                                             |
                                                    (500ms Batch Worker)
                                                             |
                                                             v
                                                    +------------------+
                                                    |  CDN Edge Cache  |
                                                    |   (Edge KV / KV) |
                                                    +------------------+
```
# Key Architectural Decisions & Explanations

## 1. Dual-Protocol Edge Gateways (WebSockets vs. SSE)
* **Decision:** Decouple connection management by splitting traffic into dedicated WebSocket Gateways for active players and SSE Gateways/CDN Caches for spectators.
* **Explanation:** Active players require full-duplex, low-latency communication for real-time move validation. Spectators are strictly read-only consumers; routing them through SSE over HTTP/2 eliminates connection state overhead and offloads 99% of the read fan-out to global CDN edge nodes.

---

## 2. In-Memory Authoritative Shards & RAM Move Logging
* **Decision:** Keep active match states entirely in-memory within isolated game server shards, appending actions instantly to high-speed Redis RAM lists.
* **Explanation:** Short match durations (30 to 90 seconds) generate only 30 to 90 individual move records. RAM operations take fractions of a millisecond, completely eliminating remote database lookup penalties and preventing lag during move validation.

---

## 3. NATS JetStream Event Broker & 500ms Spectator Throttling
* **Decision:** Offload spectator match event distribution from core game shards to NATS JetStream, applying a 500ms batching window before pushing updates to the CDN.
* **Explanation:** Pushing micro-events instantly to thousands of observers saturates network interfaces. Batching updates every 500ms reduces message volume by up to 90% while providing a smooth viewing experience. Furthermore, NATS JetStream maintains a rolling history log, allowing late-joining spectators to instantly sync state without touching primary databases.

---

## 4. 20-Second Short TTL Grace Period & AOF Persistence
* **Decision:** Implement a tight 20-second Redis-backed TTL grace period alongside asynchronous Append-Only File (AOF) disk flushing.
* **Explanation:** For ultra-quick matches, long grace periods freeze opponents unnecessarily. A 20-second window preserves disconnected player data briefly for instant reconnections without stalling the gameplay loop, while background disk persistence ensures match data survives unexpected node reboots.

---

## 5. Sharded SQL Persistence & Edge JWT Validation
* **Decision:** Store long-term player accounts and profiles for 100M registered users in a horizontally sharded SQL database (e.g., CockroachDB) and validate sessions using stateless Edge JWTs.
* **Explanation:** Core identity and progression data require robust transactional safety. Validating JSON Web Tokens at the edge gateway prevents authentication spikes from hitting or overwhelming primary game servers during peak concurrency.