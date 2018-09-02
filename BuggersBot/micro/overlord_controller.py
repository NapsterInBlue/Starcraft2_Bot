import random
from sc2.constants import *


class OverlordController:
    def __init__(self, bot):
        self.bot = bot
        self.scouting_controller = self.bot.scouting_controller

    async def step(self):
        await self.scout()

    async def scout(self):
        for overlord in self.bot.units(OVERLORD).idle:
            if overlord not in self.scouting_controller.overlords:
                self.scouting_controller.overlords.add(overlord)

            available_expansions = set(self.bot.globals.enemy_expansions) - self.scouting_controller.scouted_expansions
            selection = random.sample(list(available_expansions), k=1)[0]
            await self.bot.do(overlord.move(selection))
            self.scouting_controller.overlords.add(overlord)
            self.scouting_controller.scouted_expansions.add(selection)
