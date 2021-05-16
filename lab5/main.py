from game import Game
from game_map import GameMap
import time

from striga import StrigaDeterministic, StrigaStochastic
from tlareg import TlaregSarsa, TlaregQLearning
from utils import GameParameters

# Initialisation

config = GameParameters(striga_lives=5, tlareg_counter_start=1000, striga_castle_time=5)

width = 8
height = 8

tlareg_start = (1, 1)
striga_start = (4, 5)

# walls and castle walls
walls = [(3, 1), (3, 2), (3, 3), (3, 5), (2, 5)]
walls += [(width - i, height - j) for j in [1, 2, 3] for i in [1, 2, 3]]
walls.remove((width - 2, height - 2))

castle = (width - 2, height - 2)

game_map = GameMap(width, height, tlareg_start, striga_start, walls, castle)

# Striga and Tlareg models

# striga = StrigaDeterministic(game_map)
striga = StrigaStochastic(game_map, attack_probability=0.3)

# tlareg = TlaregSarsa(game_map, striga, config)
tlareg = TlaregQLearning(game_map, striga, config)

n_games = 5000
report_step = n_games // 10

tlareg.init_Q()

start_time = time.time()
# tlareg.learn(n_games=n_games, alpha=0.9, gamma=0.9, start_eps=0.99, end_eps=0.01, report_step=report_step)
tlareg.learn(n_games=n_games, alpha=0.1, gamma=0.1, start_eps=0.9, end_eps=0.01, report_step=report_step)

# tlareg.learn(n_games=n_games, alpha=0.8, gamma=0.9, start_eps=0.99, end_eps=0.01, report_step=report_step)

end_time = time.time()
elapsed = end_time - start_time
print(f'-----{elapsed:5.1f} s')

# Animation

while True:
    game_map.reset(tlareg_start, striga_start)
    striga.reset()

    game = Game(game_map, tlareg, striga, config)
    game.animate(1)
