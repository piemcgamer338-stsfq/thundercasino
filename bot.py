import asyncio
import os
import discord

from discord.ext import commands

from config import (
    DISCORD_TOKEN,
    DATABASE_URL,
    PREFIX,
    EMBED_DEFAULT,
    EMBED_WIN,
    EMBED_LOSS,
)

from database import Database
from ltc_watcher import LTCWatcher

from utils import (
    format_points,
)

from images import (
    create_coinflip_image,
    save_image,
)


# ============================================================
# THUNDER CASINO
# ============================================================

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(
    command_prefix=PREFIX,
    intents=intents,
    help_command=None,
)

db = Database(DATABASE_URL)

ltc_watcher = None


# ============================================================
# CURRENCY
# ============================================================

# $0.01 = 2 points
# $1.00 = 200 points

POINTS_PER_CENT = 2
POINTS_PER_USD = 200
USD_PER_POINT = 0.005


# ============================================================
# HELP COMMAND LISTS
# ============================================================

BALANCE_COMMANDS = [
    (".giveaway", "Manage and create server giveaways."),
    (".steal", "Steals custom emojis from the provided parameters and adds them to this server."),
    (".achievements", "Shows your achievements or another user's achievements."),
    (".address", "Displays basic balances and recent activity for a specified Litecoin address."),
    (".ai", "Ask Thunder Casino AI a question."),
    (".alerts", "View and manage your Litecoin price alerts interactively."),
    (".calc", "Perform calculations. Supports +, -, *, /, parentheses, etc."),
    (".calendar", "Shows a monthly calendar with your gambling streak."),
    (".clan", "View, create, or manage your clan and inspect others."),
    (".crypto", "Displays top 6 cryptos with live price, 7-day graph, and stats."),
    (".games", "Shows all commands in the games category."),
    (".guide", "Learn how to use Thunder Casino."),
    (".help", "All commands of the bot."),
    (".image", "Generate an image from a prompt."),
    (".leaderboard", "Show top 10 gamblers."),
    (".litecoin", "View Litecoin/USDT chart for various time ranges."),
    (".meme", "Reply to a message to meme it into an image."),
    (".multiplayer", "View all available multiplayer games."),
    (".payment", "Check a payment order."),
    (".ping", "Responds with a Pong! message and system health metrics."),
    (".poll", "Create a real-time Yes/No poll."),
    (".privacy", "Toggle your account privacy settings."),
    (".provablyfair", "Check game fairness or verify a game's outcome."),
    (".quote", "Quote a message as an image."),
    (".race", "View the week wager race leaderboard."),
    (".rank", "Displays a user's gambling rank and progress. Allows claiming eligible rank roles and one-time rewards."),
    (".ranks", "View all the ranks that exist along with their reward."),
    (".report", "Report a message by replying to it or providing its ID/link."),
    (".season", "View the dynamic clan season progress and leaderboard."),
    (".seed", "Change your provably fair client seed."),
    (".sms", "Purchase temporary phone numbers for SMS verification."),
    (".specialrace", "Displays the Special Race Leaderboard."),
    (".stats", "View your stats or other user stats."),
    (".thread", "Manage private threads and members."),
    (".worldtime", "Shows the current time in major parts of the world."),
]


UTILITY_COMMANDS = [
    (".affiliates", "View your affiliate status or join using someone's code."),
    (".balance", "Check your current points and their equivalent in LTC and USD."),
    (".code", "Claim a promotional code to earn points."),
    (".daily", "Claim your daily free points reward. You can claim it once every 24 hours."),
    (".deposit", "Deposit Litecoin seamlessly into your account."),
    (".monthly", "Shows your monthly bonus info."),
    (".rain", "Initiate a rain of points for active users in the channel."),
    (".rainwheel", "Initiate a rain wheel lobby where one lucky winner takes the entire jackpot!"),
    (".rakeback", "Shows your rakeback info."),
    (".splitorsteal", "Initiate a split or steal lobby where two random users face off for the pot!"),
    (".tip", "Tip another user an amount of points."),
    (".vault", "Access your secure cold storage vault."),
    (".vip", "Check your or another user's VIP progress."),
    (".weekly", "Shows your weekly bonus info."),
    (".withdraw", "Withdraws Litecoin safely from Thunder Casino. Minimum: 20 points."),
    (".withdrawold", "Withdraws Litecoin to a specified address. Minimum: 20 points."),
    (".withdrawsol", "Withdraws Solana to a specified address. Minimum: 20 points."),
    (".price", "Check the equivalent of points in LTC and USD, or convert a number to different currencies."),
]


