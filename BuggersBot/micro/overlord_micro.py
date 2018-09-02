from sc2.constants import *


class ZerglingController:
    def __init__(self, bot):
        self.bot = bot

        self.baneling_ratio = None
        self.BANELING_RATIO = .2
