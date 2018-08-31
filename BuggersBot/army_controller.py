from sc2.constants import *

from .queen_controller import QueenController


class ArmyController:
    def __init__(self, bot):
        self.bot = bot
        self.queen_controller = QueenController(bot)

    def init(self):
        self.map_center = self.bot.game_info.map_center

    async def step(self):
        await self.queen_controller.queen_behavior()

    async def defend(self, unit):
        bases = self.bot.building_controller.bases
        for enemy in self.bot.known_enemy_units:
            dist_to_base = min([enemy.distance_to(base) for base in bases])
            if dist_to_base < 30:
                await self.bot.do(unit.attack(enemy))

    async def patrol(self, unit):
        if unit.is_idle:
            await self.bot.do(unit.move(self.bot.townhalls.random.position))