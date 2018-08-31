import random

from sc2.constants import *

from .queen_controller import QueenController


class ArmyController:
    def __init__(self, bot):
        self.bot = bot
        self.queen_controller = QueenController(bot)

    async def step(self):
        await self.queen_controller.queen_behavior()
        await self.attack_strategy()

    async def attack_strategy(self):
        # {UNIT: [n to fight, n to defend]}
        aggressive_units = {ZERGLING: [15, 5],
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
            if dist_to_base < 30:
                await self.bot.do(unit.attack(enemy))

    async def patrol(self, unit):
        if unit.is_idle:
            await self.bot.do(unit.move(self.bot.townhalls.random.position))

    def find_target(self):
        if len(self.bot.known_enemy_units) > 0:
            return random.choice(self.bot.known_enemy_units)
        elif len(self.bot.known_enemy_structures) > 0:
            return random.choice(self.bot.known_enemy_structures)
        else:
            return self.bot.enemy_start_locations[0]