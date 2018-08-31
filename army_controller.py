from sc2.constants import *


class ArmyController:
    def __init__(self, bot):
        self.bot = bot

    async def defend(self, unit):
        for enemy in self.bot.known_enemy_units:
            dist_to_base = min([enemy.distance_to(base) for base in self.bot.bases])
            if dist_to_base < 30:
                await self.bot.do(unit.attack(enemy))

    async def patrol(self, unit):
        if unit.is_idle:
            await self.bot.do(unit.move(self.bot.townhalls.random.position))