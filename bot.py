import asyncio
import discord

from discord.ext import commands

from config import (
    DISCORD_TOKEN,
    DATABASE_URL,
    PREFIX,
    EMBED_DEFAULT,
    EMBED_WIN,
)

from database import Database
from ltc_watcher import LTCWatcher

from utils import format_points


# ============================================================
# THUNDER CASINO BOT
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
# HELP COMMAND DATA
# ============================================================

BALANCE_COMMANDS = [
    (".giveaway", "Manage and create server giveaways."),
    (".steal", "Steals custom emojis from the provided parameters and adds them to this server."),
    (".achievements", "Shows your achievements or another user's achievements."),
    (".address", "Displays basic balances and recent activity for a specified Litecoin address."),
    (".ai", "Ask BetRush AI a question."),
    (".alerts", "View and manage your Litecoin price alerts interactively."),
    (".calc", "Perform calculations. Supports +, -, *, /, parentheses, etc."),
    (".calendar", "Shows a monthly calendar with your gambling streak."),
    (".clan", "View, create, or manage your clan and inspect others."),
    (".crypto", "Displays top 6 cryptos with live price, 7-day graph, and stats."),
    (".games", "Shows all commands in the games category."),
    (".guide", "Learn how to use the bot."),
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
    (".deposit", "Deposit cryptocurrency seamlessly into your account."),
    (".monthly", "Shows your monthly bonus info."),
    (".rain", "Initiate a rain of points for active users in the channel."),
    (".rainwheel", "Initiate a rain wheel lobby where one lucky winner takes the entire jackpot!"),
    (".rakeback", "Shows your rakeback info."),
    (".splitorsteal", "Initiate a split or steal lobby where two random users face off for the pot!"),
    (".tip", "Tip another user an amount of points."),
    (".vault", "Access your secure cold storage vault."),
    (".vip", "Check your or another user's VIP progress."),
    (".weekly", "Shows your weekly bonus info."),
    (".withdraw", "Withdraws cryptocurrency safely from BetRush. Minimum: 20 points."),
    (".withdrawold", "Withdraws Litecoin to a specified address for BetRush. Minimum: 20 points."),
    (".withdrawsol", "Withdraws Solana to a specified address. Minimum: 20 points."),
    (".price", "Check the equivalent of points in LTC and USD, or convert a number to different currencies."),
]


GAME_COMMANDS = [
    (
        ".cf / .coinflip",
        ".cf <bet amount in points> <Heads / Tails or H / T>\n"
        "One provably-fair roll decides the result. Winner takes 1.92× the bet."
    ),
    (
        ".bj / .blackjack",
        ".bj <bet amount in points> [21+3 sidebet] [Perfect Pair sidebet]\n"
        "Winner takes 1.92× the bet."
    ),
    (
        ".mines",
        ".mines <bet amount in points>\n"
        "Reveal tiles and cash out before hitting a mine."
    ),
    (
        ".horse",
        ".horse <bet amount in points>\n"
        "Choose Horse 1, 2, 3, or 4 and watch the race."
    ),
    (
        ".limbo",
        ".limbo <bet amount in points> <target multiplier>\n"
        "Choose a target multiplier and try to beat it."
    ),
    (
        ".bjdice",
        ".bjdice <bet amount in points>\n"
        "Roll as close to 21 as possible. Going over 21 loses."
    ),
    (
        ".ward",
        ".ward <bet amount in points>\n"
        "You and the bot roll a die. The higher roll wins."
    ),
]


# ============================================================
# HELP EMBEDS
# ============================================================

def create_main_help():

    return discord.Embed(
        title="Help Command - Main Menu",
        description=(
            "Welcome to **Thunder Casino**, the best Discord "
            "Litecoin Casino Bot.\n\n"
            "💡 New here? Read `.guide`\n\n"
            "**Rate:** 1 point = 0.005 LTC\n"
            "**Total Commands:** "
            f"{len(BALANCE_COMMANDS) + len(UTILITY_COMMANDS) + len(GAME_COMMANDS)}\n"
            "**Total Users:** "
            f"{get_total_users_sync()}\n\n"
            "Bot made by <@1519015243710201927>"
        ),
        color=EMBED_DEFAULT,
    )


