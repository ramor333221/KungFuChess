# config/constants.py
from typing import Set

# ==========================================
# UI & Display Configurations
# ==========================================
# גודל משבצת בפיקסלים על המסך (לשימוש ה-BoardMapper וה-Controller)
CELL_SIZE: int = 100


# ==========================================
# Time & Simulation Configurations
# ==========================================
# הגדרות זמן תנועה במילישניות (לשימוש ה-GameStatusManager)
MOVEMENT_DURATION_MS: int = 1000


# ==========================================
# Chess Domain & Token Definitions
# ==========================================
# הגדרת משבצת ריקה במטריצה
EMPTY_CELL: str = "."

# הגדרות תקינות עבור כלי השחמט (לשימוש ה-InputValidator וה-RulesEngine)
VALID_COLORS: Set[str] = {"w", "b"}
VALID_PIECES: Set[str] = {"K", "Q", "R", "B", "N", "P"}


# ==========================================
# I/O & Parsing Configuration Headers
# ==========================================
# כותרות לזיהוי חלקי קלט (לשימוש ה-BoardParser)
BOARD_HEADER: str = "Board:"
COMMANDS_HEADER: str = "Commands:"