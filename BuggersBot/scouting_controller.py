import random
from sc2.constants import *


class ScoutingController:
    def __init__(self, bot):
        self.bot = bot
        self.verbose = self.bot.verbose

        self.overlords = None

        self.lings = set()
        self.NUM_LINGS = 3

        self.scout_timer = 0
        self.SCOUT_INTERVAL = 30

    async def step(self):
        await self.assign_ling_scouts()

    async def assign_ling_scouts(self):
        current_time = self.bot.time
        if current_time - self.scout_timer > self.SCOUT_INTERVAL:
            self.scout_timer = self.bot.time

            n_scouting_lings_assigned = len(self.lings)
            missing_scouting_lings = self.NUM_LINGS - n_scouting_lings_assigned

            for scouting_ling_tag in list(self.lings):
                unit = self.bot.units.find_by_tag(scouting_ling_tag)

                if unit is not None:
                    target = random.sample(list(self.bot.expansion_locations), k=1)[0]
                    await self.bot.do(unit.attack(target))
                else:
                    self.scouting_lings.remove(unit)
                    missing_scouting_lings += 1

            if missing_scouting_lings > 0:
                idle_lings = self.bot.units(ZERGLING).idle

                if idle_lings.exists:
                    if self.verbose:
                        print('%6.2f Scouting' % (self.bot.time))

                    for _ in range(missing_scouting_lings):
                        if self.bot.units(ZERGLING).amount > 0:
                            ling = idle_lings.furthest_to(self.bot.globals.hq)
                        else:
                            ling = idle_lings.random

                        if ling:
                            target = random.sample(list(self.bot.expansion_locations), k=1)[0]
                            await self.bot.do(ling.attack(target))

                        idle_lings = self.bot.units(ZERGLING).idle
                        if not idle_lings.exists:
                            break

                else:
                    pass
