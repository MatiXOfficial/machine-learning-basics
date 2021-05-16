import random

import matplotlib.pyplot as plt
import numpy as np
import time

from exceptions import StrigaHitTlareg, TlaregHitStriga
from game_map import GameMap
from striga import Striga
from utils import Action, GameParameters, State


class Tlareg:
    TLAREG_DEAD_REWARD = -1000_000
    TLAREG_KILLED_REWARD = -100_000
    TLAREG_MISSED_REWARD = -50

    STRIGA_MISSED_REWARD = 2
    STRIGA_HIT_REWARD = 10_000
    STRIGA_KILLED_REWARD = 100_000

    GETTING_CLOSER_REWARD = 0.2
    NOT_GETTING_CLOSER_REWARD = -0.1

    def __init__(self, game_map: GameMap, striga: Striga, config: GameParameters):
        self.game_map = game_map
        self.striga = striga
        self.config = config

        self.alpha = None
        self.gamma = None

        self.tlareg_start = (self.game_map.tlareg.x, self.game_map.tlareg.y)
        self.striga_start = (self.game_map.striga.x, self.game_map.striga.y)

        self.tlareg_counter = self.config.tlareg_counter_start
        self.striga_lives = config.striga_lives
        self.striga_castle_counter = 0

        self.Q = None

        self.x_data = None
        self.rewards_data = None
        self.tlareg_life_time_data = None
        self.hits_before_death_data = None

    def choose_action(self, state, eps):
        raise NotImplementedError('Use a child class instead!')

    def reset_parameters(self):
        self.game_map.reset(self.tlareg_start, self.striga_start)
        self.game_map.reset_traleg_frequency()
        self.striga.reset()
        self.tlareg_counter = self.config.tlareg_counter_start
        self.striga_lives = self.config.striga_lives

    def init_Q(self):
        self.Q = dict()
        for tlareg_pos in self.game_map.get_valid_positions():
            for striga_pos in self.game_map.get_valid_positions():
                if tlareg_pos == striga_pos:
                    continue

                state = State(tlareg_pos, striga_pos)
                actions = list(map(lambda d: Action.from_direction(d), self.game_map.get_possible_moves(tlareg_pos)))
                actions += [Action.ATTACK]

                self.Q[state] = dict()
                for action in actions:
                    self.Q[state][action] = 0

    def learn(self, n_games=5000, alpha=0.8, gamma=0.6, start_eps=0.8, end_eps=0.1, report_step=500):
        self.x_data = np.arange(n_games)
        self.rewards_data = [0] * n_games
        self.tlareg_life_time_data = [0] * n_games
        self.hits_before_death_data = [0] * n_games

        self.alpha = alpha
        self.gamma = gamma
        eps = start_eps
        eps_step = (start_eps - end_eps) / (n_games - 1)
        start_time = time.time()
        for i in range(1, n_games + 1):
            self.learning_episode(eps, i - 1)

            if i in [1, 5, 10, 50, 100]:
                self.game_map.save_traleg_frequency(f'it = {i}')

            if i % report_step == 0:
                end_time = time.time()
                elapsed = end_time - start_time
                start_time = end_time
                print(f'{i:5} ({elapsed:2.1f} s): eps: {eps:0.2f}')
                self.game_map.save_traleg_frequency(f'it = {i}')

            eps -= eps_step
            self.reset_parameters()

        self.plot_data()

    def learning_episode(self, eps, it):
        state = self.game_map.state
        action = self.choose_action(state, eps)

        while True:
            reward = 0

            # Tlareg
            self.tlareg_counter -= 1
            if self.tlareg_counter == 0:  # end of the episode, Tlareg loses
                self.update(state, action, Tlareg.TLAREG_DEAD_REWARD, it=it)
                return

            try:
                reward += self.perform_action(action)
            except StrigaHitTlareg:  # end of the episode, Tlareg loses
                self.update(state, action, Tlareg.TLAREG_KILLED_REWARD, it=it)
                return
            except TlaregHitStriga:
                self.hits_before_death_data[it] += 1
                self.tlareg_counter = self.config.tlareg_counter_start
                self.striga_lives -= 1
                if self.striga_lives > 0:
                    self.striga.go_to_castle()
                    self.striga_castle_counter = self.config.striga_castle_time
                    reward += Tlareg.STRIGA_HIT_REWARD
                else:  # end of the episode, Tlareg wins
                    self.update(state, action, Tlareg.STRIGA_KILLED_REWARD, it=it)
                    return

            # striga
            if self.striga_castle_counter > 0:
                self.striga_castle_counter -= 1
                if self.striga_castle_counter == 0:
                    self.striga.leave_castle()
            else:
                try:
                    self.striga.move()
                except StrigaHitTlareg:  # end of the episode, Tlareg loses
                    self.update(state, action, Tlareg.TLAREG_KILLED_REWARD, it=it)
                    return

            # end of turn, update
            next_state = self.game_map.state
            next_action = self.choose_action(next_state, eps)
            self.update(state, action, reward, next_state, next_action, it=it)
            state = next_state
            action = next_action

            self.tlareg_life_time_data[it] += 1

    def update(self, s, a, r, n_s=None, n_a=None, it=None):
        if it is not None:
            self.rewards_data[it] += r

        if n_s is not None:
            self.Q[s][a] += self.alpha * (r + self.gamma * self.Q[n_s][n_a] - self.Q[s][a])
        else:
            self.Q[s][a] += self.alpha * (r - self.Q[s][a])

    def get_best_action(self, state):
        max_value = max(self.Q[state].values())
        best_actions = [action for action, value in self.Q[state].items() if value == max_value]
        return random.choice(best_actions)

    def perform_action(self, action):
        if action == Action.ATTACK:
            self.game_map.tlareg_attack()
            return Tlareg.TLAREG_MISSED_REWARD
        else:
            prev_diff = self.game_map.tlareg - self.game_map.striga
            self.game_map.move_tlareg(action.to_direction())
            new_diff = prev_diff + action.to_direction()
            if new_diff.get_dist() < prev_diff.get_dist():
                return Tlareg.GETTING_CLOSER_REWARD
            else:
                return Tlareg.NOT_GETTING_CLOSER_REWARD

    def move(self):
        state = State(self.game_map.tlareg, self.game_map.striga)
        action = self.get_best_action(state)
        if action == Action.ATTACK:
            self.game_map.tlareg_attack()
        else:
            self.game_map.move_tlareg(action.to_direction())

    def plot_single(self, data, title, ylabel):
        weighted_sums = np.empty(len(self.x_data), dtype=float)
        weighted_sums[0] = data[0]
        alpha = 0.005
        for i in range(1, len(data)):
            weighted_sums[i] = alpha * data[i] + (1 - alpha) * weighted_sums[i - 1]
        plt.plot(self.x_data, weighted_sums, label=f'exponential, alpha = {alpha}')

        plt.plot(self.x_data, np.cumsum(data) / np.arange(1, len(self.x_data) + 1), label='cumulative')
        plt.title(f'{title}')
        plt.xlabel('iterations')
        plt.ylabel(f'{ylabel}')
        plt.gca().yaxis.grid(True)
        plt.legend()
        plt.tight_layout()
        plt.savefig(f'plots/{title.replace(" ", "_").lower()}.jpg')
        plt.close()

    def plot_data(self):
        self.plot_single(self.rewards_data, 'Rewards', 'sum of the rewards')
        self.plot_single(self.tlareg_life_time_data, 'Life time', 'survived turns')
        self.plot_single(self.hits_before_death_data, 'Hits before death', 'hits')


class TlaregSarsa(Tlareg):

    def choose_action(self, state, eps):
        if random.uniform(0, 1) < eps:
            return random.choice(list(self.Q[state].items()))[0]
        else:
            return self.get_best_action(state)


class TlaregQLearning(Tlareg):

    def choose_action(self, state, eps):
        return self.get_best_action(state)
