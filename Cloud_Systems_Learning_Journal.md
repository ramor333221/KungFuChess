# Cloud Systems Learning Journal

**Course / Project:** Cloud Architecture & Distributed Systems  

---

## Introduction
This document tracks the progressive learning, architectural design decisions, and technical understandings developed throughout the exploration of cloud systems, containerization, orchestration, and database management.

---

## Table of Concepts & Understandings

## Docker & Containerization: Core Summary

Docker standardizes software deployment by packaging code, dependencies, and system tools into isolated, portable units. 

### Key Concepts Breakdown
* **Blueprints & Runtime:** A **Docker Image** acts as a read-only template, which is instantiated into a running, isolated **Container** based on instructions defined in a **Dockerfile**.
* **Multi-Container Management:** **Docker Compose** coordinates complex systems with multiple interacting services using a single YAML file.
* **Support Systems:** 
  * **Volumes:** Ensure data persistence past container lifecycles.
  * **Networks:** Provide secure isolation and communication pathways between containers.
  * **Registries (Docker Hub):** Serve as repositories for pre-built images.
  * **Environment Variables:** Allow flexible, secure configuration at runtime.

---

### Architecture Diagram
```text
                        [ Docker Compose ]
                               │
       ┌───────────────────────┴───────────────────────┐
       ▼                                               ▼
┌──────────────┐                               ┌──────────────┐
| Web Container| <──(Docker Network: chess-net)─> | DB Container |
└──────────────┘                               └──────┬───────┘
                                                      │
                                                      ▼
                                              [ Docker Volume ]
                                              (Persistent Data)
```                                             
                                                                                 
                                              
## Kubernetes & Orchestration: Core Summary

Kubernetes (K8s) automates the deployment, scaling, and management of containerized applications across a cluster of physical or virtual machines.

### Key Concepts Breakdown
* **Cluster Management & Scheduling:** Groups multiple nodes into a unified resource pool, automatically scheduling containers based on available CPU and memory.
* **Pods:** The core deployment unit; ephemeral containers wrapped with a shared network space, local communication, and managed lifecycles.
* **Health Probes:** Automated liveness and readiness checks that monitor application health, triggering automated healing and restarts.
* **Services & DNS:** Provide stable internal load balancers and static names to handle dynamic, constantly changing pod IP addresses.

---

### Architecture Diagram

```text
                     [ External Client Traffic ]
                                  │
                                  ▼
┌───────────────────────────────────────────────────────────────────┐
| Kubernetes Cluster                                                |
|                                                                   |
|   ┌────────────────────────┐         ┌────────────────────────┐   |
|   | Service (Stable DNS)   | <-----> | Pod (Ephemeral Wrapper)|   |
|   └────────────────────────┘         └────────────────────────┘   |
|               ▲                                   │               |
|               │ (Load Balancing)                  ▼               |
|   ┌───────────┴────────────┐             [ Health Probes ]        |
|   | Cluster Nodes (Nodes)  | <─────── (Automated Healing/Restarts)|
|   └────────────────────────┘                                    |
└───────────────────────────────────────────────────────────────────┘

```


## K3s & Lightweight Orchestration:

**K3s** is a fully CNCF-certified, minimal-footprint Kubernetes distribution engineered specifically to address the resource constraints of edge computing, Internet of Things (IoT) devices, and local development environments.

### Core Architectural Pillars
* **Single Binary Distribution:** Unlike standard Kubernetes which distributes control-plane and worker components across multiple binaries, K3s packages the entire execution environment into a single compact executable under 100 MB.
* **Datastore Optimization (Kine & SQLite):** Replaces the resource-heavy, distributed `etcd` key-value store with a lightweight embedded **SQLite** database. This is achieved via **Kine**, an abstraction layer shim that translates Kubernetes API server requests into standard SQL queries.
* **Batteries-Included Ecosystem:** Ships pre-bundled with essential operational tools to eliminate manual setup overhead, including `containerd` (container runtime), `Flannel` (overlay networking), `Traefik` (ingress controller), and `CoreDNS`.

---

### Trade-offs & Operational Limitations
* **Resource Efficiency vs. Scalability:** K3s runs smoothly on hardware with as little as 512 MB of RAM, but it is optimized for small-to-medium clusters (tested up to ~1,200 nodes) rather than massive enterprise data centers.
* **Single Point of Failure (SPOF):** Single-node default SQLite setups are ideal for edge/dev, but require manual configuration of external databases (like PostgreSQL, MySQL, or multi-node etcd) to achieve true high availability (HA).
* **Opinionated Defaults:** Bundled components like Traefik and Flannel streamline quick deployment, but require explicit disabling if you want to use custom networking plugins or alternative ingress controllers.

---

### Architecture Comparison Diagram

```text
Standard K8s Control Plane:
[ API Server ] <──> [ Controller Manager ] <──> [ etcd (Heavy Distributed KV) ]

                            vs.

Lightweight K3s Architecture:
[ Single Binary Process (<100MB) ] <──> [ Kine Abstraction Shim ] <──> [ Embedded SQLite ]
```



## Comprehensive PostgreSQL & Relational Architecture Summary

