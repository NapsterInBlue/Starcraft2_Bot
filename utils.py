# coding=utf-8

import random

import sc2
from sc2.units import Units
from sc2.unit import Unit

from sc2.constants import (LARVA, DRONE, OVERLORD, QUEEN,
                           ZERGLING)
from sc2.constants import HATCHERY, EXTRACTOR, SPAWNINGPOOL
from sc2.constants import RESEARCH_ZERGLINGMETABOLICBOOST
from sc2.constants import EFFECT_INJECTLARVA, RALLY_WORKERS, RALLY_UNITS

from sc2.position import Point2


class UtilityBot(object):
    pass

    @property
    def game_time_in_seconds(self):
        # returns real time if game is played on "faster"
        return self.state.game_loop * 0.725 * (1 / 16)

    @property
    def game_time_in_mins(self):
        # returns real time if game is played on "faster"
        return self.game_time_in_seconds / 60

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

    async def patrol(self, unit):
        if unit.is_idle:
            await self.do(unit.move(self.townhalls.random.position))

    async def defend(self, unit):
        for enemy in self.known_enemy_units:
            dist_to_base = min([enemy.distance_to(base) for base in self.bases])
            if dist_to_base < 30:
                await self.do(unit.attack(enemy))

    def center_of_units(self, units):
        if isinstance(units, list):
            units = Units(units, self._game_data)
        assert isinstance(units, Units)
        assert units.exists
        if len(units) == 1:
            return units[0].position.to2
        coordX = sum([unit.position.x for unit in units]) / len(units)
        coordY = sum([unit.position.y for unit in units]) / len(units)
        return Point2((coordX, coordY))

    def find_amass_army_rally_point(self):
        """Figure out where to send new units when intentionally building an army"""
        enemy_hq = self.enemy_start_locations[0]
        satellite = self.townhalls.closest_to(enemy_hq)
        point = satellite.position.towards(self._game_info.map_center, distance=5, limit=True)
        print("Setting Rally point to {}".format(point.position.to2))
        return point