# coding=utf-8

import random

import sc2
from sc2.units import Units
from sc2.unit import Unit

from sc2.constants import *

from sc2.position import Point2


class Coordinator:
    def __init__(self, bot):
        self.bot = bot

        self.OPENER = True
        self.AMASS_ARMY = False

# utils

    def check_unit_build(self, desired_unit, needs_larva=True, max_units=999,
                         supply_used_gt=0, supply_used_lt=201,
                         supply_left_gt=0, supply_left_lt=201):

        unit_count = self.bot.units(desired_unit).amount + self.bot.already_pending(desired_unit)
        larva_req_met = not needs_larva or self.bot.globals.larvae.exists

        return (larva_req_met
                and supply_used_lt > self.bot.supply_used > supply_used_gt
                and supply_left_lt > self.bot.supply_left > supply_left_gt
                and self.bot.can_afford(desired_unit)
                and unit_count < max_units)

    def check_for_building(self, desired_building, at_least=0, limit=999):

        building_count = (self.bot.units(desired_building).amount
                          + self.bot.already_pending(desired_building))

        return (at_least <= building_count < limit
                and self.bot.can_afford(desired_building))

    def center_of_units(self, units):
        if isinstance(units, list):
            units = Units(units, self.bot._game_data)
        assert isinstance(units, Units)
        assert units.exists
        if len(units) == 1:
            return units[0].position.to2
        coordX = sum([unit.position.x for unit in units]) / len(units)
        coordY = sum([unit.position.y for unit in units]) / len(units)
        return Point2((coordX, coordY))

    async def toggle_amass_army(self, value):
        self.bot.AMASS_ARMY = value