## Database Paradigms & PostgreSQL Summary

### 1. SQL vs. NoSQL
* **SQL (Relational):** Structured tables, strict schemas, Primary/Foreign keys, and normalization (e.g., PostgreSQL, MySQL).
* **NoSQL (Non-Relational):** Flexible data models like JSON documents or key-value pairs for rapid scaling (e.g., MongoDB, Redis).

### 2. PostgreSQL Advanced Features
* **Native JSONB:** Bridges SQL and NoSQL by supporting structured tables with flexible JSON storage and indexing.
* **Advanced Indexing:** B-Tree (default equality/range), GIN & GiST (full-text, arrays, geo-data).
* **Scaling Infrastructure:** PgBouncer (connection pooling) and Streaming Replication (high availability).

### 3. ACID Mechanics Under the Hood
* **WAL (Write-Ahead Log):** Ensures **Atomicity** (transaction rollbacks) and **Durability** (crash recovery persistence).
* **MVCC (Multi-Version Concurrency Control):** Maximizes **Isolation** by maintaining multiple row versions so readers and writers don't block each other.
---

### 4. Architecture & Mechanics Diagram

```text
┌────────────────────────────────────────────────────────────────────────┐
| PostgreSQL & Relational Architecture                                   |
|  • Schema & Integrity: [ Customers Table ] ──(Foreign Key)──> [ Orders ]|
|  • Specialized Storage: Supports rigid SQL tables + flexible JSONB     |
└────────────────────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────────────────────┐
| Performance & Concurrency Infrastructure                               |
|  • Indexing:           [ B-Tree / GIN / GiST ]                         |
|  • Scaling & Pooling:  [ PgBouncer ] ──> [ Streaming Replication ]     |
└────────────────────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────────────────────┐
| ACID Mechanics Under the Hood                                          |
|  • Durability & Atomicity:  [ Application ] ──> [ Write-Ahead Log (WAL) ]|
|  • Isolation (Concurrency): [ MVCC ] (Maintains multiple row versions) |
└────────────────────────────────────────────────────────────────────────┘
```


# Redis: Core Concepts & Architecture Summary

Redis is an ultra-fast, in-memory data store that serves as a foundational component in modern cloud and distributed architectures.

## Key Takeaways
* **Performance & Data Structures:** Operates directly in RAM for sub-millisecond response times, supporting rich data types (hashes, sets, sorted sets) far beyond basic key-values.
* **Dual Role (Cache & Bus):** Functions as a high-speed distributed cache to protect primary databases from heavy load, while doubling as a real-time message broker via Pub/Sub and Streams.
* **Advanced Capabilities:** Leverages TTL for automatic key expiration, ensures thread-safe atomic operations via Lua scripting, handles rate limiting, and powers event-driven workflows with Redis Streams.
* **High Availability & Recovery:** Balances in-memory volatility with disk persistence (RDB snapshots and AOF logs) and utilizes Redis Sentinel for automated master-replica failover to guarantee uptime.

## Redis Architecture & Concepts Diagram

```text
┌─────────────────────────────────────────────────────────────┐
|                      REDIS CORE                             |
|          (In-Memory RAM / Sub-Millisecond Speed)            |
└──────────────────────┬──────────────────────────────────────┘
                       │
       ┌───────────────┴───────────────┐
       ▼                               ▼
┌─────────────┐                 ┌─────────────┐
| Cache & DS  |                 | Message Bus |
| (RAM Store) |                 | (Pub/Sub &  |
|             |                 |   Streams)  |
└──────┬──────┘                 └──────┬──────┘
       │                               │
       ▼                               ▼
┌─────────────┐                 ┌─────────────┐
| Operations  |                 | Persistence |
| • TTL       |                 | • RDB Snap  |
| • Lua Script|                 | • AOF Logs  |
| • Rate Limit|                 └──────┬──────┘
└──────┬──────┘                        │
       │                               │
       └───────────────┬───────────────┘
                       ▼
        ┌─────────────────────────────┐
        |      High Availability      |
        |   • Master-Replica Sync     |
        |   • Redis Sentinel Failover |
        └─────────────────────────────┘
```

## Networking & Communication Protocols Summary

* **REST APIs (FastAPI):** Stateless, request-response architecture using standard HTTP methods for scalable web services.
* **WebSockets:** Stateful, full-duplex, bi-directional real-time communication channel over a single persistent TCP connection.
* **Docker Bridge Networks (`chess-net`):** Isolated virtual networks that allow secure, internal communication between containers on the same host.

---

### Architecture Diagram

```text
┌─────────────────────────────────────────────────────────────┐
|               NETWORKING & COMMUNICATION                    |
└──────────────────────────┬──────────────────────────────────┘
                           │
         ┌─────────────────┼─────────────────────────┐
         ▼                 ▼                         ▼
┌─────────────────┐ ┌─────────────┐ ┌─────────────────────────┐
|    REST APIs    | | WebSockets  | | Docker Bridge (`chess-net`)|
| (Stateless HTTP)| |(Bi-directional)| | (Secure Inter-Service) |
└─────────────────┘ └─────────────┘ └─────────────────────────┘
```