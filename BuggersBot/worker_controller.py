from sc2.ids.unit_typeid import UnitTypeId
from sc2.constants import *


class WorkerController:
    def __init__(self, bot=None):
        self.bot = bot

        self.larvae = None

        self.max_workers_on_gas = 9
        self.current_workers_on_gas = 0
        self.maximum_workers = 65

        self.worker_unit_types = [
            UnitTypeId.DRONE,
            UnitTypeId.PROBE,
            UnitTypeId.SCV
        ]

        self.threat_proximity = 20

        self.nearby_enemy_workers_found = {}
        self.nearby_enemy_units_found = {}
        self.nearby_enemy_structures_found = {}

    async def step(self):
        self.larvae = self.bot.coordinator.larvae

        self.update_threats()
        self.update_worker_count_on_gas()
        await self.build_workers()
        await self.bot.distribute_workers()

    def update_threats(self):
        """Updates self.nearby_enemy_X dicts when enemies are within
        self.threat_proximity units"""
        hatcheries = self.bot.units(UnitTypeId.HATCHERY)

        for hatchery in hatcheries:
            nearby_enemy_workers = self.bot.known_enemy_units.filter(
                lambda unit: unit.type_id in self.worker_unit_types
            ).closer_than(self.threat_proximity, hatchery.position)

            nearby_enemy_units = self.bot.known_enemy_units.filter(
                lambda unit: unit.type_id not in self.worker_unit_types
            ).closer_than(self.threat_proximity, hatchery.position)

            nearby_enemy_structures = self.bot.known_enemy_structures.closer_than(
                self.threat_proximity, hatchery.position
            )

            for unit in nearby_enemy_workers:
                if unit.tag not in self.nearby_enemy_workers_found:
                    self.nearby_enemy_workers_found[unit.tag] = {'position': unit.position}

            for unit in nearby_enemy_units:
                if unit.tag not in self.nearby_enemy_workers_found:
                    self.nearby_enemy_workers_found[unit.tag] = {'position': unit.position}

            for unit in nearby_enemy_structures:
                if unit.tag not in self.nearby_enemy_structures_found:
                    self.nearby_enemy_structures_found[unit.tag] = {'position': unit.position}

    def update_worker_count_on_gas(self):
        self.current_workers_on_gas = 0

        for geyser in self.bot.geysers:
            self.current_workers_on_gas += geyser.assigned_harvesters

    async def build_workers(self):
        n_workers = self.bot.units(UnitTypeId.DRONE).amount

        if self.optimize_worker_ct():
            if self.bot.coordinator.check_unit_build(UnitTypeId.DRONE):
                await self.bot.do(self.larvae.random.train(UnitTypeId.DRONE))

    def optimize_worker_ct(self):
        for base in self.bot.townhalls:
            if (base.assigned_harvesters - base.ideal_harvesters < 0
                    and self.bot.coordinator.check_unit_build(DRONE, max_units=self.maximum_workers)):

                return True
        return False
