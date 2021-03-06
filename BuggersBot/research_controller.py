"""
Controls research capabilities (a verbose task) per the current
strategy

self.<X>_research_priority should be dictated in strategy_controller.py
"""

from sc2.constants import *


class ResearchController:
    def __init__(self, bot):
        self.bot = bot
        self.checker = bot.checker

        self.upgrades = {
            'ground_melee': [
                RESEARCH_ZERGMELEEWEAPONSLEVEL1,
                RESEARCH_ZERGMELEEWEAPONSLEVEL2,
                RESEARCH_ZERGMELEEWEAPONSLEVEL3
            ],
            'ground_missile': [
                RESEARCH_ZERGMISSILEWEAPONSLEVEL1,
                RESEARCH_ZERGMISSILEWEAPONSLEVEL2,
                RESEARCH_ZERGMISSILEWEAPONSLEVEL3
            ],
            'ground_armor': [
                RESEARCH_ZERGGROUNDARMORLEVEL1,
                RESEARCH_ZERGGROUNDARMORLEVEL2,
                RESEARCH_ZERGGROUNDARMORLEVEL3
            ]
        }

        self.upgrade_names = {
                RESEARCH_ZERGMELEEWEAPONSLEVEL1: 'GROUND MELEE 1',
                RESEARCH_ZERGMELEEWEAPONSLEVEL2: 'GROUND MELEE 2',
                RESEARCH_ZERGMELEEWEAPONSLEVEL3: 'GROUND MELEE 3',

                RESEARCH_ZERGMISSILEWEAPONSLEVEL1: 'GROUND MISSILE 1',
                RESEARCH_ZERGMISSILEWEAPONSLEVEL2: 'GROUND MISSILE 2',
                RESEARCH_ZERGMISSILEWEAPONSLEVEL3: 'GROUND MISSILE 3',

                RESEARCH_ZERGGROUNDARMORLEVEL1: 'GROUND ARMOR 1',
                RESEARCH_ZERGGROUNDARMORLEVEL2: 'GROUND ARMOR 2',
                RESEARCH_ZERGGROUNDARMORLEVEL3: 'GROUND ARMOR 3'
        }

        self.evo_research_priority = ['ground_melee', 'ground_armor', 'ground_missile']

    async def step(self):
        await self.manage_evo_upgrades()

    async def manage_evo_upgrades(self):
        for evo in self.bot.units(UnitTypeId.EVOLUTIONCHAMBER).ready.noqueue:
            abilities = await self.bot.get_available_abilities(evo)

            for upgrade_type in self.evo_research_priority:
                for upgrade in self.upgrades[upgrade_type]:
                    if upgrade in abilities and self.checker.research(upgrade):
                        await self.bot.do(evo(upgrade))
