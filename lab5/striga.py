import random

from game_map import GameMap
from utils import Direction, Action, Position


class Striga:

    def __init__(self, game_map):
        self.game_map = game_map

    def reset(self):
        raise NotImplementedError

    def move(self):
        raise NotImplementedError

    def go_to_castle(self):
        self.game_map.move_striga_to_castle()

    def leave_castle(self):
        raise NotImplementedError


class StrigaDeterministic(Striga):
    """
        Fully deterministic
    """

    def __init__(self, game_map: GameMap, start_idx=10):
        super().__init__(game_map)
        self.start_idx = start_idx
        self.idx = start_idx
        self.positions = [(1, 0), (2, 0), (3, 0), (3, 0), (4, 0), (4, 1), (4, 1), (4, 2), (4, 3), (4, 4), (4, 5),
                          (4, 6), (4, 6), (3, 6), (2, 6), (1, 6), (1, 6), (1, 5), (1, 4), (1, 4), (1, 3), (1, 2),
                          (1, 1)]
        self.actions = [Action.MOVE_RIGHT, Action.MOVE_RIGHT, Action.ATTACK, Action.MOVE_RIGHT, Action.MOVE_UP,
                        Action.ATTACK, Action.MOVE_UP, Action.MOVE_UP, Action.MOVE_UP, Action.MOVE_UP, Action.MOVE_UP,
                        Action.ATTACK, Action.MOVE_LEFT, Action.MOVE_LEFT, Action.MOVE_LEFT, Action.ATTACK,
                        Action.MOVE_DOWN, Action.MOVE_DOWN, Action.ATTACK, Action.MOVE_DOWN, Action.MOVE_DOWN,
                        Action.MOVE_DOWN, Action.MOVE_DOWN]

        # do not start with attack after leaving the castle
        self.possible_start_indices = [i for i in range(len(self.actions)) if self.actions[i] != Action.ATTACK]

    def reset(self):
        self.idx = self.start_idx

    def move(self):
        action = self.actions[self.idx]
        if action == Action.ATTACK:
            self.game_map.striga_attack()
        else:
            direction = action.to_direction()
            # Do not enter fields occupied by Tlareg
            if self.game_map.striga + direction == self.game_map.tlareg:
                return
            self.game_map.move_striga(action.to_direction())
        self.idx = (self.idx + 1) % len(self.actions)

    def leave_castle(self):
        new_idx = random.choice(self.possible_start_indices)
        position = Position(self.positions[new_idx][0], self.positions[new_idx][1])
        while position == self.game_map.tlareg:
            new_idx = random.choice(self.possible_start_indices)
            position = Position(self.positions[new_idx][0], self.positions[new_idx][1])

        self.game_map.striga = position
        self.idx = new_idx


class StrigaStochastic(Striga):
    """
    Striga moves randomly and slightly prefers to move in the same direction as previously. Striga bounces off the
    edges of the map and walls. Striga attacks with selected probability.
    """

    def __init__(self, game_map, attack_probability: float = 0.15, prev_direction: Direction = Direction.UP):
        super().__init__(game_map)
        self.attack_probability = attack_probability
        self.prev_direction = prev_direction

        self.start_prev_direction = prev_direction

    def reset(self):
        self.prev_direction = self.start_prev_direction

    def move(self):
        if random.uniform(0, 1) < self.attack_probability:  # attack
            self.game_map.striga_attack()
        else:  # move
            directions = [self.prev_direction, Direction.get_random()]
            direction = random.choice(directions)
            new_pos = self.game_map.striga + direction

            # Reverse the direction if encountered a wall or end of the map
            if not new_pos.is_valid(self.game_map):
                direction = direction.get_opposite()
                new_pos = self.game_map.striga + direction

            # Move if the new position is valid and Tlareg is not there
            if new_pos.is_valid(self.game_map) and new_pos != self.game_map.tlareg:
                self.game_map.move_striga(direction)
                self.prev_direction = direction

    def leave_castle(self):
        self.game_map.striga_leave_castle()
