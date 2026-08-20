import asyncio
import discord

from discord.ext import commands

from config import (
    DISCORD_TOKEN,
    DATABASE_URL,
    PREFIX,
    EMBED_DEFAULT,
    EMBED_WIN,
    EMBED_LOSS,
    EMBED_NEUTRAL
)

from database import Database
from ltc_watcher import LTCWatcher

from utils import (
    format_points,
    points_to_usd
)


# ============================================================
# BOT
# ============================================================

intents = discord.Intents.default()

intents.message_content = True

bot = commands.Bot(
    command_prefix=PREFIX,
    intents=intents,
    help_command=None
)


# ============================================================
# DATABASE
# ============================================================

db = Database(DATABASE_URL)

ltc_watcher = None


# ============================================================
# READY
# ============================================================

@bot.event
async def on_ready():

    global ltc_watcher

    print("=" * 50)

    print(
        f"Thunder Casino online as {bot.user}"
    )

    print(
        f"Prefix: {PREFIX}"
    )

    print("=" * 50)

    # --------------------------------------------------------
    # Database
    # --------------------------------------------------------

    if db.pool is None:

        await db.connect()

        print(
            "[DATABASE] PostgreSQL connected."
        )

    # --------------------------------------------------------
    # LTC watcher
    # --------------------------------------------------------

    if ltc_watcher is None:

        ltc_watcher = LTCWatcher(
            bot,
            db
        )

        asyncio.create_task(
            ltc_watcher.start()
        )

        print(
            "[LTC] Watcher task started."
        )


# ============================================================
# HELP VIEW
# ============================================================

class HelpView(discord.ui.View):

    def __init__(self):

        super().__init__(
            timeout=300
        )

        self.current_menu = "balance"

    # --------------------------------------------------------
    # BALANCE
    # --------------------------------------------------------

    @discord.ui.button(
        label="Balance",
        emoji="💰",
        style=discord.ButtonStyle.primary
    )
    async def balance_button(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):

        self.current_menu = "balance"

        embed = create_balance_help()

        await interaction.response.edit_message(
            embed=embed,
            view=self
        )

    # --------------------------------------------------------
    # GAMES
    # --------------------------------------------------------

    @discord.ui.button(
        label="Games",
        emoji="🎮",
        style=discord.ButtonStyle.secondary
    )
    async def games_button(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):

        self.current_menu = "games"

        embed = create_games_help()

        await interaction.response.edit_message(
            embed=embed,
            view=self
        )

    # --------------------------------------------------------
    # UTILITY
    # --------------------------------------------------------

    @discord.ui.button(
        label="Utility",
        emoji="🛠️",
        style=discord.ButtonStyle.secondary
    )
    async def utility_button(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):

        self.current_menu = "utility"

        embed = create_utility_help()

        await interaction.response.edit_message(
            embed=embed,
            view=self
        )


# ============================================================
# HELP EMBEDS
# ============================================================

def create_balance_help():

    embed = discord.Embed(
        title="💰 Thunder Casino",
        description=(
            "Welcome to **Thunder Casino**.\n\n"
            "Manage your balance and casino wallet "
            "using the commands below."
        ),
        color=EMBED_DEFAULT
    )

    embed.add_field(
        name="💰 Balance",
        value=(
            "` .balance `\n"
            "` .bal `\n\n"
            "View your current points balance."
        ),
        inline=False
    )

    embed.add_field(
        name="💳 Deposit",
        value=(
            "` .deposit `\n\n"
            "Generate your personal Litecoin "
            "deposit address."
        ),
        inline=False
    )

    embed.add_field(
        name="💸 Withdraw",
        value=(
            "` .withdraw <amount> <address> `"
        ),
        inline=False
    )

    embed.set_footer(
        text="Thunder Casino • .help"
    )

    return embed


