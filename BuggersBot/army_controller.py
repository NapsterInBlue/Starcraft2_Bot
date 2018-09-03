"""
Controls all army micro and macro.

Army unit-specific controllers should drop their main coroutines in `ArmyController.step()`

Also has utility functions for:

- Defend
- Patrol
"""


import random

from sc2.unit import Unit
from sc2.units import Units
from sc2.constants import *

from BuggersBot.micro.queen_controller import QueenController
from BuggersBot.micro.zergling_controller import ZerglingController
from BuggersBot.micro.overlord_controller import OverlordController


class ArmyController:
    def __init__(self, bot):
        self.bot = bot
        self.queen_controller = QueenController(bot)
        self.zergling_controller = ZerglingController(bot)
        self.overlord_controller = OverlordController(bot)

    async def step(self):
        await self.queen_controller.queen_behavior()
        await self.zergling_controller.step()
        await self.overlord_controller.step()
        await self.attack_strategy()

    async def attack_strategy(self):
        # {UNIT: [n to fight, n to defend]}
        aggressive_units = {ZERGLING: [15, 5],
                            BANELING: [5, 1]
                            }

        for UNIT in aggressive_units:
            if self.bot.units(UNIT).amount > aggressive_units[UNIT][0]:
                for s in self.bot.units(UNIT).idle:
                    await self.bot.do(s.attack(self.find_target()))

            elif self.bot.units(UNIT).amount > aggressive_units[UNIT][1]:
                for s in self.bot.units(UNIT).idle:
                    await self.defend(s)

# utils

    async def defend(self, unit):
        bases = self.bot.globals.bases
        for enemy in self.bot.known_enemy_units:
            dist_to_base = min([enemy.distance_to(base) for base in bases])
            if dist_to_base < 20:
                await self.bot.do(unit.attack(enemy))

    async def patrol(self, unit, locations, attack=False):
        if isinstance(locations, Unit) or isinstance(locations, Units):
            locations = [loc.position for loc in locations]

        dest = random.choice(locations)

        if not attack:
            if unit.is_idle:
                await self.bot.do(unit.move(dest))
        else:
            if unit.is_idle:
                await self.bot.do(unit.attack(dest))

    def find_target(self):
        if len(self.bot.known_enemy_units) > 0:
            return random.choice(self.bot.known_enemy_units)
        elif len(self.bot.known_enemy_structures) > 0:
            return random.choice(self.bot.known_enemy_structures)
        else:
            return self.bot.enemy_start_locations[0]
