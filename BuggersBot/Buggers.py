import random

import sc2

from sc2.position import Point2
from sc2.constants import *

from .coordinator import Coordinator
from .opener import Opener
from .unit_creation_controller import UnitCreationController
from .army_controller import ArmyController
from .worker_controller import WorkerController
from .event_manager import EventManager
from .building_controller import BuildingController


class Buggers(sc2.BotAI):
    def __init__(self):
        self.ITERATIONS_PER_MINUTE = 165
        self.OPENER = True
        self.AMASS_ARMY = False

        self.coordinator = Coordinator(bot=self)
        self.opener = Opener(bot=self)
        self.unit_creation_controller = UnitCreationController(bot=self)
        self.army_controller = ArmyController(bot=self)
        self.building_controller = BuildingController(bot=self)
        self.worker_controller = WorkerController(bot=self)
        self.event_manager = EventManager()

        self.order_queue = []

    def on_start(self):
        self.army_controller.init()

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

        await self.coordinator.step()

        if self.OPENER:
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
        if self.coordinator.game_time_in_mins > 3 and not self.AMASS_ARMY:
            await self.coordinator.toggle_amass_army(True)