def create_games_help():

    embed = discord.Embed(
        title="🎮 Thunder Casino — Games",
        color=EMBED_DEFAULT
    )

    embed.add_field(
        name="🪙 Coinflip",
        value=(
            "**`.cf <amount> <heads/tails>`**\n"
            "Example: `.cf 100 h`\n\n"
            "One provably-fair roll decides the result.\n"
            "Winner receives **1.92×** the bet."
        ),
        inline=False
    )

    embed.add_field(
        name="🃏 Blackjack",
        value=(
            "**`.bj <amount>`**\n"
            "Optional side bets:\n"
            "`21+3` • `Perfect Pair`"
        ),
        inline=False
    )

    embed.add_field(
        name="💣 Mines",
        value=(
            "**`.mines <amount>`**\n"
            "Reveal tiles and cash out before hitting a mine."
        ),
        inline=False
    )

    embed.add_field(
        name="🐎 Horse",
        value=(
            "**`.horse <amount>`**\n"
            "Choose Horse 1–4 and watch the race."
        ),
        inline=False
    )

    embed.add_field(
        name="📈 Limbo",
        value=(
            "**`.limbo <amount> <target>`**\n"
            "Choose your target multiplier."
        ),
        inline=False
    )

    embed.add_field(
        name="🎲 BJ Dice",
        value=(
            "**`.bjdice <amount>`**\n"
            "Roll as close to 21 as possible."
        ),
        inline=False
    )

    embed.add_field(
        name="🎲 Ward",
        value=(
            "**`.ward <amount>`**\n"
            "You and the bot roll a die."
        ),
        inline=False
    )

    return embed


def create_utility_help():

    embed = discord.Embed(
        title="🛠️ Thunder Casino — Utility",
        color=EMBED_DEFAULT
    )

    embed.add_field(
        name="🏆 Leaderboard",
        value=(
            "**`.lb`** / **`.leaderboard`**\n"
            "View the top wagerers."
        ),
        inline=False
    )

    embed.add_field(
        name="📊 Stats",
        value=(
            "**`.stats`**\n"
            "View your casino statistics."
        ),
        inline=False
    )

    embed.add_field(
        name="🏦 Deposit History",
        value=(
            "**`.dephistory`**\n"
            "View your deposit history."
        ),
        inline=False
    )

    embed.add_field(
        name="❓ Help",
        value="**`.help`**",
        inline=False
    )

    return embed


# ============================================================
# HELP COMMAND
# ============================================================

@bot.command(
    name="help"
)
async def help_command(ctx):

    embed = create_balance_help()

    await ctx.send(
        embed=embed,
        view=HelpView()
    )


# ============================================================
# BALANCE
# ============================================================

@bot.command(
    name="balance",
    aliases=["bal", "b"]
)
async def balance(ctx):

    balance = await db.get_balance(
        ctx.author.id
    )

    usd = points_to_usd(balance)

    embed = discord.Embed(
        title=f"💰 {ctx.author.display_name}'s Wallet",
        color=EMBED_DEFAULT
    )

    embed.add_field(
        name="Balance",
        value=(
            f"**{format_points(balance)} points**\n"
            f"≈ **${usd:.2f}**"
        ),
        inline=False
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
    amount: float
):

    if amount <= 0:

        await ctx.send(
            "❌ Amount must be greater than 0."
        )

        return

    await db.add_balance(
        member.id,
        amount
    )

    new_balance = await db.get_balance(
        member.id
    )

    embed = discord.Embed(
        title="💰 Balance Updated",
        description=(
            f"{member.mention} received "
            f"**{format_points(amount)} points**."
        ),
        color=EMBED_WIN
    )

    embed.add_field(
        name="New Balance",
        value=(
            f"**{format_points(new_balance)} points**"
        )
    )

    await ctx.send(
        embed=embed
    )


# ============================================================
# RUN
# ============================================================

if not DISCORD_TOKEN:

    raise RuntimeError(
        "DISCORD_TOKEN is missing from .env"
    )


bot.run(
    DISCORD_TOKEN
)
