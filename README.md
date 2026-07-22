# Architecture

ChessCTD follows a layered architecture that separates responsibilities into independent modules. This design improves maintainability, readability, scalability, and testability.

```
                +----------------------+
                |      GUI / Client    |
                +----------+-----------+
                           |
                           v
                +----------------------+
                |   Application Layer  |
                +----------+-----------+
                           |
                           v
                +----------------------+
                |     Core Engine      |
                +----------+-----------+
                           |
                           v
                +----------------------+
                |      Data Layer      |
                +----------------------+
```

---

# Layer Responsibilities

## GUI Layer (`src/GUI`)

Responsible for all user interactions.

Responsibilities:

- Display the chess board
- Handle mouse and keyboard input
- Render animations
- Show menus and dialogs
- Display game status

This layer never contains chess rules. It only presents information to the player.

---

## Application Layer (`src/application`)

Acts as the bridge between the user interface and the chess engine.

Responsibilities:

- User authentication
- Client-server communication
- Matchmaking
- Game session management
- Request routing
- Socket communication

This layer coordinates the application but does not implement chess logic.

---

## Core Layer (`src/core`)

The heart of the application.

Responsibilities:

- Chess rules
- Move validation
- Check detection
- Checkmate and stalemate detection
- Game state management
- Controllers
- Validators
- Utility functions

The core layer is completely independent from the GUI and networking, making it reusable and easy to test.

---

## Data Layer (`DB`)

Responsible for persistent storage.

Responsibilities:

- User accounts
- Match history
- Player statistics
- Database queries
- SQLite connection management

The rest of the application communicates with the database only through this layer.

---

# Models

The `src/models` package defines the application's domain objects.

Examples include:

- Board state
- Game status
- Interfaces
- Shared data models

These classes are shared across multiple layers while remaining independent of the user interface.

---

# Networking

The networking subsystem implements a client-server architecture using TCP sockets.

Main components include:

- Game Server
- Network Client
- Matchmaker
- Engine Facade

Responsibilities:

- Establish client connections
- Synchronize game states
- Forward moves between players
- Manage active game sessions
- Handle player disconnections

---

# Design Patterns

Several software design patterns are used throughout the project.

## Observer Pattern

Used to notify different components whenever important game events occur.

Examples:

- Move notifications
- Score updates
- Sound effects
- Achievement tracking
- Logging

This allows new observers to be added without modifying the game engine.


## Publish-Subscribe (Pub/Sub)

The application uses a Publish-Subscribe architecture to decouple communication between modules. Components publish events without knowledge of their subscribers, allowing features such as GUI updates, logging, sound effects, and network synchronization to react independently to the same event. This design improves modularity, extensibility, and maintainability.

---

## Facade Pattern

The `EngineFacade` provides a simplified interface between the networking layer and the chess engine, hiding internal implementation details.

---

## Factory Pattern

The `BoardFactory` creates board instances from different input sources while encapsulating object creation logic.

---

## MVC-inspired Separation

Although not a strict MVC implementation, the project separates:

- **Model** — Board state and game data
- **View** — GUI rendering
- **Controller** — User interaction and move handling

This separation keeps presentation logic independent from game logic.

---

# Testing Strategy

Testing is organized into multiple levels.

### Unit Tests

Verify individual components such as:

- Validators
- Controllers
- Chess engine
- Utility functions

### Integration Tests

Verify collaboration between modules including:

- Authentication flow
- Match creation
- Multiplayer communication
- Observer notifications
- Complete gameplay scenarios

---

# Project Goals

The architecture was designed with the following objectives:

- Separation of concerns
- Modular design
- High cohesion
- Low coupling
- Easy maintenance
- Reusable chess engine
- Independent testing
- Scalable networking infrastructure
