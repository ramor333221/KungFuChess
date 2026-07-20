import asyncio
from config.constants import MATCHMAKING_TIMEOUT, ELO_DIFFERENCE_THRESHOLD


class Matchmaker:
    """Manages the queue of players and handles ELO-based pairing."""

    def __init__(self):
        self.seeking_players = []

    async def add_to_queue(self, player_session):
        """Adds a player to the queue and attempts to find an opponent."""
        self.seeking_players.append(player_session)
        print(f"Player {player_session['username']} is waiting for a match...")

        opponent = await self.find_opponent(player_session)
        return opponent

    async def find_opponent(self, player):
        """Pairs players based on ELO proximity using configurable thresholds."""
        start_time = asyncio.get_event_loop().time()

        while asyncio.get_event_loop().time() - start_time < MATCHMAKING_TIMEOUT:
            for potential in self.seeking_players:
                if potential['username'] != player['username']:
                    # Use constant instead of magic number
                    if abs(player['elo'] - potential['elo']) <= ELO_DIFFERENCE_THRESHOLD:
                        self.seeking_players.remove(player)
                        self.seeking_players.remove(potential)
                        return potential
            await asyncio.sleep(2)
        return None