from matplotlib import pyplot as plt
from matplotlib.animation import FuncAnimation

from exceptions import TlaregHitStriga, StrigaHitTlareg
from game_map import GameMap
from striga import Striga, StrigaDeterministic, StrigaStochastic


class Game:

    def __init__(self, game_map: GameMap, striga: Striga, striga_castle_time: int = 3):
        self.game_map = game_map
        self.striga = striga
        self.striga_castle_time = striga_castle_time

        self.striga_castle_counter = 0

    def simulate_turn(self):
        # TODO: witcher
        # striga
        if self.striga_castle_counter > 0:
            self.striga_castle_counter -= 1
            if self.striga_castle_counter == 0:
                self.striga.leave_castle()
        else:
            try:
                self.striga.move()
            except StrigaHitTlareg:
                print('Striga hit Tlareg')
                pass
            except TlaregHitStriga:
                print('Tlareg hit Striga')
                self.striga.go_to_castle()
                self.striga_castle_counter = self.striga_castle_time

    def animate(self, interval=200):
        fig = plt.figure()
        im = plt.imshow(self.game_map.get_imshow_data(), cmap=GameMap.colormap)
        fig.gca().invert_yaxis()
        fig.gca().axis('off')
        fig.tight_layout()

        _ = FuncAnimation(fig, self.animate_frame, fargs=[im], interval=interval)
        plt.show()

    def animate_frame(self, i, im):
        self.simulate_turn()
        im.set_array(self.game_map.get_imshow_data())


if __name__ == '__main__':
    some_map = GameMap(20, 20, (14, 13), (15, 15),
                       [(19, 19), (18, 19), (17, 19), (17, 18), (17, 17), (18, 17), (19, 17), (19, 18)],
                       (18, 18))

    # some_striga = StrigaDeterministic(some_map)
    some_striga = StrigaStochastic(some_map)

    game = Game(some_map, some_striga, striga_castle_time=10)
    game.animate()
