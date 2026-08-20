from PIL import Image, ImageDraw, ImageFont
import os

from config import CARD_FOLDER


# ============================================================
# CARD SYSTEM
# ============================================================

SUITS = [
    "hearts",
    "diamonds",
    "clubs",
    "spades",
]

RANKS = [
    "ace",
    "2",
    "3",
    "4",
    "5",
    "6",
    "7",
    "8",
    "9",
    "10",
    "jack",
    "queen",
    "king",
]


def card_path(card):
    return os.path.join(
        CARD_FOLDER,
        f"{card}.png"
    )


def load_card(card):
    path = card_path(card)

    if not os.path.exists(path):
        raise FileNotFoundError(
            f"Missing card image: {path}"
        )

    return Image.open(path).convert("RGBA")


def create_deck():

    return [
        f"{rank}_of_{suit}"
        for suit in SUITS
        for rank in RANKS
    ]


# ============================================================
# COINFLIP IMAGE
# ============================================================

def create_coinflip_image(result):
    """
    Creates a simple Thunder Casino coinflip image.

    result must be:
        heads
        tails
    """

    width = 1200
    height = 500

    # Purple casino-style background
    image = Image.new(
        "RGB",
        (width, height),
        (40, 25, 60)
    )

    draw = ImageDraw.Draw(image)

    # Try a common system font.
    # If unavailable Pillow uses its default font.
    try:
        title_font = ImageFont.truetype(
            "arial.ttf",
            64
        )

        result_font = ImageFont.truetype(
            "arial.ttf",
            100
        )

    except Exception:

        title_font = ImageFont.load_default()
        result_font = ImageFont.load_default()

    # --------------------------------------------------------
    # Title
    # --------------------------------------------------------

    draw.text(
        (width // 2, 60),
        "THUNDER CASINO",
        fill="white",
        anchor="mm",
        font=title_font
    )

    # --------------------------------------------------------
    # Coin
    # --------------------------------------------------------

    coin_x = width // 2
    coin_y = height // 2 + 20

    radius = 150

    draw.ellipse(
        (
            coin_x - radius,
            coin_y - radius,
            coin_x + radius,
            coin_y + radius,
        ),
        fill=(150, 95, 220),
        outline=(220, 180, 255),
        width=8,
    )

    # --------------------------------------------------------
    # Coin result
    # --------------------------------------------------------

    result_text = result.upper()

    draw.text(
        (coin_x, coin_y),
        result_text,
        fill="white",
        anchor="mm",
        font=result_font
    )

    return image


def save_image(image, filename):

    os.makedirs(
        "generated",
        exist_ok=True
    )

    path = os.path.join(
        "generated",
        filename
    )

    image.save(path)

    return path


# ============================================================
# BLACKJACK IMAGE
# ============================================================

def create_blackjack_image(
    player_cards,
    dealer_cards,
    dealer_hidden=True
):

    dealer_images = []

    for index, card in enumerate(dealer_cards):

        if index == 0 and dealer_hidden:

            dealer_images.append(
                Image.new(
                    "RGBA",
                    (250, 350),
                    (40, 40, 40, 255)
                )
            )

        else:

            dealer_images.append(
                load_card(card)
            )

    player_images = [
        load_card(card)
        for card in player_cards
    ]

    dealer_width = sum(
        image.width
        for image in dealer_images
    )

    player_width = sum(
        image.width
        for image in player_images
    )

    width = max(
        dealer_width,
        player_width,
        900
    )

    height = 800

    canvas = Image.new(
        "RGB",
        (width, height),
        (35, 35, 35)
    )

    draw = ImageDraw.Draw(canvas)

    draw.text(
        (width // 2, 40),
        "DEALER",
        fill="white",
        anchor="mm"
    )

    x = (width - dealer_width) // 2

    for image in dealer_images:

        canvas.paste(
            image,
            (x, 80),
            image
        )

        x += image.width

    draw.text(
        (width // 2, 450),
        "PLAYER",
        fill="white",
        anchor="mm"
    )

    x = (width - player_width) // 2

    for image in player_images:

        canvas.paste(
            image,
            (x, 490),
            image
        )

        x += image.width

    return canvas
