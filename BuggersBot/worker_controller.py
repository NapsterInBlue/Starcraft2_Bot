"""
Controls allocation and optimal counts/behavior of worker units
"""

from sc2.ids.unit_typeid import UnitTypeId
from sc2.constants import *


class WorkerController:
    def __init__(self, bot=None):
        self.bot = bot

        self.max_workers_on_gas = 9
        self.current_workers_on_gas = 0
        self.maximum_workers = 65

    async def step(self):
        self.larvae = self.bot.globals.larvae

        self.update_worker_count_on_gas()
        await self.build_workers()
        await self.bot.distribute_workers()

    def update_worker_count_on_gas(self):
        self.current_workers_on_gas = 0

        for geyser in self.bot.geysers:
            self.current_workers_on_gas += geyser.assigned_harvesters

    async def build_workers(self):
        n_workers = self.bot.units(UnitTypeId.DRONE).amount

        if self.optimize_worker_ct():
            await self.bot.do(self.larvae.random.train(UnitTypeId.DRONE))

    def optimize_worker_ct(self):
        for base in self.bot.globals.bases:
            if (base.assigned_harvesters - base.ideal_harvesters < 0
                    and self.bot.checker.unit(DRONE, max_units=self.maximum_workers)):

                return True
        return False