GAME_COMMANDS = [
    (
        ".cf / .coinflip",
        "`.cf <amount> <heads/tails>`\n"
        "Choose Heads or Tails and bet your points.\n"
        "One provably-fair roll decides the result.\n"
        "Winner receives 1.92× the bet."
    ),

    (
        ".bj / .blackjack",
        "`.bj <amount> [21+3] [perfect pair]`\n"
        "Play Blackjack with optional side bets."
    ),

    (
        ".mines",
        "`.mines <amount>`\n"
        "Reveal safe tiles and cash out before hitting a mine."
    ),

    (
        ".horse",
        "`.horse <amount>`\n"
        "Choose one of four horses and watch the race."
    ),

    (
        ".limbo",
        "`.limbo <amount> <target>`\n"
        "Set a target multiplier and try to beat it."
    ),

    (
        ".bjdice",
        "`.bjdice <amount>`\n"
        "Roll as close to 21 as possible without going over."
    ),

    (
        ".ward",
        "`.ward <amount>`\n"
        "You and the bot roll a die. Higher roll wins."
    ),
]


# ============================================================
# HELP EMBED
# ============================================================

async def build_main_help():

    try:
        total_users = await get_total_users()
    except Exception:
        total_users = 0

    total_commands = (
        len(BALANCE_COMMANDS)
        + len(UTILITY_COMMANDS)
        + len(GAME_COMMANDS)
    )

    return discord.Embed(
        title="Help Command - Main Menu",
        description=(
            "Welcome to **Thunder Casino**, the best Discord "
            "Litecoin Casino Bot.\n\n"
            "💡 New here? Read `.guide`\n\n"
            "**Rate:** $0.01 = 2 points\n"
            f"**Total Commands:** {total_commands}\n"
            f"**Total Users:** {total_users}\n\n"
            "Bot made by <@1519015243710201927>"
        ),
        color=EMBED_DEFAULT,
    )


# ============================================================
# CATEGORY EMBEDS
# ============================================================

def build_games_embed():

    embed = discord.Embed(
        title="Games",
        description=(
            "All available Thunder Casino games.\n\n"
            "Choose another category using the menu below."
        ),
        color=EMBED_DEFAULT,
    )

    for command, description in GAME_COMMANDS:

        embed.add_field(
            name=command,
            value=description,
            inline=False,
        )

    embed.set_footer(
        text="Thunder Casino • Games"
    )

    return embed


def build_utility_embed():

    embed = discord.Embed(
        title="Utility",
        description=(
            "Utility and account commands.\n\n"
            "Choose another category using the menu below."
        ),
        color=EMBED_DEFAULT,
    )

    for command, description in UTILITY_COMMANDS:

        embed.add_field(
            name=command,
            value=description,
            inline=False,
        )

    embed.set_footer(
        text="Thunder Casino • Utility"
    )

    return embed


def build_balance_embed():

    embed = discord.Embed(
        title="Balance",
        description=(
            "Balance, information and miscellaneous commands.\n\n"
            "Choose another category using the menu below."
        ),
        color=EMBED_DEFAULT,
    )

    for command, description in BALANCE_COMMANDS:

        embed.add_field(
            name=command,
            value=description,
            inline=False,
        )

    embed.set_footer(
        text="Thunder Casino • Balance"
    )

    return embed


# ============================================================
# HELP SELECT MENU
# ============================================================

class HelpSelect(discord.ui.Select):

    def __init__(self):

        super().__init__(
            placeholder="Select a category...",
            min_values=1,
            max_values=1,
            options=[
                discord.SelectOption(
                    label="Games",
                    value="games",
                    description="View all Thunder Casino games.",
                ),
                discord.SelectOption(
                    label="Utility",
                    value="utility",
                    description="View all utility commands.",
                ),
                discord.SelectOption(
                    label="Balance",
                    value="balance",
                    description="View balance and information commands.",
                ),
            ],
        )

    async def callback(self, interaction: discord.Interaction):

        selected = self.values[0]

        if selected == "games":

            embed = build_games_embed()

        elif selected == "utility":

            embed = build_utility_embed()

        elif selected == "balance":

            # IMPORTANT:
            # Explicit Balance handler.
            # This edits the SAME help message.

            embed = build_balance_embed()

        else:

            embed = await build_main_help()

        await interaction.response.edit_message(
            embed=embed,
            view=self.view,
        )


# ============================================================
# HELP VIEW
# ============================================================

class HelpView(discord.ui.View):

    def __init__(self):

        super().__init__(
            timeout=300
        )

        self.select_menu = HelpSelect()

        self.add_item(
            self.select_menu
        )


