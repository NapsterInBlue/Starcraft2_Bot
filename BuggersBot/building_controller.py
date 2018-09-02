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
        await self.expand_hatcheries()

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

    async def expand_hatcheries(self):
        if self.bot.strategy_controller.EXPAND and self.checker.building(HATCHERY):
            loc = self.find_expansion_location()
            print('Expanding to ', loc)
            self.bot.strategy_controller.EXPAND = False
            await self.bot.expand_now(location=loc)

    def find_expansion_location(self):
        debug = True

        bases = self.bot.globals.bases
        center = self.bot.calculator.center_of_units(bases)

        candidates = list(filter(
            lambda x: x not in [base.position for base in self.bot.globals.bases],
            center.sort_by_distance(list(self.bot.expansion_locations))
        ))[2:]

        loc = random.sample(candidates, k=1)[0]

        if debug:
            print([base.position for base in bases])
            print(center)
            print(candidates)
            print(loc)

        return loc

# utils

    def announce(self, unit, unit_str):
        if not self.bot.already_pending(unit):
            print('{:6.2f} Building {}'.format(self.bot.time, unit_str))