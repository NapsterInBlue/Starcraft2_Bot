from sc2.constants import *


class Globals:
    def __init__(self, bot):
        self.bot = bot
        self.bases = None
        self.larvae = None

        self.worker_unit_types = [
            UnitTypeId.DRONE,
            UnitTypeId.PROBE,
            UnitTypeId.SCV
        ]

        self.threat_proximity = 20

        self.nearby_enemy_workers_found = {}
        self.nearby_enemy_units_found = {}
        self.nearby_enemy_structures_found = {}

        self.map_center = None

    def init(self):
        self.map_center = self.bot.game_info.map_center

    async def step(self):
        self.update_base_list()
        self.update_larvae_list()
        self.update_threats()

    def update_base_list(self):
        self.bases = self.bot.townhalls

    def update_larvae_list(self):
        self.larvae = self.bot.units(LARVA)

    def update_threats(self):
        """Updates self.nearby_enemy_X dicts when enemies are within
        self.threat_proximity units"""

        for base in self.bases:
            nearby_enemy_workers = self.bot.known_enemy_units.filter(
                lambda unit: unit.type_id in self.worker_unit_types
            ).closer_than(self.threat_proximity, base.position)

            nearby_enemy_units = self.bot.known_enemy_units.filter(
                lambda unit: unit.type_id not in self.worker_unit_types
            ).closer_than(self.threat_proximity, base.position)

            nearby_enemy_structures = self.bot.known_enemy_structures.closer_than(
                self.threat_proximity, base.position
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

# utils

    @property
    def game_time_in_seconds(self):
        # returns real time if game is played on "faster"
        return self.bot.state.game_loop * 0.725 * (1 / 16)

    @property
    def game_time_in_mins(self):
        # returns real time if game is played on "faster"
        return self.game_time_in_seconds / 60