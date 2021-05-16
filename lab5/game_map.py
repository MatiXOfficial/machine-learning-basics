import random

import matplotlib.pyplot as plt
from matplotlib import colors

from exceptions import TlaregHitStriga, StrigaHitTlareg
from utils import Position, Direction, State


class GameMap:
    colormap = colors.ListedColormap(['black', 'grey', 'green', 'red', 'lime', 'lightcoral'])
    norm = colors.BoundaryNorm([0, 1, 2, 3, 4, 5, 6], colormap.N)

    def __init__(self, width: int, height: int, tlareg: tuple[int, int], striga: tuple[int, int],
                 walls: list[tuple[int, int]], castle: tuple[int, int], striga_momentum: Direction = Direction.UP):
        self.width = width
        self.height = height
        self.tlareg = Position(tlareg[0], tlareg[1])
        self.striga = Position(striga[0], striga[1])
        self.walls = {Position(wall[0], wall[1]) for wall in walls}
        self.castle = Position(castle[0], castle[1])
        self.striga_momentum = striga_momentum

        self.tlareg_attacked_positions = []
        self.striga_attacked_positions = []

        self.tlareg_frequency = [[0 for _ in range(self.height)] for _ in range(self.width)]
        self.tlareg_frequency[self.tlareg.y][self.tlareg.x] = 1

    @property
    def state(self):
        return State(self.tlareg, self.striga)

    def reset(self, tlareg: tuple[int, int], striga: tuple[int, int], striga_momentum: Direction = Direction.UP):
        self.tlareg = Position(tlareg[0], tlareg[1])
        self.striga = Position(striga[0], striga[1])
        self.striga_momentum = striga_momentum

        self.tlareg_attacked_positions = []
        self.striga_attacked_positions = []

    def get_imshow_data(self):
        data = [[0 for _ in range(self.height)] for _ in range(self.width)]

        for wall in self.walls:
            data[wall.y][wall.x] = 1

        if self.tlareg is not None:
            data[self.tlareg.y][self.tlareg.x] = 2
        if self.striga is not None:
            data[self.striga.y][self.striga.x] = 3

        for position in self.tlareg_attacked_positions:
            data[position.y][position.x] = 4
        self.tlareg_attacked_positions = []
        for position in self.striga_attacked_positions:
            data[position.y][position.x] = 5
        self.striga_attacked_positions = []

        return data

    def reset_traleg_frequency(self):
        self.tlareg_frequency = [[0 for _ in range(self.height)] for _ in range(self.width)]
        self.tlareg_frequency[self.tlareg.y][self.tlareg.x] = 1

    def save_traleg_frequency(self, title, directory='./plots/frequency'):
        fig = plt.figure()
        im = plt.imshow(self.tlareg_frequency, cmap='Greens')
        fig.gca().invert_yaxis()
        plt.title(title)
        plt.savefig(directory + f'/{title}.jpg')
        plt.close(fig)

    def get_possible_moves(self, position: Position):
        moves = set()
        for direction in Direction:
            new_position = position + direction
            if new_position.is_valid(self):
                moves.add(direction)
        return moves

    def get_valid_positions(self):
        return [Position(x, y) for x in range(self.width) for y in range(self.height) if Position(x, y).is_valid(self)]

    def move_tlareg(self, direction: Direction):
        """
            It is assumed that the move is possible.
        """
        self.tlareg += direction
        self.tlareg_frequency[self.tlareg.y][self.tlareg.x] += 1
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

    def striga_leave_castle(self):
        positions = [Position(self.width - 4, self.height - i) for i in [1, 2, 3, 4]]
        positions += [Position(self.width - i, self.height - 4) for i in [3, 2, 1]]
        position = random.choice(positions)
        while not position.is_valid(self) or position == self.tlareg:
            position = random.choice(positions)
        self.striga = position

    def tlareg_attack(self):
        attacked_positions = [self.tlareg + Position(i, j) for i in [-1, 0, 1] for j in [-1, 0, 1]]
        attacked_positions.remove(self.tlareg)
        self.tlareg_attacked_positions = list(filter(lambda pos: pos.is_valid(self), attacked_positions))
        if self.striga in self.tlareg_attacked_positions:
            raise TlaregHitStriga

    def striga_attack(self):
        attacked_positions = []
        if self.striga_momentum.value[0] == 0:
            attacked_positions += [self.striga + Position(i, self.striga_momentum.value[1]) for i in [-1, 0, 1]]
        else:
            attacked_positions += [self.striga + Position(self.striga_momentum.value[0], i) for i in [-1, 0, 1]]
        self.striga_attacked_positions = list(filter(lambda pos: pos.is_valid(self), attacked_positions))
        if self.tlareg in attacked_positions:
            self.tlareg = None
            raise StrigaHitTlareg
