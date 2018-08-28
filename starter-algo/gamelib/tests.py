import unittest
import json
from .game import GameState
from .unit import GameUnit
from .advanced import AdvancedGameState

class BasicTests(unittest.TestCase):

    def make_turn_0_map(self, adv=False):
        config = '''
        {
        "waitTimeManual": 1820000,
        "printMapString": false,
        "printTStrings": false,
        "soldiersCanStackOnDeployment": true,
        "towerBuildTime": 0,
        "waitTimeBotMax": 1220000,
        "PI": {
            "damageToPlayer": 1.0,
            "cost": 1.0,
            "getHitRadius": 0.51,
            "damageS": 1.0,
            "damageT": 1.0,
            "health": 15.0,
            "range": 3.0,
            "speed": 0.5
        },
        "selfDestructRadius": 1.5,
        "printPlayerInputStrings": false,
        "rerouteMidRound": true,
        "EI": {
            "damageToPlayer": 1.0,
            "cost": 3.0,
            "getHitRadius": 0.51,
            "damageS": 3.0,
            "damageT": 3.0,
            "health": 5.0,
            "range": 5.0,
            "speed": 0.25
        },
        "SI": {
            "damageToPlayer": 1.0,
            "cost": 1.0,
            "getHitRadius": 0.51,
            "damageS": 10.0,
            "damageT": 0.0,
            "health": 40.0,
            "range": 3.0,
            "speed": 0.25
        },
        "displayBotErrors": false,
        "waitForever": false,
        "replaySave": 1,
        "FF": {
            "damage": 0.0,
            "cost": 1.5,
            "getHitRadius": 0.51,
            "health": 60.0,
            "range": 0.0
        },
        "printPlayerGetHitStrings": false,
        "DF": {
            "damage": 4.0,
            "cost": 6.0,
            "getHitRadius": 0.51,
            "health": 75.0,
            "range": 3.0
        },
        "printActStrings": false,
        "waitTimeBotSoft": 1200000,
        "printHitStrings": false,
        "EF": {
            "damage": 0.0,
            "cost": 8.0,
            "getHitRadius": 0.51,
            "health": 30.0,
            "range": 3.0,
            "supportShieldAmount": 10.0
        },
        "destroyOwnUnitDelay": 1,
        "destroyOwnUnitsEnabled": true,
        "metalForPlayerDamage": 2.0,
        "shieldDecayPerFrame": 0.15,
        "displayBotTimes": true,
        "basePlayerHealthDamage": 1,
        "damageGrowthBasedOnY": 0.0,
        "meleeMultiplier": 0.0,
        "destroyOwnUnitRefund": 0.5,
        "typeDefinitions":[{"display":"Filter","shorthand":"FF"},{"display":"Encryptor","shorthand":"EF"},{"display":"Destructor","shorthand":"DF"},{"display":"Ping","shorthand":"PI"},{"display":"EMP","shorthand":"EI"},{"display":"Scrambler","shorthand":"SI"},{"display":"Remove","shorthand":"RM"}],
        "startingFood": 5.0,
        "startingHP": 30.0,
        "startingMetal": 50.0,
        "metalPerRound": 15.0,
        "foodPerRound": 5.0,
        "maxFood": 999999.0,
        "roundStartSuddenDeath": 5,
        "turnIntervalForFoodCapSchedule": 5,
        "turnIntervalForFoodSchedule": 10,
        "suddenDeathFoodCapGrowthRate": 5.0,
        "foodGrowthRate": 1,
        "foodSpoilPerRound": 0.33333,
        "stepsRequiredSelfDestruct": 5
        }
        '''
        turn_0 = '''{"p2Units":[[],[],[],[],[],[],[]],"turnInfo":[0,0,-1],"p1Stats":[30.0,50.0,5.0,0],"p1Units":[[],[],[],[],[],[],[]],"p2Stats":[30.0,50.0,5.0,0],"events":{"selfDestruct":[],"breach":[],"damage":[],"shield":[],"move":[],"spawn":[],"death":[],"attack":[],"melee":[]}}'''
        if adv:
            return AdvancedGameState(json.loads(config), turn_0)
        return GameState(json.loads(config), turn_0)

    def test_basic(self, adv=False):
        self.assertEqual(True, True, "It's the end of the world as we know it, and I feel fine")

    def test_advanced_game_state(self, adv=False):
        advanced = self.make_turn_0_map(True)
        self.assertTrue(isinstance(advanced, GameState))
        self.assertTrue(isinstance(advanced, AdvancedGameState))
        for name in sorted(dir(self)):
            if name.startswith("test") and "advanced" not in name:
                getattr(self, name)(True)

    def test_simple_fields(self, adv=False):
        game = self.make_turn_0_map(adv)
        self.assertEqual(5, game.get_resource('bits'), "I should have 5 bits")
        self.assertEqual(50, game.get_resource('cores'), "I should have 50 cores")
        self.assertEqual(5, game.get_resource('bits', True), "My opponent should have 5 bits")
        self.assertEqual(50, game.get_resource('cores', True), "My opponent should have 50 cores")
        self.assertEqual(0, game.turn_number, "The map does not have a turn_number, or we can't read it")
        self.assertEqual(30, game.my_integrity, "My integrity is not working")
        self.assertEqual(30, game.enemy_integrity, "My opponent has no integrity!")

    def test_spawning(self, adv=False):
        game = self.make_turn_0_map(adv)
        self.assertEqual(True, game.attempt_spawn("SI", [[13, 0]]), "We cannot spawn a soldier!")
        self.assertEqual(False, game.attempt_spawn("SI", [[13, 13]]), "We can spawn a soldier in the middle of the map?!?!")
        self.assertEqual(False, game.can_spawn("FF", [14, 14]), "Apparently I can place towers on my opponent's side")
        self.assertEqual(True, game.attempt_spawn("DF", [[13, 6]]), "We cannot spawn a tower!")
        self.assertEqual(2, game.attempt_spawn("SI", [[13, 0], [13, 0], [13, 5]]), "More or less than 2 units were spawned!")
        self.assertEqual([("DF", 13, 6)], game.build_stack, "Build queue is wrong!")
        self.assertEqual([("SI", 13, 0), ("SI", 13, 0), ("SI", 13, 0)], game.deploy_stack, "Deploy queue is wrong!")

    def test_trivial_functions(self, adv=False):
        game = self.make_turn_0_map(adv)
        self.assertEqual(1, game.map.distance_between_locations([0, 0], [0,-1]), "The distance between 0,0 and 0,-1 should be 1")
        self.assertEqual(1, game.map.distance_between_locations([-1, -1], [-2,-1]), "The distance between -1,-1 and -2,-1 should be 1")
        self.assertEqual(5, game.map.distance_between_locations([0, 0], [4, 3]), "The distance between 0,0 and 16,9 should be 5")
        self.assertEqual(0, len(game.map.get_locations_in_range([-500,-500], 10)), "Invalid tiles are being marked as in range")
        self.assertEqual(1, len(game.map.get_locations_in_range([13,13], 0)), "A location should be in range of itself")
    
    def test_get_units(self, adv=False):
        game = self.make_turn_0_map(adv)
        self.assertEqual(0, len(game.map[13,13]), "There should not be a unit on this location")
        for i in range(3):
            game.map.add_unit("EI", [13,13])
        self.assertEqual(3, len(game.map[13,13]), "Information seems not to be stacking")
        for i in range(3):
            game.map.add_unit("FF", [13,13])
        self.assertEqual(1, len(game.map[13,13]), "Towers seem to be stacking")
        
    def test_get_units_in_range(self, adv=False):
        game = self.make_turn_0_map(adv)
        self.assertEqual(1, len(game.map.get_locations_in_range([13,13], 0)), "We should be in 0 range of ourself")
        self.assertEqual(37, len(game.map.get_locations_in_range([13,13], 3)), "Wrong number of tiles in range")

    def _test_get_attackers(self, adv=False):
        game = self.make_turn_0_map(adv)
        
        self.assertEqual([], game.get_attackers([13,13], 0), "Are we being attacked by a ghost?")
        game.map.add_unit("DF", [12,12], 0)
        self.assertEqual([], game.get_attackers([13,13], 0), "Are we being attacked by a friend?")
        game.map.add_unit("EF", [13,12], 1)
        self.assertEqual([], game.get_attackers([13,13], 0), "Are we being attacked by an encryptor?")
        game.map.add_unit("FF", [14,12], 1)
        self.assertEqual([], game.get_attackers([13,13], 0), "Are we being attacked by a filter?")
        game.map.add_unit("DF", [12,14], 1)
        self.assertEqual(1, len(game.get_attackers([13,13], 0)), "We should be in danger")
        game.map.add_unit("DF", [13,14], 1)
        game.map.add_unit("DF", [14,14], 1)
        self.assertEqual(3, len(game.get_attackers([13,13], 0)), "We should be in danger from 3 places")

    def test_print_unit(self, adv=False):
        game = self.make_turn_0_map(adv)

        game.map.add_unit("FF", [14,13], 1)
        got_string = str(game.map[14,13][0])
        expected_string = "Enemy FF, 100% stability"
        self.assertEqual(got_string, expected_string, "Expected {} from print_unit test got {}".format(expected_string, got_string))

    def test_future_bits(self, adv=False):
        game = self.make_turn_0_map(adv)

        self.future_turn_testing_function(game, 8.33, 1)
        self.future_turn_testing_function(game, 10.55, 2)
        self.future_turn_testing_function(game, 12.04, 3)
        self.future_turn_testing_function(game, 13.03, 4)
        self.future_turn_testing_function(game, 13.68, 5)
        self.future_turn_testing_function(game, 14.74, 9)
        self.future_turn_testing_function(game, 15.83, 10)

    def future_turn_testing_function(self, game, expected, turns):
        actual = game.project_future_bits(turns)
        self.assertAlmostEqual(actual, expected, 0, "Expected {} power {} turns from now, got {}".format(expected, turns, actual))
