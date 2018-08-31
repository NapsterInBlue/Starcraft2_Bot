import random

import sc2

from sc2.position import Point2
from sc2.constants import *

from .coordinator import Coordinator
from .opener import Opener
from .army_controller import ArmyController
from .worker_controller import WorkerController
from .event_manager import EventManager


class Buggers(sc2.BotAI):
    def __init__(self):
        self.ITERATIONS_PER_MINUTE = 165
        self.OPENER = True
        self.AMASS_ARMY = False

        self.coordinator = Coordinator(bot=self)
        self.opener = Opener(bot=self)
        self.army_controller = ArmyController(bot=self)
        self.worker_controller = WorkerController(bot=self)
        self.event_manager = EventManager()

        self.order_queue = []

    def on_start(self):
        self.army_controller.init()

        self.event_manager.add_event(self.worker_controller.step, 0.1)
        self.event_manager.add_event(self.army_controller.step, 0.1)

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
            await self.build_offensive_force()
            await self.attack()
            await self.assign_rally_points()
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

    async def build_offensive_force(self):
        if self.coordinator.check_unit_build(OVERLORD, supply_left_lt=5):
            await self.do(self.larvae.random.train(OVERLORD))

        if self.coordinator.check_unit_build(ZERGLING, max_units=50):
            await self.do(self.larvae.random.train(ZERGLING))

        if self.worker_controller.optimize_worker_ct():
            await self.do(self.larvae.random.train(DRONE))

    async def toggle_amass_army(self, value):
        self.AMASS_ARMY = value
        del self.hatcheryRallyPointsSet

    async def assign_rally_points(self):
        """Rally workers to nearest minerals. Rally units closeby."""
        if hasattr(self, "hatcheryRallyPointsSet"):
            for hatch in self.townhalls:
                if hatch.tag not in self.hatcheryRallyPointsSet:
                    mf = self.state.mineral_field.closest_to(hatch.position.to2.offset(Point2((0, -3))))
                    err = await self.do(hatch(RALLY_WORKERS, mf))
                    if not err:
                        mfs = self.state.mineral_field.closer_than(10, hatch.position.to2)
                        if self.AMASS_ARMY:
                            loc = self.coordinator.find_amass_army_rally_point()
                        elif mfs.exists:
                            loc = self.coordinator.center_of_units(mfs)
                        err = await self.do(hatch(RALLY_UNITS, loc))
                        if not err:
                            self.hatcheryRallyPointsSet[hatch.tag] = loc
        else:
            self.hatcheryRallyPointsSet = {}

    def find_target(self):
        if len(self.known_enemy_units) > 0:
            return random.choice(self.known_enemy_units)
        elif len(self.known_enemy_structures) > 0:
            return random.choice(self.known_enemy_structures)
        else:
            return self.enemy_start_locations[0]

    async def attack(self):
        # {UNIT: [n to fight, n to defend]}
        aggressive_units = {ZERGLING: [15, 5],
                            }

        for UNIT in aggressive_units:
            if self.units(UNIT).amount > aggressive_units[UNIT][0]:
                for s in self.units(UNIT).idle:
                    await self.do(s.attack(self.find_target()))

            elif self.units(UNIT).amount > aggressive_units[UNIT][1]:
                for s in self.units(UNIT).idle:
                    await self.army_controller.defend(s)

    async def game_time(self):
        if self.coordinator.game_time_in_mins > 3 and not self.AMASS_ARMY:
            await self.toggle_amass_army(True)