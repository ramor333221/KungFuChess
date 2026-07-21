import asyncio
import time

MATCHMAKING_TIMEOUT = 60  # seconds
ELO_RANGE = 100


class Matchmaker:
    """Handles player queuing and ELO proximity matchmaking."""

    def __init__(self):
        self.seeking_players = []
        self._lock = asyncio.Lock()

    async def add_to_queue(self, player_session: dict) -> dict | None:
        async with self._lock:
            if any(p["username"] == player_session["username"] for p in self.seeking_players):
                return None
            self.seeking_players.append(player_session)

        return await self._find_opponent_loop(player_session)

    async def _find_opponent_loop(self, player: dict) -> dict | None:
        start_time = time.monotonic()

        while time.monotonic() - start_time < MATCHMAKING_TIMEOUT:
            async with self._lock:
                if player not in self.seeking_players:
                    return player.get("matched_opponent")

                opponent = self._find_candidate(player)
                if opponent:
                    self.seeking_players.remove(player)
                    self.seeking_players.remove(opponent)
                    player["matched_opponent"] = opponent
                    opponent["matched_opponent"] = player
                    return opponent

            await asyncio.sleep(1)

        async with self._lock:
            if player in self.seeking_players:
                self.seeking_players.remove(player)

        return None

    def _find_candidate(self, player: dict) -> dict | None:
        for potential in self.seeking_players:
            if potential["username"] != player["username"]:
                if abs(player["elo"] - potential["elo"]) <= ELO_RANGE:
                    return potential
        return None

    async def remove_from_queue(self, username: str):
        async with self._lock:
            self.seeking_players = [
                p for p in self.seeking_players if p["username"] != username
            ]