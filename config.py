import os
from decimal import Decimal
from dotenv import load_dotenv

load_dotenv()

# ============================================================
# THUNDER CASINO CONFIG
# ============================================================

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
DATABASE_URL = os.getenv("DATABASE_URL")
LTC_XPUB = os.getenv("LTC_XPUB")
OWNER_ID = int(os.getenv("OWNER_ID", "0"))

PREFIX = os.getenv("PREFIX", ".")

# ------------------------------------------------------------
# CURRENCY
# ------------------------------------------------------------

# $0.01 = 2 points
POINTS_PER_CENT = Decimal("2")

# Therefore:
# $1 = 200 points
POINTS_PER_USD = Decimal("200")

# ------------------------------------------------------------
# LTC WATCHER
# ------------------------------------------------------------

LTC_CHECK_INTERVAL = 30
LTC_REQUIRED_CONFIRMATIONS = 1

# ------------------------------------------------------------
# GAME SETTINGS
# ------------------------------------------------------------

# Coinflip
COINFLIP_MULTIPLIER = Decimal("1.92")

# Blackjack
BLACKJACK_MULTIPLIER = Decimal("1.92")

# Prevent ridiculous bets
MIN_BET = 1
MAX_BET = 10_000_000

# ------------------------------------------------------------
# FILES
# ------------------------------------------------------------

CARD_FOLDER = "cards"

# ------------------------------------------------------------
# COLORS
# ------------------------------------------------------------

EMBED_DEFAULT = 0x2B2023
EMBED_WIN = 0x2ECC71
EMBED_LOSS = 0xE74C3C
EMBED_NEUTRAL = 0x808080
