from sc2.constants import *


class UnitCreationController:
    def __init__(self, bot):
        self.bot = bot
        self.larvae = None

    async def step(self):
        self.update_larvae()
        await self.build_offensive_force()

    def update_larvae(self):
        self.larvae = self.bot.units(LARVA)

    async def build_offensive_force(self):
        if self.bot.coordinator.unit_check(OVERLORD, supply_left_lt=5):
            await self.bot.do(self.bot.globals.larvae.random.train(OVERLORD))

        if self.bot.coordinator.unit_check(ZERGLING, max_units=50):
            await self.bot.do(self.bot.globals.larvae.random.train(ZERGLING))

        if self.bot.worker_controller.optimize_worker_ct():
            await self.bot.do(self.bot.globals.larvae.random.train(DRONE))

    def find_amass_army_rally_point(self):
        """Figure out where to send new units when intentionally building an army"""
        enemy_hq = self.bot.enemy_start_locations[0]
        satellite = self.bot.townhalls.closest_to(enemy_hq)
        point = satellite.position.towards(self.bot._game_info.map_center, distance=5, limit=True)
        print("Setting Rally point to {}".format(point.position.to2))
        return point