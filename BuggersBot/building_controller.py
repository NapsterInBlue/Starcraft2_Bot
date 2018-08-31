from sc2.constants import *


class BuildingController:
    def __init__(self, bot):
        self.bot = bot

        self.bases = []

    async def step(self):
        await self.update_base_list()

    async def update_base_list(self):
        for base in self.bot.townhalls:
            if base not in self.bases:
                self.bases.append(base)
