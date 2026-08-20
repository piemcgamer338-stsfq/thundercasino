from PIL import Image, ImageDraw, ImageFont
import os

from config import CARD_FOLDER


# ============================================================
# CARD SYSTEM
# ============================================================


def card_path(card):
    """
    Convert:

        queen_of_hearts

    into:

        cards/queen_of_hearts.png
    """

    return os.path.join(
        CARD_FOLDER,
        f"{card}.png"
    )


def load_card(card):
    """
    Load a card PNG.

    Example:

        load_card("queen_of_hearts")
    """

    path = card_path(card)

    if not os.path.exists(path):
        raise FileNotFoundError(
            f"Missing card image: {path}"
        )

    return Image.open(path).convert("RGBA")


# ============================================================
# CARD NAMES
# ============================================================

SUITS = [
    "hearts",
    "diamonds",
    "clubs",
    "spades"
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
    "king"
]


def create_deck():

    deck = []

    for suit in SUITS:

        for rank in RANKS:

            deck.append(
                f"{rank}_of_{suit}"
            )

    return deck


# ============================================================
# BLACKJACK IMAGE
# ============================================================


def create_blackjack_image(
    player_cards,
    dealer_cards,
    dealer_hidden=True
):

    cards = []

    # --------------------------------------------------------
    # Dealer cards
    # --------------------------------------------------------

    for index, card in enumerate(dealer_cards):

        if index == 0 and dealer_hidden:

            cards.append(
                Image.new(
                    "RGBA",
                    (250, 350),
                    (40, 40, 40, 255)
                )
            )

        else:

            cards.append(
                load_card(card)
            )

    dealer_width = sum(
        image.width for image in cards
    )

    player_images = [
        load_card(card)
        for card in player_cards
    ]

    player_width = sum(
        image.width for image in player_images
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

    # --------------------------------------------------------
    # Dealer
    # --------------------------------------------------------

    draw.text(
        (width // 2, 40),
        "DEALER",
        fill="white",
        anchor="mm"
    )

    x = (width - dealer_width) // 2

    for image in cards:

        canvas.paste(
            image,
            (x, 80),
            image
        )

        x += image.width

    # --------------------------------------------------------
    # Player
    # --------------------------------------------------------

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


# ============================================================
# SAVE IMAGE
# ============================================================


def save_image(image, filename):

    os.makedirs("generated", exist_ok=True)

    path = os.path.join(
        "generated",
        filename
    )

    image.save(path)

    return path
