# System Architecture Design: High-Scale Multiplayer Matchmaking & Game Sharding

## first design
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

### 3. Instant Replay Recovery (No Snapshots Needed)
* **Decision:** Utilize full match move logs stored in memory rather than periodic time-based snapshots.
* **Explanation:** Because an entire 30-to-90-second match generates only 30 to 90 individual move records, Redis stores these tiny text strings effortlessly. If a server crashes, replaying a 90-move list takes less than 2 milliseconds, making complex snapshot intervals entirely redundant.

### 4.  20 Second Short TTL Grace Period & Crash Recovery
* **Decision:** Implement a tight  20 second Redis-backed TTL grace period alongside Redis AOF (Append-Only File) persistence.
* **Explanation:** For ultra-quick matches, a long grace period freezes opponents for too long. A 3-to-5-second window preserves disconnected player data briefly for instant reconnections without stalling the gameplay loop, while background disk persistence (AOF) ensures active match data survives unexpected server reboots.

### 5. Asynchronous Background Batching
* **Decision:** Decouple disk persistence from the active gameplay path using an asynchronous background worker.
* **Explanation:** A separate background worker periodically flushes accumulated move logs to disk in batches, completely removing disk I/O bottlenecks from the main game loop.

