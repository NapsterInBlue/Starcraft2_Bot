"""
Controls the construction of buildings
"""

import random

from sc2.constants import *

from sc2.position import Point2


class BuildingController:
    def __init__(self, bot):
        self.bot = bot
        self.checker = self.bot.checker

    async def step(self):
        await self.expand_vespene()
        await self.build_evo_chamber()
        await self.build_baneling_nest()

    async def expand_vespene(self):
        bases = self.bot.globals.bases

        for base in bases:
            if base.assigned_harvesters < base.ideal_harvesters:
                continue
            vgs = self.bot.state.vespene_geyser.closer_than(15, base)
            for vg in vgs:
                if not self.bot.units(EXTRACTOR).closer_than(1, vg).exists:
                    if self.bot.checker.building(EXTRACTOR):
                        await self.bot.do(self.bot.units(DRONE).random.build(EXTRACTOR, vg))

    async def build_evo_chamber(self):
        if self.checker.building(UnitTypeId.EVOLUTIONCHAMBER,
                                 limit=self.bot.strategy_controller.MAX_EVOS):

            base = self.bot.globals.bases.random
            self.announce(EVOLUTIONCHAMBER, 'Evolution Chamber')
            await self.bot.build(EVOLUTIONCHAMBER, near=base)

    async def build_baneling_nest(self):
        if (self.bot.units(SPAWNINGPOOL).exists and
                self.checker.building(UnitTypeId.BANELINGNEST, limit=1)):

            self.announce(BANELINGNEST, 'Baneling Nest')
            await self.bot.build(BANELINGNEST, near=self.bot.globals.hq)


# utils

    def announce(self, unit, unit_str):
        if not self.bot.already_pending(unit):
            print('{:6.2f} Building {}'.format(self.bot.time, unit_str))