# ============================================================
# HELP COMMAND
# ============================================================

@bot.command(
    name="help"
)
async def help_command(ctx):

    embed = await build_main_help()

    await ctx.send(
        embed=embed,
        view=HelpView(),
    )


# ============================================================
# TOTAL USERS
# ============================================================

async def get_total_users():

    if db.pool is None:

        return 0

    try:

        async with db.pool.acquire() as conn:

            result = await conn.fetchval(
                "SELECT COUNT(*) FROM users"
            )

            return result or 0

    except Exception as error:

        print(
            f"[HELP] User count error: {error}"
        )

        return 0


# ============================================================
# BALANCE COMMAND
# ============================================================

@bot.command(
    name="balance",
    aliases=[
        "bal",
        "b",
    ],
)
async def balance_command(ctx):

    balance = await db.get_balance(
        ctx.author.id
    )

    # 200 points = $1
    usd_value = float(balance) / POINTS_PER_USD

    embed = discord.Embed(
        description=(
            f"## **{ctx.author.display_name}'s Wallet**\n\n"
            f"**Balance:** ${usd_value:.2f}"
        ),
        color=EMBED_DEFAULT,
    )

    await ctx.send(
        embed=embed
    )


# ============================================================
# COINFLIP
# ============================================================

COINFLIP_MULTIPLIER = 1.92


def make_coinflip_result():

    # Cryptographically secure random byte.
    random_byte = os.urandom(1)[0]

    roll = (
        random_byte / 255
    ) * 100

    if roll < 50:

        return "heads", roll

    return "tails", roll


@bot.command(
    name="coinflip",
    aliases=[
        "cf",
    ],
)
async def coinflip_command(
    ctx,
    amount: int = None,
    choice: str = None,
):

    # --------------------------------------------------------
    # COINFLIP INSTRUCTIONS
    # --------------------------------------------------------

    if amount is None:

        embed = discord.Embed(
            title="How to play Coinflip",
            description=(
                "`.cf <amount> <color>` — pick **Tails** "
                "or **Heads** and bet.\n\n"
                "One provably-fair roll (0–100) decides it:\n"
                "**Heads < 50**\n"
                "**Tails ≥ 50**\n\n"
                "Winner takes **1.92× the bet**."
            ),
            color=EMBED_DEFAULT,
        )

        await ctx.send(
            embed=embed
        )

        return

    # --------------------------------------------------------
    # BET VALIDATION
    # --------------------------------------------------------

    if amount <= 0:

        await ctx.send(
            "❌ Your bet must be greater than 0 points."
        )

        return

    # --------------------------------------------------------
    # CHOICE
    # --------------------------------------------------------

    if choice is None:

        # If no side was supplied, randomly choose one.
        random_side = os.urandom(1)[0] % 2

        if random_side == 0:

            player_choice = "heads"

        else:

            player_choice = "tails"

    else:

        choice = choice.lower()

        if choice in (
            "h",
            "head",
            "heads",
        ):

            player_choice = "heads"

        elif choice in (
            "t",
            "tail",
            "tails",
        ):

            player_choice = "tails"

        else:

            await ctx.send(
                "❌ Choose **Heads** or **Tails**.\n"
                "Example: `.cf 100 h`"
            )

            return

    # --------------------------------------------------------
    # BALANCE
    # --------------------------------------------------------

    balance = await db.get_balance(
        ctx.author.id
    )

    if float(balance) < amount:

        await ctx.send(
            f"❌ You don't have enough points.\n"
            f"Balance: **{format_points(balance)} points**"
        )

        return

    # --------------------------------------------------------
    # RESULT
    # --------------------------------------------------------

    result, roll = make_coinflip_result()

    won = (
        player_choice == result
    )

    # --------------------------------------------------------
    # REMOVE BET
    # --------------------------------------------------------

    try:

        await db.remove_balance(
            ctx.author.id,
            amount,
        )

    except AttributeError:

        # Compatibility fallback if the database uses
        # update_balance instead of remove_balance.

        await db.add_balance(
            ctx.author.id,
            -amount,
        )

    # --------------------------------------------------------
    # PAYOUT
    # --------------------------------------------------------

    payout = 0

    if won:

        payout = round(
            amount * COINFLIP_MULTIPLIER
        )

        await db.add_balance(
            ctx.author.id,
            payout,
        )

        result_message = (
            f"**You won — {format_points(payout)} points**"
        )

        embed_color = EMBED_WIN

    else:

        result_message = (
            "**Bot wins — better luck next flip.**"
        )

        embed_color = EMBED_LOSS

    # --------------------------------------------------------
    # IMAGE
    # --------------------------------------------------------

    image = create_coinflip_image(
        result
    )

    filename = (
        f"coinflip_{ctx.author.id}_{ctx.message.id}.png"
    )

    image_path = save_image(
        image,
        filename
    )

    file = discord.File(
        image_path,
        filename="coinflip.png",
    )

    # --------------------------------------------------------
    # DISPLAY VALUES
    # --------------------------------------------------------

    player_display = (
        "Heads"
        if player_choice == "heads"
        else "Tails"
    )

    bot_display = (
        "Tails"
        if player_choice == "heads"
        else "Heads"
    )

    result_display = (
        "Heads"
        if result == "heads"
        else "Tails"
    )

    # --------------------------------------------------------
    # RESULT EMBED
    # --------------------------------------------------------

    embed = discord.Embed(
        title="Coinflip",
        description=(
            f"**Bet:** {format_points(amount)} points\n\n"
            f"**{ctx.author.display_name}:** {player_display}\n"
            f"**Bot:** {bot_display}\n\n"
            f"{result_message}"
        ),
        color=embed_color,
    )

    embed.set_image(
        url="attachment://coinflip.png"
    )

    embed.add_field(
        name="Result",
        value=(
            f"**{result_display}**\n"
            f"Roll: **{roll:.2f}**"
        ),
        inline=False,
    )

    embed.add_field(
        name="Provably Fair",
        value=(
            "This game uses a fresh random result for every flip."
        ),
        inline=False,
    )

    embed.set_footer(
        text="Thunder Casino • Coinflip"
    )

    await ctx.send(
        embed=embed,
        file=file,
    )

    # --------------------------------------------------------
    # DELETE GENERATED IMAGE
    # --------------------------------------------------------

    try:

        os.remove(
            image_path
        )

    except Exception:

        pass


