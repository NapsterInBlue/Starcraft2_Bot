import sys

import sc2
from sc2 import run_game, maps, Race, Difficulty
from sc2.player import Bot, Computer

from examples.zerg.hydralisk_push import Hydralisk
from examples.baneling_bust import BanelingBustBot

from protossbot import NickProtossBot
from zergbot import NickZergBot
from workerrush import WorkerRushBot


def resolve_args():
    bot = sys.argv[1].lower()

    if bot == 'protoss':
        return Race.Protoss, NickProtossBot()
    elif bot == 'rush':
        return Race.Zerg, WorkerRushBot()
    elif bot == 'bane':
        return Race.Zerg, BanelingBustBot()
    elif bot == 'hydra':
        return Race.Zerg, Hydralisk()
    elif bot == 'zerg':
        return Race.Zerg, NickZergBot()


if __name__ == '__main__':
    selectedBot = resolve_args()

    run_game(maps.get("AbyssalReefLE"), [
        Bot(*selectedBot),
        Computer(Race.Terran, Difficulty.Medium)
        ], realtime=False)
