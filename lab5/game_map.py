import random

from matplotlib import colors

from exceptions import TlaregHitStriga, StrigaHitTlareg
from utils import Position, Direction


class GameMap:
    colormap = colors.ListedColormap(['black', 'grey', 'green', 'red'])

    def __init__(self, width: int, height: int, tlareg: tuple[int, int], striga: tuple[int, int],
                 walls: list[tuple[int, int]], castle: tuple[int, int], striga_lives: int = 3,
                 striga_momentum: Direction = Direction.UP):
        self.width = width
        self.height = height
        self.tlareg = Position(tlareg[0], tlareg[1])
        self.striga = Position(striga[0], striga[1])
        self.walls = {Position(wall[0], wall[1]) for wall in walls}
        self.castle = Position(castle[0], castle[1])
        self.striga_lives = striga_lives
        self.striga_momentum = striga_momentum

    def get_imshow_data(self):
        data = [[0 for _ in range(self.width)] for _ in range(self.height)]
        for wall in self.walls:
            data[wall.y][wall.x] = 1
        if self.tlareg is not None:
            data[self.tlareg.y][self.tlareg.x] = 2
        if self.striga is not None:
            data[self.striga.y][self.striga.x] = 3
        return data

    def get_possible_moves(self, position: Position):
        moves = set()
        for direction in Direction:
            new_position = position + direction
            if new_position.is_valid(self):
                moves.add(direction)
        return moves

    def move_tlareg(self, direction: Direction):
        """
            It is assumed that the move is possible.
        """
        self.tlareg += direction
        if self.tlareg == self.striga:
            raise StrigaHitTlareg

    def move_striga(self, direction: Direction):
        """
            It is assumed that the move is possible.
        """
        self.striga += direction
        self.striga_momentum = direction
        if self.striga == self.tlareg:
            raise TlaregHitStriga

    def move_striga_to_castle(self):
        self.striga = self.castle

    def move_striga_to_random(self):
        position = Position(-1, -1)
        while not position.is_valid(self):
            position = Position(random.randint(0, self.width), random.randrange(0, self.height))
        self.striga = position

    def tlareg_attack(self):
        if abs(self.tlareg.x - self.striga.x) <= 1 and abs(self.tlareg.y - self.striga.y) <= 1:
            self.tlareg = None
            raise TlaregHitStriga

    def striga_attack(self):
        attacked_positions = []
        if self.striga_momentum.value[0] == 0:
            attacked_positions += [Position(i, self.striga_momentum.value[1]) for i in range(-1, 2)]
        else:
            attacked_positions += [Position(self.striga_momentum.value[0], i) for i in range(-1, 2)]
        if self.tlareg in attacked_positions:
            self.tlareg = None
            raise StrigaHitTlareg
