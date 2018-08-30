import random

import sc2

from sc2.constants import (LARVA, DRONE, OVERLORD, QUEEN,
                           ZERGLING)
from sc2.constants import HATCHERY, EXTRACTOR, SPAWNINGPOOL
from sc2.constants import RESEARCH_ZERGLINGMETABOLICBOOST
from sc2.constants import EFFECT_INJECTLARVA


class NickZergBot(sc2.BotAI):
    def __init__(self):
        self.ITERATIONS_PER_MINUTE = 165
        self.MAX_WORKERS = 65
        self.OPENER = True
        self.iteration = 0

        self.larvae = None
        self.creep_queen = None
        self.bases = None
        self.hq = None

    async def on_step(self, iteration):
        self.bases = self.townhalls
        self.hq = self.townhalls.first
        self.larvae = self.units(LARVA)
        self.iteration = iteration

        await self.distribute_workers()
        await self.opener()
        await self.queen_behavior()

        if not self.OPENER:
            await self.build_offensive_force()
            await self.attack()

    def check_unit_build(self, desired_unit, needs_larva=True, max_units=999,
                         supply_used_gt=0, supply_used_lt=201,
                         supply_left_gt=0, supply_left_lt=201):

        unit_count = self.units(desired_unit).amount + self.already_pending(desired_unit)
        larva_req_met = not needs_larva or self.larvae.exists

        return (larva_req_met
                and supply_used_lt > self.supply_used > supply_used_gt
                and supply_left_lt > self.supply_left > supply_left_gt
                and self.can_afford(desired_unit)
                and unit_count < max_units)

    def check_for_building(self, desired_building, at_least=0, limit=999):

        building_count = (self.units(desired_building).amount
                          + self.already_pending(desired_building))

        return (at_least <= building_count < limit
                and self.can_afford(desired_building))

    def optimize_worker_ct(self):
        for base in self.townhalls:
            if (base.assigned_harvesters - base.ideal_harvesters < 0
                    and self.check_unit_build(DRONE, max_units=self.MAX_WORKERS)):

                return True
        return False

    async def opener(self):
        """Lovingly and painstakingly implented the build order of this guide:
        https://www.reddit.com/r/allthingszerg/comments/3wzi14/welcome_to_lotv_heres_my_writeup_of_solid/"""
        if self.OPENER:
            if self.check_unit_build(DRONE, supply_used_lt=13):
                await self.do(self.larvae.random.train(DRONE))

            if self.check_unit_build(OVERLORD, supply_used_lt=14, max_units=2):
                await self.do(self.larvae.random.train(OVERLORD))

            if self.check_for_building(HATCHERY, limit=2):
                await self.expand_now()

            if self.check_unit_build(DRONE, supply_used_lt=20, supply_left_gt=4):
                await self.do(self.larvae.random.train(DRONE))

            if self.check_for_building(HATCHERY, at_least=2):
                if self.check_for_building(SPAWNINGPOOL, limit=1):
                    await self.do(self.units(DRONE).random.move(self.enemy_start_locations[0]))
                    await self.build(SPAWNINGPOOL, near=self.hq)

                if self.check_for_building(EXTRACTOR, limit=1) and self.supply_used > 17:
                    drone = self.workers.random
                    target = self.state.vespene_geyser.closest_to(drone.position)
                    await self.do(drone.build(EXTRACTOR, target))

                if self.check_unit_build(OVERLORD, supply_used_gt=20, max_units=3):
                    await self.do(self.larvae.first.train(OVERLORD))

                if self.optimize_worker_ct():
                    await self.do(self.larvae.first.train(DRONE))

                if self.units(SPAWNINGPOOL).ready:
                    if (self.check_unit_build(QUEEN, max_units=3, needs_larva=False)
                            and self.hq.is_ready and self.hq.noqueue):

                        await self.do(self.hq.train(QUEEN))

                    if self.can_afford(RESEARCH_ZERGLINGMETABOLICBOOST):
                        self.OPENER = False
                        await self.do(self.units(SPAWNINGPOOL).first(RESEARCH_ZERGLINGMETABOLICBOOST))

    async def build_offensive_force(self):
        if self.check_unit_build(OVERLORD, supply_left_lt=5):
            await self.do(self.larvae.random.train(OVERLORD))

        if self.check_unit_build(ZERGLING, max_units=50):
            await self.do(self.larvae.random.train(ZERGLING))

        if self.optimize_worker_ct():
            await self.do(self.larvae.random.train(DRONE))

    async def patrol(self, unit):
        if unit.is_idle:
            await self.do(unit.move(self.townhalls.random.position))

    async def defend(self, unit):
        for enemy in self.known_enemy_units:
            dist_to_base = min([enemy.distance_to(base) for base in self.bases])
            if dist_to_base < 30:
                await self.do(unit.attack(enemy))

    async def queen_behavior(self):
        if self.units(QUEEN).exists:
            for queen in self.units(QUEEN):
                await self.defend(queen)
                await self.patrol(queen)

                abilities = await self.get_available_abilities(queen)
                if EFFECT_INJECTLARVA in abilities:
                    await self.do(queen(EFFECT_INJECTLARVA, self.townhalls.closest_to(queen)))

    def find_target(self):
        if len(self.known_enemy_units) > 0:
            return random.choice(self.known_enemy_units)
        elif len(self.known_enemy_structures) > 0:
            return random.choice(self.known_enemy_structures)
        else:
            return self.enemy_start_locations[0]

    async def attack(self):
        # {UNIT: [n to fight, n to defend]}
        aggressive_units = {ZERGLING: [15, 5],
                            }

        for UNIT in aggressive_units:
            if self.units(UNIT).amount > aggressive_units[UNIT][0]:
                for s in self.units(UNIT).idle:
                    await self.do(s.attack(self.find_target()))

            elif self.units(UNIT).amount > aggressive_units[UNIT][1]:
                for s in self.units(UNIT).idle:
                    await self.defend(s)
