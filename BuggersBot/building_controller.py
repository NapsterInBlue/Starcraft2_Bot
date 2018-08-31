"""
Controls the construction of buildings
"""

from sc2.constants import *

from sc2.position import Point2


class BuildingController:
    def __init__(self, bot):
        self.bot = bot

    async def step(self):
        await self.expand_vespene()

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

