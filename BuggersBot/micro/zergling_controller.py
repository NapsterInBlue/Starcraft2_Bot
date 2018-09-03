import random

from sc2.constants import *


class ZerglingController:
    def __init__(self, bot):
        self.bot = bot

        self.baneling_ratio = None
        self.BANELING_RATIO = .2

        self.early_harassers = set()

    async def step(self):
        self.update_baneling_ratio()
        await self.early_harass()
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

    async def early_harass(self):
        if (self.bot.strategy_controller.ZERGLING_NATURAL_HARASS
                and len(self.early_harassers) < 4
                and self.bot.units(ZERGLING).exists):

            for ling in self.bot.units(ZERGLING):
                self.early_harassers.add(ling)

        for ling in self.early_harassers:
            await self.bot.army_controller.patrol(ling,
                                                  self.bot.globals.enemy_expansions[:2])