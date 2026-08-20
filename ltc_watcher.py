import asyncio
import aiohttp

from config import (
    LTC_CHECK_INTERVAL,
    LTC_REQUIRED_CONFIRMATIONS,
    LTC_XPUB
)


class LTCWatcher:

    def __init__(self, bot, database):

        self.bot = bot
        self.db = database

        self.running = False

    # ========================================================
    # START
    # ========================================================

    async def start(self):

        if self.running:
            return

        self.running = True

        print(
            "[LTC] Watcher started."
        )

        while self.running:

            try:

                await self.check_deposits()

            except Exception as e:

                print(
                    f"[LTC] Watcher error: {e}"
                )

            await asyncio.sleep(
                LTC_CHECK_INTERVAL
            )

    # ========================================================
    # CHECK DEPOSITS
    # ========================================================

    async def check_deposits(self):

        # ----------------------------------------------------
        # This will be completed next:
        #
        # 1. Derive next LTC address from XPUB
        # 2. Assign address to user
        # 3. Check blockchain
        # 4. Detect payment
        # 5. Check confirmations
        # 6. Get LTC/USD price
        # 7. Convert USD -> points
        # 8. Credit user
        # 9. Send deposit confirmation
        # 10. Prevent duplicate TX credits
        # ----------------------------------------------------

        pass
