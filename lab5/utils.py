import random
from enum import Enum


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
