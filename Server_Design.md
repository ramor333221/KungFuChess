# Comprehensive System Architecture Document

## 1. System Components & Architecture

### API Gateway (Static Requests Entry Point)
* **Role:** Handles all non-real-time operations, such as user authentication (Login), initial room creation, and retrieving user history and data.
* **Architecture Contribution:** Protects core servers from unnecessary traffic loads and centralizes the external entry point for clients.

### WebSocket Gateway (Live Traffic & Horizontal Routing)
* **Role:** Manages persistent connections with clients, captures player actions, and broadcasts state updates. Manages a Heartbeat (Ping-Pong) mechanism to detect sudden disconnections (Half-Open Connections) and immediately free up resources.
* **Horizontal Routing:** When operating with multiple gateway instances behind a Load Balancer, each message from the authoritative server is forwarded via dedicated NATS Pub/Sub channels targeted specifically to the gateway connected to the client, ensuring precise message delivery.
* **Security:** Protected via Token / JWT authentication validated during the initial handshake and maintained within the connection context.

### Matchmaker (Player Matchmaking Module)
* **Role:** Manages player waiting queues and groups them into game sessions according to defined criteria (such as rating/rank).

### Game Allocator
* **Role:** Receives game creation approval, selects an available game server in the cluster, and maintains real-time mapping (`Room ID -> Shard IP`) in system memory.

### Game Server Shards & Authoritative Game Engine
* **Role:** The critical component running actual game logic as the absolute single source of truth.
* **Working Principle:** Clients and gateways do not determine outcomes. Every player action is processed in the server engine for anti-cheat enforcement. Additionally, Client-Side Prediction and Server Reconciliation techniques are implemented to handle network latency.

---

## 2. Tech Stack & Supporting Infrastructure

### Internal Communication & Message Reliability (NATS JetStream & Pub/Sub)
* The central messaging backbone across all microservices, ensuring at-least-once message delivery via built-in persistence, acknowledgments (ACKs), and fault-tolerant routing between game servers and WebSocket gateway instances.

### State Management & Temporary Data (Redis Cluster + Hash Tags)
* **Sessions:** Tracking gateways and active connections.
* **Active Rooms:** Room mapping and server allocation.
* **Reconnect Handling:** Temporary identifiers for fast reconnection in case of drops.
* **Matchmaking Queue:** Fast waiting queues based on in-memory data structures (Sorted Sets).
* **Hash Tags Optimization:** Utilizing key structures combining hash tags (e.g., `{room:123}:state`) to force the Redis cluster to store all data related to the exact same room on the exact same physical node, preventing cross-slot errors and speeding up data access.

### Persistent & Historical Database (PostgreSQL)
* The primary database managing 100 million registered users, profiles, game history, and precise move history sequencing. SQLite is entirely unsuitable due to being a single-file database, lacking high concurrent write capability, and facing architectural limitations at the scale of hundreds of millions of users.

### Deployment, Execution, & Orchestration (Docker Compose & Kubernetes / K3s)
* **Docker Compose:** Fast local development environment.
* **Kubernetes / K3s:** Production container management including dynamic auto-scaling, self-healing, and load management.

### Observability Layer
* **Prometheus & Grafana:** Collecting CPU, memory, and NATS traffic metrics and displaying them on live dashboards.
* **OpenTelemetry:** Distributed tracing of message paths across the system.

---

## 3. Scale, Traffic, & Concurrency Handling

### Support for 10 Million Concurrent Users
* A single server cannot handle the load. The system is deployed across hundreds of distributed Docker instances.
* Player and room mapping is handled via a high-speed Redis cluster, while the routing layer (NATS Pub/Sub + WebSocket Gateways) allows any player to play from anywhere and connect to any room in the cluster without losing synchronization.

### Network Traffic Volume Calculation
* For **10,000,000** active players where each performs an action on average every 2 seconds:
  $$\frac{10,000,000}{2} = 5,000,000 \text{ msgs/sec}$$
* Assuming an average payload of ~300 bytes per message:
  $$5,000,000 \times 300 \text{ bytes} = 1,500,000,000 \text{ bytes/sec} \approx 1.5 \text{ GB/sec } (\approx 12 \text{ Gbps})$$
* This is a massive volume requiring a fully distributed architecture to prevent network collapse or bottlenecks in individual servers.

### Short Matches (30 to 90 seconds) & Impact on Containers
* **High Churn Rate:** Rooms open, fill up, and close in the thousands every minute.
* **Game Server Shards:** Require aggressive auto-scaling within Kubernetes, rapid memory cleanup upon match completion, and efficient snapshot mechanisms to prevent latency during high-frequency new game creation.
* **Matchmaker & Game Allocator:** Operate entirely in-memory using Redis for ultra-fast matching without latency.