def create_category_embed(category):

    if category == "games":

        embed = discord.Embed(
            title="Games",
            description=(
                "All available casino games.\n\n"
                "Select another category below."
            ),
            color=EMBED_DEFAULT,
        )

        for command, description in GAME_COMMANDS:

            embed.add_field(
                name=f"**{command}**",
                value=description,
                inline=False,
            )

        embed.set_footer(
            text="Thunder Casino • Games"
        )

        return embed

    if category == "utility":

        embed = discord.Embed(
            title="Utility",
            description=(
                "Utility and account commands.\n\n"
                "Select another category below."
            ),
            color=EMBED_DEFAULT,
        )

        for command, description in UTILITY_COMMANDS:

            embed.add_field(
                name=f"**{command}**",
                value=description,
                inline=False,
            )

        embed.set_footer(
            text="Thunder Casino • Utility"
        )

        return embed

    if category == "balance":

        embed = discord.Embed(
            title="Balance",
            description=(
                "Casino, information and miscellaneous commands.\n\n"
                "Select another category below."
            ),
            color=EMBED_DEFAULT,
        )

        for command, description in BALANCE_COMMANDS:

            embed.add_field(
                name=f"**{command}**",
                value=description,
                inline=False,
            )

        embed.set_footer(
            text="Thunder Casino • Balance"
        )

        return embed

    return create_main_help()


# ============================================================
# HELP SELECT MENU
# ============================================================

class HelpSelect(discord.ui.Select):

    def __init__(self):

        options = [
            discord.SelectOption(
                label="Games",
                value="games",
                description="View all casino games.",
            ),
            discord.SelectOption(
                label="Utility",
                value="utility",
                description="View all utility commands.",
            ),
            discord.SelectOption(
                label="Balance",
                value="balance",
                description="View balance and miscellaneous commands.",
            ),
        ]

        super().__init__(
            placeholder="Select a category",
            min_values=1,
            max_values=1,
            options=options,
        )

    async def callback(self, interaction):

        selected = self.values[0]

        embed = create_category_embed(
            selected
        )

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

        self.add_item(
            HelpSelect()
        )


# ============================================================
# USER COUNT
# ============================================================

def get_total_users_sync():

    # Database is loaded asynchronously.
    # The real count is updated by the async help command.
    return "..."


async def get_total_users():

    try:

        async with db.pool.acquire() as conn:

            count = await conn.fetchval(
                "SELECT COUNT(*) FROM users"
            )

            return count or 0

    except Exception:

        return 0


# ============================================================
# HELP COMMAND
# ============================================================

@bot.command(
    name="help"
)
async def help_command(ctx):

    total_users = await get_total_users()

    total_commands = (
        len(BALANCE_COMMANDS)
        + len(UTILITY_COMMANDS)
        + len(GAME_COMMANDS)
    )

    embed = discord.Embed(
        title="Help Command - Main Menu",
        description=(
            "Welcome to **Thunder Casino**, the best Discord "
            "Litecoin Casino Bot.\n\n"
            "💡 New here? Read `.guide`\n\n"
            "**Rate:** 1 point = 0.005 LTC\n"
            f"**Total Commands:** {total_commands}\n"
            f"**Total Users:** {total_users}\n\n"
            "Bot made by <@1519015243710201927>"
        ),
        color=EMBED_DEFAULT,
    )

    await ctx.send(
        embed=embed,
        view=HelpView(),
    )


# ============================================================
# BALANCE COMMAND
# ============================================================

@bot.command(
    name="balance",
    aliases=["bal", "b"],
)
async def balance(ctx):

    balance = await db.get_balance(
        ctx.author.id
    )

    # Requested wallet display.
    #
    # The points system still exists internally.
    # The wallet message displays USD.

    usd_value = float(balance) * 0.005

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
# ADD BALANCE
# ============================================================

@bot.command(
    name="add"
)
@commands.is_owner()
async def add_balance(
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
        value=f"**{format_points(new_balance)} points**",
        inline=False,
    )

    await ctx.send(
        embed=embed
    )


# ============================================================
# BOT READY
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
            "❌ Invalid argument. Please check the command format."
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
        "DISCORD_TOKEN is missing from .env"
    )


bot.run(
    DISCORD_TOKEN
)
