import unittest

from src.application import GameServer


class TestMatchCreation(unittest.IsolatedAsyncioTestCase):
    async def test_start_new_match_creates_room(self):
        # אתחול השרת
        server = GameServer()

        # הגדרת שני שחקנים
        p1 = {"username": "Player1", "elo": 1200}
        p2 = {"username": "Player2", "elo": 1250}

        # ביצוע הפעולה
        room = await server.start_new_match(p1, p2)

        # וידוא שהחדר נוצר ושהשחקנים הוקצו
        self.assertIsNotNone(room.room_id)
        self.assertEqual(room.players["white"]["name"], "Player1")
        self.assertEqual(room.players["black"]["name"], "Player2")
        print(f"Test 5 Passed: Room {room.room_id} created successfully.")


if __name__ == "__main__":
    unittest.main()