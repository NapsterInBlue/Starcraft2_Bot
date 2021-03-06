"""
Central point of logic for strategy that all other Controllers read from
"""


from sc2.constants import *


class StrategyController:
    def __init__(self, bot):
        self.bot = bot

        self.OPENER = True

        self.ZERGLING_NATURAL_HARASS = True

        self.AMASS_ARMY = False

        self.max_bases = 2
        self.EXPAND = False

        self.MAX_EVOS = 1

    async def step(self):
        await self.game_time_benchmarks()

    async def game_time_benchmarks(self):
        if self.bot.globals.game_time_in_mins > 3 and not self.AMASS_ARMY:
            await self.toggle_amass_army(True)

        if self.bot.globals.game_time_in_mins > 3.5 and len(self.bot.globals.bases) < 3:
            if not self.bot.building_controller.kill_dual_expand:
                self.EXPAND = True
                self.max_bases = 3

        if self.bot.globals.game_time_in_mins > 6:
            self.ZERGLING_NATURAL_HARASS = False

    async def toggle_amass_army(self, value):
        print("Amassing army")
        self.AMASS_ARMY = value
        self.bot.unit_creation_controller.baseRallyPointsSet = {}
