from sc2.constants import *


class QueenController:
    def __init__(self, bot):
        self.bot = bot

    async def queen_behavior(self):
        if self.bot.units(QUEEN).exists:
            for queen in self.bot.units(QUEEN):
                await self.bot.army_controller.defend(queen)
                await self.bot.army_controller.patrol(queen, self.bot.townhalls)

                abilities = await self.bot.get_available_abilities(queen)
                if EFFECT_INJECTLARVA in abilities:
                    await self.bot.do(queen(EFFECT_INJECTLARVA, self.bot.townhalls.closest_to(queen)))
