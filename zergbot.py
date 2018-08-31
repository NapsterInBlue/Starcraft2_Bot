import random

import sc2
from sc2.units import Units
from sc2.unit import Unit

from sc2.constants import *

from sc2.position import Point2


from coordinator import Coordinator


class NickZergBot(sc2.BotAI):
    def __init__(self):
        self.ITERATIONS_PER_MINUTE = 165
        self.MAX_WORKERS = 65
        self.AMASS_ARMY = False
        self.OPENER = True
        self.iteration = 0

        self.larvae = None
        self.creep_queen = None
        self.bases = None
        self.hq = None

        self.coordinator = Coordinator(bot=self)

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
            await self.assign_rally_points()
            await self.game_time()

    async def opener(self):
        """Lovingly and painstakingly implented the build order of this guide:
        https://www.reddit.com/r/allthingszerg/comments/3wzi14/welcome_to_lotv_heres_my_writeup_of_solid/"""
        if self.OPENER:
            if self.coordinator.check_unit_build(DRONE, supply_used_lt=13):
                await self.do(self.larvae.random.train(DRONE))

            if self.coordinator.check_unit_build(OVERLORD, supply_used_lt=14, max_units=2):
                await self.do(self.larvae.random.train(OVERLORD))

            if self.coordinator.check_for_building(HATCHERY, limit=2):
                await self.expand_now()

            if self.coordinator.check_unit_build(DRONE, supply_used_lt=20, supply_left_gt=4):
                await self.do(self.larvae.random.train(DRONE))

            if self.coordinator.check_for_building(HATCHERY, at_least=2):
                if self.coordinator.check_for_building(SPAWNINGPOOL, limit=1):
                    await self.do(self.units(DRONE).random.move(self.enemy_start_locations[0]))
                    await self.build(SPAWNINGPOOL, near=self.hq)

                if self.coordinator.check_for_building(EXTRACTOR, limit=1) and self.supply_used > 17:
                    drone = self.workers.random
                    target = self.state.vespene_geyser.closest_to(drone.position)
                    await self.do(drone.build(EXTRACTOR, target))

                if self.coordinator.check_unit_build(OVERLORD, supply_used_gt=20, max_units=3):
                    await self.do(self.larvae.first.train(OVERLORD))

                if self.coordinator.optimize_worker_ct():
                    await self.do(self.larvae.first.train(DRONE))

                if self.units(SPAWNINGPOOL).ready:
                    if (self.coordinator.check_unit_build(QUEEN, max_units=3, needs_larva=False)
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

    async def queen_behavior(self):
        if self.units(QUEEN).exists:
            for queen in self.units(QUEEN):
                await self.defend(queen)
                await self.patrol(queen)

                abilities = await self.get_available_abilities(queen)
                if EFFECT_INJECTLARVA in abilities:
                    await self.do(queen(EFFECT_INJECTLARVA, self.townhalls.closest_to(queen)))

    async def toggle_amass_army(self, value):
        self.AMASS_ARMY = value
        del self.hatcheryRallyPointsSet

    async def assign_rally_points(self):
        """Rally workers to nearest minerals. Rally units closeby."""
        if hasattr(self, "hatcheryRallyPointsSet"):
            for hatch in self.townhalls:
                if hatch.tag not in self.hatcheryRallyPointsSet:
                    mf = self.state.mineral_field.closest_to(hatch.position.to2.offset(Point2((0, -3))))
                    err = await self.do(hatch(RALLY_WORKERS, mf))
                    if not err:
                        mfs = self.state.mineral_field.closer_than(10, hatch.position.to2)
                        if self.AMASS_ARMY:
                            loc = self.find_amass_army_rally_point()
                        elif mfs.exists:
                            loc = self.center_of_units(mfs)
                        err = await self.do(hatch(RALLY_UNITS, loc))
                        if not err:
                            self.hatcheryRallyPointsSet[hatch.tag] = loc
        else:
            self.hatcheryRallyPointsSet = {}

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

    async def game_time(self):
        if self.game_time_in_mins > 3 and not self.AMASS_ARMY:
            await self.toggle_amass_army(True)