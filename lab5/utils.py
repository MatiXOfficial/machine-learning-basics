import random
from dataclasses import dataclass
from enum import Enum


@dataclass
class GameParameters:
    striga_lives: int = 3
    tlareg_counter_start: int = 1000
    striga_castle_time: int = 3


class Direction(Enum):
    UP = (0, 1)
    LEFT = (-1, 0)
    DOWN = (0, -1)
    RIGHT = (1, 0)

    def get_opposite(self):
        return Direction((self.value[0] * (-1), self.value[1] * (-1)))

    def get_next(self):
        members = list(self.__class__)
        idx = members.index(self)
        return members[(idx + 1) % len(members)]

    @staticmethod
    def get_random():
        return random.choice(list(Direction))


class Action(Enum):
    MOVE_UP = 1
    MOVE_LEFT = 2
    MOVE_DOWN = 3
    MOVE_RIGHT = 4
    ATTACK = 5

    def to_direction(self):
        if self == Action.MOVE_UP:
            return Direction.UP
        elif self == Action.MOVE_LEFT:
            return Direction.LEFT
        elif self == Action.MOVE_DOWN:
            return Direction.DOWN
        elif self == Action.MOVE_RIGHT:
            return Direction.RIGHT
        else:
            raise ValueError('Wrong value')

    @staticmethod
    def from_direction(direction: Direction):
        if direction == Direction.UP:
            return Action.MOVE_UP
        elif direction == Direction.LEFT:
            return Action.MOVE_LEFT
        elif direction == Direction.DOWN:
            return Action.MOVE_DOWN
        elif direction == Direction.RIGHT:
            return Action.MOVE_RIGHT
        else:
            raise ValueError('Wrong argument')

    def __repr__(self):
        return self.name


class Position:

    def __init__(self, x: int, y: int):
        self.x = x
        self.y = y

    def move(self, direction: Direction):
        self.x += direction.x
        self.y += direction.y

    def is_in_map(self, game_map):
        return 0 <= self.x < game_map.width and 0 <= self.y < game_map.height

    def is_valid(self, game_map):
        return self.is_in_map(game_map) and self not in game_map.walls

    def get_dist(self):
        return abs(self.x) + abs(self.y)

    def __add__(self, other):
        if isinstance(other, Direction):
            return Position(self.x + other.value[0], self.y + other.value[1])
        else:
            return Position(self.x + other.x, self.y + other.y)

    def __sub__(self, other):
        if isinstance(other, Direction):
            return Position(self.x - other.value[0], self.y - other.value[1])
        else:
            return Position(self.x - other.x, self.y - other.y)

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    def __hash__(self):
        return (self.x, self.y).__hash__()

    def __repr__(self):
        return f'({self.x}, {self.y})'


class State:

    def __init__(self, tlareg: Position, striga: Position):
        self.tlareg = tlareg
        self.striga = striga

    def __eq__(self, other):
        return self.tlareg == other.tlareg and self.striga == other.striga

    def __hash__(self):
        return (self.tlareg + self.striga).__hash__()

    def __repr__(self):
        return f'T: ({self.tlareg.x}, {self.tlareg.y}), S: ({self.striga.x}, {self.striga.y})'
