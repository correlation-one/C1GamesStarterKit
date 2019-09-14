import gamelib
import random
import math
import warnings
from sys import maxsize
import json

global location_options, fire_param, scrambler_param, bits_save_threshold
location_options = [
    [0,13],
    [1,12],
    [2,11],
    [3,10],
    [4,9],
    [5,8],
    [6,7],
    [7,6],
    [8,5],
    [9,4],
    [10,3],
    [11,2],
    [12,1],
    [13,0],
    [14,0],
    [15,1],
    [16,2],
    [17,3],
    [18,4],
    [19,5],
    [20,6],
    [21,7],
    [22,8],
    [23,9],
    [24,10],
    [25,11],
    [26,12],
    [27,13]
]

fire_param = 0.5
scrambler_param = 0.5
bits_save_threshold = 10

class AttackStrategy:

    def spawn_attackers(self, game_state, scrambler_heatmap, score_board):
        if not self.is_attack(game_state, risk_level):
            return

        spawn_location, path, destr_count = self.best_spawn_location(game_state, scrambler_heatmap, score_board)

        if self.is_spawn_encryptor(game_state):
            encryptors = self.spawn_encryptors(game_state, path)
            game_state.attemp_spawn(game_state.ENCRYPTOR, encryptors)

        game_state.attemp_spawn(game_state.EMP, spawn_location, destr_count)
        game_state.attemp_spawn(game_state.PING, spawn_location, game_state.number_affordable(game_state.PING))


    def is_spawn_encryptor(self, game_state):
        if game_state.turn_number >= 5:
            return True
        return False

    def spawn_encryptors(self, game_state, path):
        core_budget = game_state.get_resource(game_state.BITS)
        num_encryptor = game_state.number_affordable(game_state.ENCRYPTOR)
        spawn_encryptor = []
        for location in path:
            if num_encryptor == 0:
                break
            neighbors = self.get_neighbors(location)
            for neighbor in neighbors:
                if neighbor not in path and game_state.can_spawn(game_state.ENCRYPTOR, neighbor):
                    spawn_encryptor.append(location)
                    num_encryptor -= 1
        
        
    def get_neighbors(self, location):
        [x, y] = location
        return [[x-1, y-1], [x, y-1], [x+1, y-1], [x-1, y], [x+1, y], [x-1, y+1], [x, y+1], [x+1, y+1]]


    def is_attack(self, game_state, risk_level):
        return False


    def best_spawn_location(self, game_state, scrambler_heatmap, score_board):
        global location_options, fire_param, scrambler_param, bits_save_threshold
        preferences = []
        paths = []
        enemy_destr_counts = []
        for location in location_options:
            path = game_state.find_path_to_edge(location)
            paths.append(path)
            preference, fire, scram, tough = 0
            for path_location in path:
                [x, y] = path_location
                enemy_destr_count = len(game_state.get_attackers(path_location, 0))
                enemy_destr_counts.append(enemy_destr_count)
                fire += enemy_destr_count * gamelib.GameUnit(DESTRUCTOR, game_state.config).damage
                scram += scrambler_heatmap[x, y]
                risk = fire * fire_param + scram * scrambler_param
                reward = score_board[x]
                preference = reward / risk
            preference.append(preference)
        idx = preferences.index(min(preferences))
        return location_options[idx], paths[idx], enemy_destr_counts[idx]

