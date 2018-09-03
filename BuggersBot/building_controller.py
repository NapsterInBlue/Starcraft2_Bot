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
            if (base.assigned_harvesters < base.ideal_harvesters
                    or not base.is_ready):
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
            await self.bot.build(EVOLUTIONCHAMBER, near=base)
            self.announce(EVOLUTIONCHAMBER, 'Evolution Chamber')

    async def build_baneling_nest(self):
        if (self.bot.units(SPAWNINGPOOL).exists and
                self.checker.building(UnitTypeId.BANELINGNEST, limit=1)):

            await self.bot.build(BANELINGNEST, near=self.bot.globals.hq)
            self.announce(BANELINGNEST, 'Baneling Nest')

    async def expand_hatcheries(self):
        if self.bot.strategy_controller.EXPAND and self.checker.building(HATCHERY):
            loc = self.find_expansion_location()
            self.bot.strategy_controller.EXPAND = False
            await self.bot.expand_now(location=loc)
            print('Expanding to ', loc)

    def find_expansion_location(self):
        """Randomly pick an unoccupied base from the three closest bases
        to the 'average location' of your existing bases"""
        debug = False

        base_locations = set([base.position for base in self.bot.globals.bases])
        center = self.bot.calculator.center_of_units(self.bot.globals.bases)

        candidates = set(self.bot.expansion_locations)

        # Remove locations with existing bases
        for candidate in list(candidates):
            for base in base_locations:
                if candidate.distance_to(base) < 10:
                    try:
                        candidates.remove(candidate)
                    except KeyError:
                        # already removed
                        pass

        candidates -= set(self.bot.globals.enemy_hq)

        closest_3 = center.sort_by_distance(list(candidates))[:3]
        loc = random.sample(closest_3, k=1)[0]

        if debug:
            print(base_locations)
            print(center)
            print(candidates)
            print(closest_3)
            print(loc)

        return loc

# utils

    def announce(self, unit, unit_str):
        if not self.bot.already_pending(unit):
            print('{:6.2f} Building {}'.format(self.bot.time, unit_str))