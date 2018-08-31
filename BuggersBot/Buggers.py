import random

import sc2

from sc2.position import Point2
from sc2.constants import *

from .coordinator import Coordinator
from .globals import Globals

from .opener import Opener
from .unit_creation_controller import UnitCreationController
from .army_controller import ArmyController
from .worker_controller import WorkerController
from .event_manager import EventManager
from .building_controller import BuildingController


class Buggers(sc2.BotAI):
    def __init__(self):
        self.globals = Globals(bot=self)
        self.coordinator = Coordinator(bot=self)
        self.opener = Opener(bot=self)
        self.unit_creation_controller = UnitCreationController(bot=self)
        self.army_controller = ArmyController(bot=self)
        self.building_controller = BuildingController(bot=self)
        self.worker_controller = WorkerController(bot=self)
        self.event_manager = EventManager()

        self.order_queue = []

    def on_start(self):
        self.globals.init()

        self.event_manager.add_event(self.globals.step, 0.1)
        self.event_manager.add_event(self.building_controller.step, 0.25)
        self.event_manager.add_event(self.unit_creation_controller.step, 0.1)
        self.event_manager.add_event(self.army_controller.step, 0.1)
        self.event_manager.add_event(self.worker_controller.step, 0.1)

    async def on_step(self, iteration):
        # if iteration == 0:
        #     print(iteration)
        #     await self.chat_send('GL HF!')
        #
        #     return

        await self.globals.step()

        if self.coordinator.OPENER:
            await self.opener.step()

        else:
            await self.game_time()

            events = self.event_manager.get_current_events(self.time)
            for event in events:
                await event()

        await self.execute_order_queue()

    async def do(self, action):
        self.order_queue.append(action)

    async def execute_order_queue(self):
        await self._client.actions(self.order_queue, game_data=self._game_data)
        self.order_queue = []

    async def game_time(self):
        if self.globals.game_time_in_mins > 3 and not self.coordinator.AMASS_ARMY:
            await self.coordinator.toggle_amass_army(True)