import unittest
import json
from .game_state import GameState
from .unit import GameUnit
from .advanced_game_state import AdvancedGameState

class BasicTests(unittest.TestCase):

    def make_turn_0_map(self, adv=False):
        config = """
        {
            "debug":{
                "printMapString":false,
                "printTStrings":false,
                "printActStrings":false,
                "printHitStrings":false,
                "printPlayerInputStrings":false,
                "printBotErrors":false,
                "printPlayerGetHitStrings":false
            },
            "unitInformation":[
                {
                "damage":0.0,
                "cost":1,
                "getHitRadius":0.51,
                "display":"Filter",
                "range":3.0,
                "shorthand":"FF",
                "stability":60.0
                },
                {
                "damage":0.0,
                "cost":4,
                "getHitRadius":0.51,
                "shieldAmount":10.0,
                "display":"Encryptor",
                "range":3.0,
                "shorthand":"EF",
                "stability":30.0
                },
                {
                "damage":4.0,
                "cost":3,
                "getHitRadius":0.51,
                "display":"Destructor",
                "range":3.0,
                "shorthand":"DF",
                "stability":75.0
                },
                {
                "damageI":1.0,
                "damageToPlayer":1.0,
                "cost":1.0,
                "getHitRadius":0.51,
                "damageF":1.0,
                "display":"Ping",
                "range":3.0,
                "shorthand":"PI",
                "stability":15.0,
                "speed":0.5
                },
                {
                "damageI":3.0,
                "damageToPlayer":1.0,
                "cost":3.0,
                "getHitRadius":0.51,
                "damageF":3.0,
                "display":"EMP",
                "range":5.0,
                "shorthand":"EI",
                "stability":5.0,
                "speed":0.25
                },
                {
                "damageI":10.0,
                "damageToPlayer":1.0,
                "cost":1.0,
                "getHitRadius":0.51,
                "damageF":0.0,
                "display":"Scrambler",
                "range":3.0,
                "shorthand":"SI",
                "stability":40.0,
                "speed":0.25
                },
                {
                "display":"Remove",
                "shorthand":"RM"
                }
            ],
            "timingAndReplay":{
                "waitTimeBotMax":100000,
                "waitTimeManual":1820000,
                "waitForever":false,
                "waitTimeBotSoft":70000,
                "replaySave":0,
                "storeBotTimes":true
            },
            "resources":{
                "turnIntervalForBitCapSchedule":10,
                "turnIntervalForBitSchedule":10,
                "bitRampBitCapGrowthRate":5.0,
                "roundStartBitRamp":10,
                "bitGrowthRate":1.0,
                "startingHP":30.0,
                "maxBits":999999.0,
                "bitsPerRound":5.0,
                "coresPerRound":5.0,
                "coresForPlayerDamage":1.0,
                "startingBits":5.0,
                "bitDecayPerRound":0.33333,
                "startingCores":25.0
            },
            "mechanics":{
                "basePlayerHealthDamage":1.0,
                "damageGrowthBasedOnY":0.0,
                "bitsCanStackOnDeployment":true,
                "destroyOwnUnitRefund":0.5,
                "destroyOwnUnitsEnabled":true,
                "stepsRequiredSelfDestruct":5,
                "selfDestructRadius":1.5,
                "shieldDecayPerFrame":0.15,
                "meleeMultiplier":0,
                "destroyOwnUnitDelay":1,
                "rerouteMidRound":true,
                "firewallBuildTime":0
            }
        }
        """
        turn_0 = """{"p2Units":[[],[],[],[],[],[],[]],"turnInfo":[0,0,-1],"p1Stats":[30.0,25.0,5.0,0],"p1Units":[[],[],[],[],[],[],[]],"p2Stats":[30.0,25.0,5.0,0],"events":{"selfDestruct":[],"breach":[],"damage":[],"shield":[],"move":[],"spawn":[],"death":[],"attack":[],"melee":[]}}"""
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
        self.assertEqual(5, game.get_resource(game.BITS), "I should have 5 bits")
        self.assertEqual(25, game.get_resource(game.CORES), "I should have 25 cores")
        self.assertEqual(5, game.get_resource(game.BITS, 1), "My opponent should have 5 bits")
        self.assertEqual(25, game.get_resource(game.CORES, 1), "My opponent should have 25 cores")
        self.assertEqual(0, game.turn_number, "The map does not have a turn_number, or we can't read it")
        self.assertEqual(30, game.my_health, "My integrity is not working")
        self.assertEqual(30, game.enemy_health, "My opponent has no integrity!")

    def test_spawning(self, adv=False):
        game = self.make_turn_0_map(adv)
        self.assertEqual(True, game.attempt_spawn("SI", [[13, 0]]), "We cannot spawn a soldier!")
        self.assertEqual(False, game.attempt_spawn("SI", [[13, 13]]), "We can spawn a soldier in the middle of the map?!?!")
        self.assertEqual(False, game.can_spawn("FF", [14, 14]), "Apparently I can place towers on my opponent's side")
        self.assertEqual(True, game.attempt_spawn("DF", [[13, 6]]), "We cannot spawn a tower!")
        self.assertEqual(2, game.attempt_spawn("SI", [[13, 0], [13, 0], [13, 5]]), "More or less than 2 units were spawned!")
        self.assertEqual([("DF", 13, 6)], game._build_stack, "Build queue is wrong!")
        self.assertEqual([("SI", 13, 0), ("SI", 13, 0), ("SI", 13, 0)], game._deploy_stack, "Deploy queue is wrong!")

    def test_trivial_functions(self, adv=False):
        game = self.make_turn_0_map(adv)

        #Distance Between locations
        self.assertEqual(1, game.game_map.distance_between_locations([0, 0], [0,-1]), "The distance between 0,0 and 0,-1 should be 1")
        self.assertEqual(1, game.game_map.distance_between_locations([-1, -1], [-2,-1]), "The distance between -1,-1 and -2,-1 should be 1")
        self.assertEqual(5, game.game_map.distance_between_locations([0, 0], [4, 3]), "The distance between 0,0 and 16,9 should be 5")
        self.assertEqual(0, len(game.game_map.get_locations_in_range([-500,-500], 10)), "Invalid tiles are being marked as in range")
        self.assertEqual(1, len(game.game_map.get_locations_in_range([13,13], 0)), "A location should be in range of itself")
    
    def test_get_units(self, adv=False):
        game = self.make_turn_0_map(adv)
        self.assertEqual(0, len(game.game_map[13,13]), "There should not be a unit on this location")
        for _ in range(3):
            game.game_map.add_unit("EI", [13,13])
        self.assertEqual(3, len(game.game_map[13,13]), "Information seems not to be stacking")
        for _ in range(3):
            game.game_map.add_unit("FF", [13,13])
        self.assertEqual(1, len(game.game_map[13,13]), "Towers seem to be stacking")
        
    def test_get_units_in_range(self, adv=False):
        game = self.make_turn_0_map(adv)
        self.assertEqual(1, len(game.game_map.get_locations_in_range([13,13], 0)), "We should be in 0 range of ourself")
        self.assertEqual(37, len(game.game_map.get_locations_in_range([13,13], 3)), "Wrong number of tiles in range")

    def _test_get_attackers(self):
        game = self.make_turn_0_map(True)
        
        self.assertEqual([], game.get_attackers([13,13], 0), "Are we being attacked by a ghost?")
        game.game_map.add_unit("DF", [12,12], 0)
        self.assertEqual([], game.get_attackers([13,13], 0), "Are we being attacked by a friend?")
        game.game_map.add_unit("EF", [13,12], 1)
        self.assertEqual([], game.get_attackers([13,13], 0), "Are we being attacked by an encryptor?")
        game.game_map.add_unit("FF", [14,12], 1)
        self.assertEqual([], game.get_attackers([13,13], 0), "Are we being attacked by a filter?")
        game.game_map.add_unit("DF", [12,14], 1)
        self.assertEqual(1, len(game.get_attackers([13,13], 0)), "We should be in danger")
        game.game_map.add_unit("DF", [13,14], 1)
        game.game_map.add_unit("DF", [14,14], 1)
        self.assertEqual(3, len(game.get_attackers([13,13], 0)), "We should be in danger from 3 places")

    def test_print_unit(self, adv=False):
        game = self.make_turn_0_map(adv)

        game.game_map.add_unit("FF", [14,13], 1)
        got_string = str(game.game_map[14,13][0])
        expected_string = "Enemy FF, stability: 60.0 location: [14, 13] "
        self.assertEqual(got_string, expected_string, "Expected {} from print_unit test got {} ".format(expected_string, got_string))

    def test_future_bits(self, adv=False):
        game = self.make_turn_0_map(adv)

        self.future_turn_testing_function(game, 8.3, 1)
        self.future_turn_testing_function(game, 10.5, 2)
        self.future_turn_testing_function(game, 12.0, 3)
        self.future_turn_testing_function(game, 13.0, 4)
        self.future_turn_testing_function(game, 13.7, 5)
        self.future_turn_testing_function(game, 14.1, 6)
        self.future_turn_testing_function(game, 14.4, 7)
        self.future_turn_testing_function(game, 14.6, 8)
        self.future_turn_testing_function(game, 14.7, 9)
        self.future_turn_testing_function(game, 15.8, 10)
        self.future_turn_testing_function(game, 16.5, 11)
        self.future_turn_testing_function(game, 17.0, 12)
        self.future_turn_testing_function(game, 17.3, 13)
        self.future_turn_testing_function(game, 17.5, 14)
        self.future_turn_testing_function(game, 17.7, 15)
        self.future_turn_testing_function(game, 17.8, 16)
        self.future_turn_testing_function(game, 17.9, 17)
        self.future_turn_testing_function(game, 17.9, 18)
        self.future_turn_testing_function(game, 17.9, 19)
        self.future_turn_testing_function(game, 18.9, 20)

    def future_turn_testing_function(self, game, expected, turns):
        actual = game.project_future_bits(turns)
        self.assertAlmostEqual(actual, expected, 0, "Expected {} power {} turns from now, got {}".format(expected, turns, actual))

