import random

from game_map import GameMap
from utils import Direction


class Striga:

    def __init__(self, game_map):
        self.game_map = game_map

    def move(self):
        raise NotImplementedError

    def go_to_castle(self):
        self.game_map.move_striga_to_castle()

    def leave_castle(self):
        self.game_map.move_striga_to_random()


class StrigaDeterministic(Striga):
    """
        One turn: Striga moves n times in a particular direction, attacks and turns left. Striga performs the turns
        with n being incremented from start (inclusive) to end (exclusive), then going back to start, etc. Striga
        bounces off the edges of the map and walls.
    """

    def __init__(self, game_map: GameMap, start: int = 1, end: int = 5, direction: Direction = Direction.UP):
        super().__init__(game_map)
        self.start = start
        self.end = end
        self.direction = direction

        self.n_moves = start
        self.curr_moves = start

    def move(self):
        if self.curr_moves > 0:  # move
            if not (self.game_map.striga + self.direction).is_valid(self.game_map):
                self.direction = self.direction.get_opposite()

            self.game_map.move_striga(self.direction)

            self.curr_moves -= 1
        else:  # attack
            self.game_map.striga_attack()

            self.n_moves += 1
            if self.n_moves == self.end:
                self.n_moves = self.start

            self.curr_moves = self.n_moves
            self.direction = self.direction.get_next()


class StrigaStochastic(Striga):
    """
    Striga moves randomly and slightly prefers to move in the same direction as previously. Striga bounces off the
    edges of the map and walls. Striga attacks with selected probability.
    """

    def __init__(self, game_map, attack_probability: float = 0.15, prev_direction: Direction = Direction.UP):
        super().__init__(game_map)
        self.attack_probability = attack_probability
        self.prev_direction = prev_direction

    def move(self):
        if random.uniform(0, 1) < self.attack_probability:  # attack
            self.game_map.striga_attack()
        else:  # move
            directions = [self.prev_direction, Direction.get_random()]
            direction = random.choice(directions)
            if not (self.game_map.striga + direction).is_valid(self.game_map):
                direction = direction.get_opposite()

            self.game_map.move_striga(direction)
            self.prev_direction = direction
