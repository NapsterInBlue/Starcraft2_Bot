"""
Central point of logic for strategy that all other Controllers read from
"""


from sc2.constants import *


class StrategyController:
    def __init__(self, bot):
        self.bot = bot

        self.OPENER = True
        self.AMASS_ARMY = False

    async def step(self):
        await self.game_time()

    async def game_time(self):
        if self.bot.globals.game_time_in_mins > 3 and not self.AMASS_ARMY:
            await self.toggle_amass_army(True)

    async def toggle_amass_army(self, value):
        print("Amassing army")
        self.AMASS_ARMY = value
        self.bot.unit_creation_controller.baseRallyPointsSet = {}