---

## 4. Fault Tolerance & Recovery Strategies

### Game Server Recovery Strategies (Server Failures)
* **State Snapshotting & Event Sourcing:** Instead of maintaining an expensive, resource-doubling hot standby server, the system saves periodic state snapshots along with event sequencing. In case of a crash, a new server loads the latest snapshot and restores the room state in mere seconds.

### Memory & Communication Resilience
* **Redis High Availability:** Utilizing distributed clusters, replicas, and Sentinel mechanisms combined with hash tags to prevent loss of connection states.
* **NATS Clustering:** Deployment of a distributed cluster with data replication preventing traffic stoppage during network node failures.


# Architectural Decisions & Rationale Analysis

Below is a detailed analysis and explanation of the core architectural decisions made during the system design:

## 1. Separation of Concerns: API Gateway vs. WebSocket Gateway
* **Decision:** Complete separation between static REST traffic (authentication, profile management, room creation) and real-time WebSocket traffic.
* **Explanation:** 
  * WebSocket connections require persistent connection management and consume entirely different memory and traffic resources compared to standard HTTP requests.
  * This separation prevents live session/game loads from impacting critical operations like login or data retrieval, and enables independent scaling tailored to each layer's specific load requirements.

## 2. Authoritative Game Engine & Latency Management
* **Decision:** The server acts as the absolute single source of truth running the game logic, combined with Client-Side Prediction and Server Reconciliation on the client side.
* **Explanation:**
  * **Anti-Cheat:** Because the client does not determine outcomes or actions, malicious players cannot cheat or modify the game state locally.
  * **Handling Latency:** Network latency is inevitable. Using client-side prediction alongside automatic server corrections allows the experience to feel responsive and immediate to the user while maintaining full synchronization with the central server.

## 3. Choosing PostgreSQL and Rejecting SQLite
* **Decision:** Using PostgreSQL for managing user data and profiles, alongside the complete rejection of SQLite.
* **Explanation:** 
  * A system required to support 100 million registered users needs a distributed database with high concurrent write capabilities (High Concurrency), advanced indexing, and enterprise-grade security.
  * SQLite is a single-file embedded database (Embedded DB) designed for local applications or small projects, and is utterly incapable of handling the volumes, high concurrency, and write loads of hundreds of millions of users.

## 4. Redis Cluster Optimization via Hash Tags
* **Decision:** Using a distributed Redis cluster combined with Hash Tags (e.g., `{room:123}:state`).
* **Explanation:** In a standard Redis cluster, different keys are automatically routed to different nodes in memory. Operations requiring access to multiple keys belonging to the same room can fail with cross-slot errors. Adding Hash Tags forces the cluster to store all data related to a specific room on the exact same physical node, accelerating data access and ensuring ultra-low latency.

## 5. Horizontal Routing via NATS Pub/Sub to WebSocket Gateway Instances
* **Decision:** Using dedicated NATS channels for routing messages between game servers and various WebSocket gateway instances.
* **Explanation:** When the system runs multiple gateway instances behind a Load Balancer, the authoritative server does not know which physical gateway a player is currently connected to. NATS Pub/Sub channels enable targeted message distribution so that the correct gateway receives the update and forwards it smoothly and transparently to the appropriate client.

## 6. State Snapshotting & Event Sourcing vs. Hot Standby
* **Decision:** Abandoning expensive hot standby servers in favor of periodic state snapshots and Event Sourcing.
* **Explanation:** Maintaining an active, resource-doubling hot standby server for every active room inefficiently doubles computing costs (CPU and memory). Storing periodic snapshots alongside an event sequence log allows a new server to load the latest state and restore the room within seconds in the event of a crash, achieving massive infrastructure resource savings.

## 7. Distributed Architecture Planning Due to Massive Traffic & High Churn Rate
* **Explanation based on scale metrics:**
  * **Network Load:** Traffic calculation for 10 million players performing an action every 2 seconds yields a massive volume of ~1.5 GB/s (~12 Gbps). Such a volume would cause an individual server to collapse and strictly requires full horizontal distribution.
  * **Short Match Lifecycle (30 to 90 seconds):** Creates a very high churn rate of opening and closing rooms in the thousands every minute. Therefore, aggressive auto-scaling mechanisms within Kubernetes and fast in-memory components (like Redis and memory-based Matchmakers) are required to prevent bottlenecks and immediately release resources.