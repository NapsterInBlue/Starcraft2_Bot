"""
Controls allocation and optimal counts/behavior of worker units
"""

from sc2.ids.unit_typeid import UnitTypeId
from sc2.constants import *


class WorkerController:
    def __init__(self, bot=None):
        self.bot = bot

        self.MAXIMUM_WORKERS = 65

    async def step(self):
        self.larvae = self.bot.globals.larvae

        await self.build_workers()
        await self.bot.distribute_workers()

    async def build_workers(self):
        if self.optimize_worker_ct():
            await self.bot.do(self.larvae.random.train(UnitTypeId.DRONE))

    def optimize_worker_ct(self):
        for base in self.bot.globals.bases:
            if (base.assigned_harvesters - base.ideal_harvesters < 0
                    and self.bot.checker.unit(DRONE, max_units=self.MAXIMUM_WORKERS)):

                return True
        return False
