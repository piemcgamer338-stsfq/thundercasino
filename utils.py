import hashlib
import hmac
import secrets
import string
from decimal import Decimal, ROUND_DOWN

# ============================================================
# GENERAL UTILITIES
# ============================================================


def format_points(points):
    """
    Format points nicely.

    Example:
    1000 -> 1,000
    1000000 -> 1,000,000
    """

    try:
        points = Decimal(str(points))
        return f"{points:,.2f}".rstrip("0").rstrip(".")
    except Exception:
        return str(points)


def usd_to_points(usd):
    """
    Convert USD to points.

    $0.01 = 2 points
    $1.00 = 200 points
    """

    usd = Decimal(str(usd))

    points = usd * Decimal("200")

    return points.quantize(
        Decimal("0.01"),
        rounding=ROUND_DOWN
    )


def points_to_usd(points):
    """
    Convert points back to USD.

    200 points = $1
    """

    points = Decimal(str(points))

    return (
        points / Decimal("200")
    ).quantize(
        Decimal("0.01"),
        rounding=ROUND_DOWN
    )


def random_client_seed(length=32):
    """
    Generate a random client seed.
    """

    chars = string.ascii_letters + string.digits

    return "".join(
        secrets.choice(chars)
        for _ in range(length)
    )


# ============================================================
# PROVABLY FAIR
# ============================================================


def generate_server_seed():
    """
    Generate a cryptographically secure server seed.
    """

    return secrets.token_hex(32)


def hash_server_seed(server_seed):
    """
    Hash the server seed before the game.

    The hash is shown to the player before the result.
    """

    return hashlib.sha256(
        server_seed.encode()
    ).hexdigest()


def generate_roll(server_seed, client_seed, nonce):
    """
    Generate deterministic roll from:

    server seed
    client seed
    nonce

    Returns:
        0.00 - 100.00
    """

    message = f"{client_seed}:{nonce}".encode()

    digest = hmac.new(
        server_seed.encode(),
        message,
        hashlib.sha256
    ).hexdigest()

    number = int(digest[:8], 16)

    roll = (number / 0xFFFFFFFF) * 100

    return round(roll, 2)


def random_game_id():
    """
    Generate a short game ID.
    """

    return secrets.randbelow(9000) + 1000
