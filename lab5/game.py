import time

from matplotlib import pyplot as plt
from matplotlib.animation import FuncAnimation

from exceptions import TlaregHitStriga, StrigaHitTlareg
from game_map import GameMap
from striga import Striga
from tlareg import Tlareg
from utils import GameParameters


class Game:

    def __init__(self, game_map: GameMap, tlareg: Tlareg, striga: Striga, config: GameParameters):
        self.game_map = game_map
        self.tlareg = tlareg
        self.striga = striga
        self.config = config

        self.tlareg_counter = config.tlareg_counter_start
        self.striga_lives = config.striga_lives
        self.striga_castle_counter = 0
        self.anim = None

    def kill_tlareg(self, message='Striga killed Tlareg'):
        self.anim.event_source.stop()
        print(message)
        # self.game_map.tlareg = None

    def kill_striga(self, message='Tlareg killed Striga'):
        self.anim.event_source.stop()
        print(message)
        # self.game_map.striga = None

    def simulate_turn(self):
        self.tlareg_counter -= 1
        if self.tlareg_counter == 0:
            self.kill_tlareg(f'Tlareg died after {self.config.tlareg_counter_start} turns without hitting Striga :(')

        # witcher
        try:
            self.tlareg.move()
        except StrigaHitTlareg:
            self.kill_tlareg()
        except TlaregHitStriga:
            self.tlareg_counter = self.config.tlareg_counter_start
            self.striga_lives -= 1
            if self.striga_lives > 0:
                self.striga.go_to_castle()
                self.striga_castle_counter = self.config.striga_castle_time
            else:
                self.kill_striga()
                return

        # striga
        if self.striga_castle_counter > 0:
            self.striga_castle_counter -= 1
            if self.striga_castle_counter == 0:
                while self.game_map.striga == self.game_map.castle:
                    self.striga.leave_castle()
        else:
            try:
                self.striga.move()
            except StrigaHitTlareg:
                self.kill_tlareg()

    def animate(self, interval=200):
        fig = plt.figure()
        im = plt.imshow(self.game_map.get_imshow_data(), cmap=GameMap.colormap, norm=GameMap.norm)
        fig.gca().invert_yaxis()
        fig.gca().axis('off')
        fig.tight_layout()

        self.anim = FuncAnimation(fig, self.animate_frame, fargs=[im], interval=interval)
        plt.show()

    def animate_frame(self, i, im):
        try:
            self.simulate_turn()
            im.set_array(self.game_map.get_imshow_data())
        except Exception as e:
            print(e)
            print(e.with_traceback())
