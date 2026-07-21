import unittest
import asyncio

from src.application import GameServer


class TestTwoPlayerMatch(unittest.IsolatedAsyncioTestCase):
    async def test_two_players_match_successfully(self):
        server = GameServer()

        # Define two distinct players
        player1 = {"username": "Alice", "elo": 1200}
        player2 = {"username": "Bob", "elo": 1210}

        # Simulate player 1 joining the queue
        task1 = asyncio.create_task(server.matchmaker.add_to_queue(player1))

        # Small delay to ensure player 1 is in the queue
        await asyncio.sleep(0.1)

        # Simulate player 2 joining the queue
        # Since their ELO difference is <= 100, they should match
        result2 = await server.matchmaker.add_to_queue(player2)
        result1 = await task1

        # Verify both players found an opponent
        self.assertIsNotNone(result1)
        self.assertIsNotNone(result2)

        # Verify they are matched with each other
        self.assertEqual(result1['username'], "Bob")
        self.assertEqual(result2['username'], "Alice")

        print("Test 6 Passed: Two players matched successfully in the queue.")


if __name__ == "__main__":
    unittest.main()