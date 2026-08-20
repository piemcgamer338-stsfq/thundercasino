import asyncpg
from decimal import Decimal


class Database:

    def __init__(self, database_url):
        self.database_url = database_url
        self.pool = None

    # ========================================================
    # CONNECTION
    # ========================================================

    async def connect(self):

        self.pool = await asyncpg.create_pool(
            self.database_url,
            min_size=1,
            max_size=10
        )

        await self.create_tables()

    # ========================================================
    # TABLES
    # ========================================================

    async def create_tables(self):

        async with self.pool.acquire() as conn:

            await conn.execute("""
                CREATE TABLE IF NOT EXISTS users (

                    user_id BIGINT PRIMARY KEY,

                    balance NUMERIC(20,2)
                        NOT NULL DEFAULT 0,

                    wagered NUMERIC(20,2)
                        NOT NULL DEFAULT 0,

                    daily_wager NUMERIC(20,2)
                        NOT NULL DEFAULT 0,

                    weekly_wager NUMERIC(20,2)
                        NOT NULL DEFAULT 0,

                    monthly_wager NUMERIC(20,2)
                        NOT NULL DEFAULT 0,

                    games_played BIGINT
                        NOT NULL DEFAULT 0,

                    games_won BIGINT
                        NOT NULL DEFAULT 0,

                    deposits NUMERIC(20,2)
                        NOT NULL DEFAULT 0,

                    withdrawals NUMERIC(20,2)
                        NOT NULL DEFAULT 0,

                    deposit_index INTEGER
                        NOT NULL DEFAULT 0,

                    created_at TIMESTAMP
                        NOT NULL DEFAULT NOW()
                );
            """)

            await conn.execute("""
                CREATE TABLE IF NOT EXISTS games (

                    id BIGSERIAL PRIMARY KEY,

                    user_id BIGINT NOT NULL,

                    game TEXT NOT NULL,

                    bet NUMERIC(20,2) NOT NULL,

                    result TEXT,

                    payout NUMERIC(20,2)
                        NOT NULL DEFAULT 0,

                    created_at TIMESTAMP
                        NOT NULL DEFAULT NOW()
                );
            """)

            await conn.execute("""
                CREATE TABLE IF NOT EXISTS deposits (

                    id BIGSERIAL PRIMARY KEY,

                    user_id BIGINT NOT NULL,

                    address TEXT NOT NULL,

                    txid TEXT UNIQUE NOT NULL,

                    ltc_amount NUMERIC(20,8)
                        NOT NULL,

                    usd_value NUMERIC(20,2)
                        NOT NULL,

                    points NUMERIC(20,2)
                        NOT NULL,

                    confirmations INTEGER
                        NOT NULL DEFAULT 0,

                    created_at TIMESTAMP
                        NOT NULL DEFAULT NOW()
                );
            """)

            await conn.execute("""
                CREATE TABLE IF NOT EXISTS settings (

                    key TEXT PRIMARY KEY,

                    value TEXT
                );
            """)

    # ========================================================
    # USER
    # ========================================================

    async def create_user(self, user_id):

        async with self.pool.acquire() as conn:

            await conn.execute("""
                INSERT INTO users (user_id)
                VALUES ($1)
                ON CONFLICT (user_id)
                DO NOTHING
            """, user_id)

    async def get_user(self, user_id):

        await self.create_user(user_id)

        async with self.pool.acquire() as conn:

            return await conn.fetchrow("""
                SELECT *
                FROM users
                WHERE user_id = $1
            """, user_id)

    # ========================================================
    # BALANCE
    # ========================================================

    async def get_balance(self, user_id):

        user = await self.get_user(user_id)

        return Decimal(str(user["balance"]))

    async def add_balance(self, user_id, amount):

        await self.create_user(user_id)

        async with self.pool.acquire() as conn:

            await conn.execute("""
                UPDATE users

                SET balance = balance + $1

                WHERE user_id = $2
            """, amount, user_id)

    async def remove_balance(self, user_id, amount):

        await self.create_user(user_id)

        async with self.pool.acquire() as conn:

            result = await conn.execute("""
                UPDATE users

                SET balance = balance - $1

                WHERE user_id = $2
                AND balance >= $1
            """, amount, user_id)

            return result == "UPDATE 1"

    # ========================================================
    # WAGER
    # ========================================================

    async def add_wager(self, user_id, amount):

        async with self.pool.acquire() as conn:

            await conn.execute("""
                UPDATE users

                SET
                    wagered = wagered + $1,
                    daily_wager = daily_wager + $1,
                    weekly_wager = weekly_wager + $1,
                    monthly_wager = monthly_wager + $1,
                    games_played = games_played + 1

                WHERE user_id = $2
            """, amount, user_id)

    async def add_win(self, user_id):

        async with self.pool.acquire() as conn:

            await conn.execute("""
                UPDATE users

                SET games_won = games_won + 1

                WHERE user_id = $1
            """, user_id)

    # ========================================================
    # GAME HISTORY
    # ========================================================

    async def save_game(
        self,
        user_id,
        game,
        bet,
        result,
        payout
    ):

        async with self.pool.acquire() as conn:

            await conn.execute("""
                INSERT INTO games
                (
                    user_id,
                    game,
                    bet,
                    result,
                    payout
                )

                VALUES
                ($1, $2, $3, $4, $5)
            """,
                user_id,
                game,
                bet,
                result,
                payout
            )

    # ========================================================
    # SETTINGS
    # ========================================================

    async def set_setting(self, key, value):

        async with self.pool.acquire() as conn:

            await conn.execute("""
                INSERT INTO settings
                (key, value)

                VALUES
                ($1, $2)

                ON CONFLICT (key)

                DO UPDATE SET
                    value = EXCLUDED.value
            """, key, value)

    async def get_setting(self, key):

        async with self.pool.acquire() as conn:

            row = await conn.fetchrow("""
                SELECT value
                FROM settings
                WHERE key = $1
            """, key)

            if row:
                return row["value"]

            return None
