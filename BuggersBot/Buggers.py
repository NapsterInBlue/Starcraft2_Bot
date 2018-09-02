import random
import sys

import sc2

from sc2.position import Point2
from sc2.constants import *

from .event_manager import EventManager
from .checker import Checker
from .calculator import Calculator
from .globals import Globals

from .opener import Opener

from .strategy_controller import StrategyController
from .unit_creation_controller import UnitCreationController
from .scouting_controller import ScoutingController
from .army_controller import ArmyController
from .worker_controller import WorkerController
from .research_controller import ResearchController
from .building_controller import BuildingController


class Buggers(sc2.BotAI):
    def __init__(self, verbose=True):
        self.verbose = verbose

        self.event_manager = EventManager()
        self.checker = Checker(bot=self)
        self.calculator = Calculator(bot=self)
        self.globals = Globals(bot=self)
        self.opener = Opener(bot=self)

        self.strategy_controller = StrategyController(bot=self)
        self.scouting_controller = ScoutingController(bot=self)
        self.unit_creation_controller = UnitCreationController(bot=self)
        self.army_controller = ArmyController(bot=self)
        self.worker_controller = WorkerController(bot=self)
        self.research_controller = ResearchController(bot=self)
        self.building_controller = BuildingController(bot=self)

        self.order_queue = []

    def on_start(self):
        self.event_manager.add_event(self.strategy_controller.step, 0.5)
        self.event_manager.add_event(self.scouting_controller.step, 0.1)
        self.event_manager.add_event(self.unit_creation_controller.step, 0.1)
        self.event_manager.add_event(self.army_controller.step, 0.1)
        self.event_manager.add_event(self.worker_controller.step, 0.25)
        self.event_manager.add_event(self.research_controller.step, 2)
        self.event_manager.add_event(self.building_controller.step, 2)

    async def on_step(self, iteration):
        if iteration == 0:
            if self.verbose:
                self.globals.init()

                print('\n-------------\n')
                print('Starting bot')
                print('\n-------------\n')

            return

        await self.globals.step()

        if self.strategy_controller.OPENER:
            await self.opener.step()

        else:
            events = self.event_manager.get_current_events(self.time)
            for event in events:
                await event()

        await self.execute_order_queue()

    async def do(self, action):
        self.order_queue.append(action)

    async def execute_order_queue(self):
        await self._client.actions(self.order_queue, game_data=self._game_data)
        self.order_queue = []
