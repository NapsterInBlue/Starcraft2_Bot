"""
Collection of useful game-state calculations for use across
different Controller classes
"""

from sc2.position import Point2
from sc2.constants import *

from sc2.unit import Unit
from sc2.units import Units


class Calculator:
    def __init__(self, bot):
        self.bot = bot

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
