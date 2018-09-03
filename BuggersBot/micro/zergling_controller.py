import random

from sc2.constants import *


class ZerglingController:
    def __init__(self, bot):
        self.bot = bot

        self.early_harassers = set()

        self.num_lings = 0
        self.num_banelings = 0
        self.baneling_ratio = 0.0
        self.BANELING_RATIO = .2

    async def step(self):
        self.update_baneling_ratio()
        await self.early_harass()
        await self.evolve_to_baneling()

    def update_baneling_ratio(self):
        zerglings = self.bot.units(ZERGLING)
        banelings = self.bot.units(BANELING)

        num_lings = len(zerglings) + len(banelings) + 0.0001
        num_banelings = len(banelings)

        self.num_lings = num_lings
        self.num_banelings = num_banelings
        self.baneling_ratio = num_banelings / num_lings

    async def early_harass(self):
        for ling in list(self.early_harassers):
            if not self.bot.units.find_by_tag(ling):
                self.early_harassers.remove(ling)

        if (self.bot.strategy_controller.ZERGLING_NATURAL_HARASS
                and len(self.early_harassers) < 4
                and self.bot.units(ZERGLING).exists):

            for ling in self.bot.units(ZERGLING):
                self.early_harassers.add(ling.tag)

        for ling in self.early_harassers:
            await self.bot.army_controller.patrol(self.bot.units.find_by_tag(ling),
                                                  self.bot.globals.enemy_expansions[:2],
                                                  attack=True)

    async def evolve_to_baneling(self):
        if self.bot.units(BANELINGNEST).exists:
            for ling in self.bot.units(ZERGLING):
                if self.bot.checker.unit(BANELING, max_units=self.num_lings * self.BANELING_RATIO):
                    await self.bot.do(ling.train(BANELING))