# ============================================================
# ADD BALANCE
# ============================================================

@bot.command(
    name="add"
)
@commands.is_owner()
async def add_balance_command(
    ctx,
    member: discord.Member,
    amount: float,
):

    if amount <= 0:

        await ctx.send(
            "❌ Amount must be greater than 0."
        )

        return

    await db.add_balance(
        member.id,
        amount,
    )

    new_balance = await db.get_balance(
        member.id
    )

    embed = discord.Embed(
        title="Balance Updated",
        description=(
            f"{member.mention} received "
            f"**{format_points(amount)} points**."
        ),
        color=EMBED_WIN,
    )

    embed.add_field(
        name="New Balance",
        value=(
            f"**{format_points(new_balance)} points**"
        ),
        inline=False,
    )

    await ctx.send(
        embed=embed
    )


# ============================================================
# READY
# ============================================================

@bot.event
async def on_ready():

    global ltc_watcher

    print("=" * 60)
    print("THUNDER CASINO")
    print("=" * 60)

    print(
        f"Logged in as: {bot.user}"
    )

    print(
        f"Bot ID: {bot.user.id}"
    )

    print(
        f"Prefix: {PREFIX}"
    )

    # --------------------------------------------------------
    # DATABASE
    # --------------------------------------------------------

    if db.pool is None:

        await db.connect()

        print(
            "[DATABASE] PostgreSQL connected."
        )

    # --------------------------------------------------------
    # LTC WATCHER
    # --------------------------------------------------------

    if ltc_watcher is None:

        ltc_watcher = LTCWatcher(
            bot,
            db,
        )

        asyncio.create_task(
            ltc_watcher.start()
        )

        print(
            "[LTC] Watcher started."
        )

    print("=" * 60)


# ============================================================
# ERROR HANDLER
# ============================================================

@bot.event
async def on_command_error(
    ctx,
    error,
):

    if isinstance(
        error,
        commands.CommandNotFound
    ):

        return

    if isinstance(
        error,
        commands.MissingRequiredArgument
    ):

        await ctx.send(
            f"❌ Missing argument: `{error.param.name}`"
        )

        return

    if isinstance(
        error,
        commands.BadArgument
    ):

        await ctx.send(
            "❌ Invalid argument. Check the command format."
        )

        return

    if isinstance(
        error,
        commands.NotOwner
    ):

        await ctx.send(
            "❌ You don't have permission to use this command."
        )

        return

    print(
        f"[COMMAND ERROR] {ctx.command}: {error}"
    )


# ============================================================
# START
# ============================================================

if not DISCORD_TOKEN:

    raise RuntimeError(
        "DISCORD_TOKEN is missing."
    )

bot.run(
    DISCORD_TOKEN
)
