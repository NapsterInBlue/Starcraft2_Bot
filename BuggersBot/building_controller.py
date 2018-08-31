"""
Controls the construction of buildings
"""

from sc2.constants import *

from sc2.position import Point2


class BuildingController:
    def __init__(self, bot):
        self.bot = bot

    async def step(self):
        await self.assign_rally_points()

    async def assign_rally_points(self):
        """Rally workers to nearest minerals. Rally units closeby."""
        if hasattr(self, "baseRallyPointsSet"):
            for base in self.bot.globals.bases:
                if base.tag not in self.baseRallyPointsSet:
                    mf = self.bot.state.mineral_field.closest_to(base.position.to2.offset(Point2((0, -3))))
                    err = await self.bot.do(base(RALLY_WORKERS, mf))
                    if not err:
                        mfs = self.bot.state.mineral_field.closer_than(10, base.position.to2)
                        if self.bot.coordinator.AMASS_ARMY:
                            loc = self.bot.unit_creation_controller.find_amass_army_rally_point()
                        elif mfs.exists:
                            loc = self.bot.coordinator.center_of_units(mfs)
                        err = await self.bot.do(base(RALLY_UNITS, loc))
                        if not err:
                            self.baseRallyPointsSet[base.tag] = loc
        else:
            self.baseRallyPointsSet = {}
