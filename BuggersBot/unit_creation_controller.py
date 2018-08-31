"""
Controls unit construction and their rally points
"""

from sc2.constants import *
from sc2.position import Point2


class UnitCreationController:
    def __init__(self, bot):
        self.bot = bot
        self.larvae = None

    async def step(self):
        self.update_larvae()
        await self.build_offensive_force()
        await self.assign_rally_points()

    def update_larvae(self):
        self.larvae = self.bot.units(LARVA)

    async def build_offensive_force(self):
        if self.bot.checker.unit(OVERLORD, supply_left_lt=5):
            await self.bot.do(self.bot.globals.larvae.random.train(OVERLORD))

        if self.bot.worker_controller.optimize_worker_ct():
            await self.bot.do(self.bot.globals.larvae.random.train(DRONE))

        if self.bot.checker.unit(ZERGLING, max_units=50):
            await self.bot.do(self.bot.globals.larvae.random.train(ZERGLING))

    async def assign_rally_points(self):
        """Rally workers to nearest minerals. Rally units closeby."""
        if hasattr(self, "baseRallyPointsSet"):
            for base in self.bot.globals.bases:
                if base.tag not in self.baseRallyPointsSet:
                    mf = self.bot.state.mineral_field.closest_to(base.position.to2.offset(Point2((0, -3))))
                    await self.bot.do(base(RALLY_WORKERS, mf))

                    # # not convinced I need these lines

                    # err = await self.bot.do(base(RALLY_WORKERS, mf))
                    # if not err:

                    mfs = self.bot.state.mineral_field.closer_than(10, base.position.to2)
                    if self.bot.strategy_controller.AMASS_ARMY:
                        loc = self.find_amass_army_rally_point()
                    elif mfs.exists:
                        loc = self.bot.calculator.center_of_units(mfs)
                    else:
                        loc = base.position.to2
                    err = await self.bot.do(base(RALLY_UNITS, loc))
                    if not err:
                        self.baseRallyPointsSet[base.tag] = loc
        else:
            self.baseRallyPointsSet = {}

# utils

    def find_amass_army_rally_point(self):
        """Figure out where to send new units when intentionally building an army"""
        satellite = self.bot.townhalls.closest_to(self.bot.globals.enemy_hq)
        point = satellite.position.towards(self.bot.globals.map_center, distance=5, limit=True)
        print("Setting Rally point to {}".format(point.position.to2))
        return point
