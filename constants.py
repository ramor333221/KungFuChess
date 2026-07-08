# constants.py

# גודל משבצת בפיקסלים על המסך
CELL_SIZE = 100

# הגדרות זמן תנועה (במילישניות)
MOVEMENT_DURATION_MS = 1000

# הגדרות תקינות עבור כלי השחמט
VALID_COLORS = {"w", "b"}
VALID_PIECES = {"K", "Q", "R", "B", "N", "P"}

# הגדרת משבצת ריקה במטריצה
EMPTY_CELL = "."

# כותרות לזיהוי חלקי קלט (Parsing Headers)
BOARD_HEADER = "Board:"
COMMANDS_HEADER = "Commands:"