from sc2.constants import *


class ZerglingController:
    def __init__(self, bot):
        self.bot = bot

        self.baneling_ratio = None
        self.BANELING_RATIO = .2

    async def step(self):
        self.update_baneling_ratio()
        await self.evolve_to_baneling()

    def update_baneling_ratio(self):
        zerglings = self.bot.units(ZERGLING)
        banelings = self.bot.units(BANELING)

        num_lings = len(zerglings) + len(banelings) + 0.0001
        num_banelings = len(banelings)

        self.baneling_ratio = num_banelings / num_lings

    async def evolve_to_baneling(self):
        if (self.baneling_ratio < self.BANELING_RATIO
                and self.bot.units(BANELINGNEST).exists):
            if self.bot.units(ZERGLING).exists and self.bot.can_afford(BANELING):
                await self.bot.do(self.bot.units(ZERGLING).random.train(BANELING))
