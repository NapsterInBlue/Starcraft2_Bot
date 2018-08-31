"""
Lovingly and painstakingly implented the build order of this guide:
https://www.reddit.com/r/allthingszerg/comments/3wzi14/welcome_to_lotv_heres_my_writeup_of_solid/

Shuts off after we research metabolic boost
"""

from sc2.constants import *


class Opener:
    def __init__(self, bot):
        self.bot = bot
        self.checker = self.bot.checker
        self.do = self.bot.do

    async def step(self):
        self.bases = self.bot.townhalls
        self.hq = self.bot.townhalls.first
        self.larvae = self.bot.units(LARVA)

        await self.bot.distribute_workers()

        if self.checker.unit(DRONE, supply_used_lt=13):
            await self.do(self.larvae.random.train(DRONE))

        if self.checker.unit(OVERLORD, supply_used_lt=14, max_units=2):
            await self.do(self.larvae.random.train(OVERLORD))

        if self.checker.building(HATCHERY, limit=2):
            await self.bot.expand_now()

        if self.checker.unit(DRONE, supply_used_lt=20, supply_left_gt=4):
            await self.do(self.larvae.random.train(DRONE))

        if self.checker.building(HATCHERY, at_least=2):
            if self.checker.building(SPAWNINGPOOL, limit=1):
                await self.do(self.bot.units(DRONE).random.move(self.bot.enemy_start_locations[0]))
                await self.bot.build(SPAWNINGPOOL, near=self.hq)

            if self.checker.building(EXTRACTOR, limit=1) and self.bot.supply_used > 17:
                drone = self.bot.workers.random
                target = self.bot.state.vespene_geyser.closest_to(drone.position)
                await self.do(drone.build(EXTRACTOR, target))

            if self.checker.unit(OVERLORD, supply_used_gt=20, max_units=3):
                await self.do(self.larvae.first.train(OVERLORD))

            if self.bot.worker_controller.optimize_worker_ct():
                await self.do(self.larvae.first.train(DRONE))

            if self.bot.units(SPAWNINGPOOL).ready:
                if (self.checker.unit(QUEEN, max_units=3, needs_larva=False)
                        and self.hq.is_ready and self.hq.noqueue):
                    await self.do(self.hq.train(QUEEN))

                if self.bot.can_afford(RESEARCH_ZERGLINGMETABOLICBOOST):
                    await self.do(self.bot.units(SPAWNINGPOOL).first(RESEARCH_ZERGLINGMETABOLICBOOST))
                    self.bot.strategy_controller.OPENER = False
