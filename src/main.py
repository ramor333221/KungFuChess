import os
import asyncio
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
import psycopg2
import redis
from datetime import datetime

app = FastAPI(title="ChessCTD Unified Core Server")

# Environment variables for infrastructure
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "postgres")
DB_NAME = os.getenv("DB_NAME", "chess_db")
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

# Initialize Redis client
redis_client = redis.Redis.from_url(REDIS_URL)


def get_db_connection():
    return psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME
    )


# --- Matchmaker & Game Server Components ---
class Matchmaker:
    """Manages player waiting queues for matchmaking sessions."""

    def __init__(self):
        self.waiting_players = []

    def add_player(self, websocket: WebSocket):
        self.waiting_players.append(websocket)
        if len(self.waiting_players) >= 2:
            p1 = self.waiting_players.pop(0)
            p2 = self.waiting_players.pop(0)
            return (p1, p2)
        return None


class GameServer:
    """Manages persistent WebSocket connections and game session routing."""

    def __init__(self, matchmaker: Matchmaker):
        self.matchmaker = matchmaker

    async def handle_connection(self, websocket: WebSocket):
        await websocket.accept()
        print("Player connected via WebSocket Gateway.")
        try:
            # Handle matchmaking queue placement
            pair = self.matchmaker.add_player(websocket)
            if pair:
                p1, p2 = pair
                await p1.send_text("Match found! Initializing game session...")
                await p2.send_text("Match found! Initializing game session...")
            else:
                await websocket.send_text("Added to matchmaking queue. Waiting for opponent...")

            # Real-time message/move loop
            while True:
                data = await websocket.receive_text()
                # Process player action through authoritative game engine logic here
                await websocket.send_text(f"Server received action: {data}")

        except WebSocketDisconnect:
            print("Player disconnected from WebSocket session.")


# Instantiate core architectural modules
matchmaker_instance = Matchmaker()
game_server_instance = GameServer(matchmaker_instance)


# --- API Gateway Endpoints (REST) ---
@app.get("/")
async def root():
    try:
        # Test Redis operation
        redis_client.set("last_ping", datetime.utcnow().isoformat())
        last_ping = redis_client.get("last_ping").decode("utf-8")

        # Test PostgreSQL connection and query
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT NOW();")
        db_time = cur.fetchone()[0]
        cur.close()
        conn.close()

        return {
            "status": "Running",
            "message": "ChessCTD Unified Core Server is up and running!",
            "redis_last_ping": last_ping,
            "database_time": str(db_time)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# --- WebSocket Gateway Endpoint (Live Traffic) ---
@app.websocket("/ws/game")
async def websocket_endpoint(websocket: WebSocket):
    await game_server_instance.handle_connection(websocket)