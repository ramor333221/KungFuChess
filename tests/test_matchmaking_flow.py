import os
import sys
import unittest
from unittest.mock import AsyncMock
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from application.sockets.game_server import GameServer


class TestMatchmakingFlow(unittest.IsolatedAsyncioTestCase):
    async def test_play_request_triggers_match(self):
        # אתחול השרת
        server = GameServer()

        # יצירת Mock עבור ה-WebSocket ושחקן בדיקה
        mock_ws = AsyncMock()
        player_session = {"username": "TestPlayer", "elo": 1200}

        # הדמיית בקשת משחק
        # כאן אנחנו בודקים את הלוגיקה של ה-GameServer
        result = await server.matchmaker.add_to_queue(player_session)

        # בבדיקה זו נוודא שהשחקן נוסף לתור
        assert player_session in server.matchmaker.seeking_players
        print("Test 5 Passed: Matchmaking request successfully added to queue.")


if __name__ == "__main__":
    unittest.main()