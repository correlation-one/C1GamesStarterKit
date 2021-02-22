import unittest
import json
from .game_state import GameState
from .unit import GameUnit

class BasicTests(unittest.TestCase):

    def make_turn_0_map(self):
        config = """
            {
            "seasonCompatibilityModeP1": 5,
            "seasonCompatibilityModeP2": 5,
            "debug":{
                "printMapString":false,
                "printTStrings":false,
                "printActStrings":false,
                "printHitStrings":false,
                "printPlayerInputStrings":false,
                "printBotErrors":true,
                "printPlayerGetHitStrings":false
            },
            "unitInformation": [
                {
                "icon": "S3_filter",
                "iconxScale": 0.4,
                "iconyScale": 0.4,
                "cost1": 1.0,
                "getHitRadius":0.01,
                "display":"filter",
                "shorthand":"FF",
                "startHealth":75.0,
                "unitCategory": 0,
                "refundPercentage": 0.75,
                "turnsRequiredToRemove": 1,
                "upgrade": {
                    "startHealth": 150.0
                }
                },
                {
                "icon": "S3_encryptor",
                "iconxScale": 0.5,
                "iconyScale": 0.5,
                "cost1":4.0,
                "getHitRadius":0.01,
                "display":"encryptor",
                "shieldRange":0,
                "shorthand":"EF",
                "startHealth":30.0,
                "unitCategory": 0,
                "refundPercentage": 0.75,
                "turnsRequiredToRemove": 1,
                "generatesResource1": 1,
                "upgrade": {
                    "generatesResource2": 1
                }
                },
                {
                "icon": "S3_destructor",
                "iconxScale": 0.5,
                "iconyScale": 0.5,
                "attackDamageWalker":5.0,
                "cost1":2.0,
                "getHitRadius":0.01,
                "display":"destructor",
                "attackRange":2.5,
                "shorthand":"DF",
                "startHealth":90.0,
                "unitCategory": 0,
                "refundPercentage": 0.75,
                "turnsRequiredToRemove": 1,
                "upgrade": {
                    "cost1": 4.0,
                    "attackRange":3.5,
                    "attackDamageWalker":15.0
                }
                },
                {
                "icon": "S3_ping",
                "iconxScale": 0.7,
                "iconyScale": 0.7,
                "attackDamageTower":2.0,
                "attackDamageWalker":2.0,
                "playerBreachDamage":1.0,
                "cost2":1.0,
                "getHitRadius":0.01,
                "display":"ping",
                "attackRange":3.5,
                "shorthand":"PI",
                "startHealth":15.0,
                "speed":1,
                "unitCategory": 1,
                "selfDestructDamageWalker": 15.0,
                "selfDestructDamageTower": 15.0,
                "metalForBreach": 1.0,
                "selfDestructRange": 1.5,
                "selfDestructStepsRequired": 5
                },
                {
                "icon": "S3_emp",
                "iconxScale": 0.47,
                "iconyScale": 0.47,
                "attackDamageWalker":6.0,
                "attackDamageTower":6.0,
                "playerBreachDamage":1.0,
                "cost2":3.0,
                "getHitRadius":0.01,
                "display":"emp",
                "attackRange":4.5,
                "shorthand":"EI",
                "startHealth":5.0,
                "speed":0.5,
                "unitCategory": 1,
                "selfDestructDamageWalker": 5.0,
                "selfDestructDamageTower": 5.0,
                "metalForBreach": 1.0,
                "selfDestructRange": 1.5,
                "selfDestructStepsRequired": 5
                },
                {
                "icon": "S3_scrambler",
                "iconxScale": 0.5,
                "iconyScale": 0.5,
                "attackDamageWalker":20.0,
                "playerBreachDamage":1.0,
                "cost2":1.0,
                "getHitRadius":0.01,
                "display":"scrambler",
                "attackRange":4.5,
                "shorthand":"SI",
                "startHealth":40.0,
                "speed":0.25,
                "unitCategory": 1,
                "selfDestructDamageWalker": 40.0,
                "selfDestructDamageTower": 40.0,
                "metalForBreach": 1.0,
                "selfDestructRange": 1.5,
                "selfDestructStepsRequired": 5
                },
                {
                "display":"Remove",
                "shorthand":"RM",
                "icon": "S3_removal",
                "iconxScale": 0.4,
                "iconyScale": 0.4
                },
                {
                "display":"Upgrade",
                "shorthand":"UP",
                "icon": "S3_upgrade",
                "iconxScale": 0.4,
                "iconyScale": 0.4
                }
            ],
            "timingAndReplay":{
                "waitTimeBotMax":35000,
                "playWaitTimeBotMax":40000,
                "waitTimeManual":1820000,
                "waitForever":false,
                "waitTimeBotSoft":5000,
                "playWaitTimeBotSoft":10000,
                "replaySave":1,
                "playReplaySave":0,
                "storeBotTimes":true,
                "waitTimeStartGame":3000,
                "waitTimeEndGame":3000
            },
            "resources":{
                "turnIntervalForBitCapSchedule":10,
                "turnIntervalForBitSchedule":10,
                "bitRampBitCapGrowthRate":5.0,
                "roundStartBitRamp":10,
                "bitGrowthRate":1.0,
                "startingHP":40.0,
                "maxBits":150.0,
                "bitsPerRound":5.0,
                "coresPerRound":5.0,
                "coresForPlayerDamage":1.0,
                "startingBits":5.0,
                "bitDecayPerRound":0.25,
                "startingCores":20.0
            },
            "misc":{
                "numBlockedLocations": 0,
                "blockedLocations": [
                ]
            }
        }
        """
        turn_0 = """{"p2Units":[[],[],[],[],[],[],[]],"turnInfo":[0,0,-1],"p1Stats":[30.0,25.0,5.0,0],"p1Units":[[],[],[],[],[],[],[]],"p2Stats":[30.0,25.0,5.0,0],"events":{"selfDestruct":[],"breach":[],"damage":[],"shield":[],"move":[],"spawn":[],"death":[],"attack":[],"melee":[]}}"""
        
        state = GameState(json.loads(config), turn_0)
        state.suppress_warnings(True)
        return state

    def test_basic(self):
        self.assertEqual(True, True, "It's the end of the world as we know it, and I feel fine")

    def test_simple_fields(self):
        game = self.make_turn_0_map()
        self.assertEqual(5, game.get_resource(game.MP), "I should have 5 MP")
        self.assertEqual(25, game.get_resource(game.SP), "I should have 25 SP")
        self.assertEqual(5, game.get_resource(game.MP, 1), "My opponent should have 5 MP")
        self.assertEqual(25, game.get_resource(game.SP, 1), "My opponent should have 25 SP")
        self.assertEqual(0, game.turn_number, "The map does not have a turn_number, or we can't read it")
        self.assertEqual(30, game.my_health, "My integrity is not working")
        self.assertEqual(30, game.enemy_health, "My opponent has no integrity!")

    def test_spawning(self):
        game = self.make_turn_0_map()
        self.assertEqual(True, game.attempt_spawn("SI", [[13, 0]]), "We cannot spawn a soldier!")
        self.assertEqual(False, game.attempt_spawn("SI", [[13, 13]]), "We can spawn a soldier in the middle of the map?!?!")
        self.assertEqual(False, game.can_spawn("FF", [14, 14]), "Apparently I can place towers on my opponent's side")
        self.assertEqual(True, game.attempt_spawn("DF", [[13, 6]]), "We cannot spawn a tower!")
        self.assertEqual(2, game.attempt_spawn("SI", [[13, 0], [13, 0], [13, 5]]), "More or less than 2 units were spawned!")
        self.assertEqual([("DF", 13, 6)], game._build_stack, "Build queue is wrong!")
        self.assertEqual([("SI", 13, 0), ("SI", 13, 0), ("SI", 13, 0)], game._deploy_stack, "Deploy queue is wrong!")

    def test_trivial_functions(self):
        game = self.make_turn_0_map()

        #Distance Between locations
        self.assertEqual(1, game.game_map.distance_between_locations([0, 0], [0,-1]), "The distance between 0,0 and 0,-1 should be 1")
        self.assertEqual(1, game.game_map.distance_between_locations([-1, -1], [-2,-1]), "The distance between -1,-1 and -2,-1 should be 1")
        self.assertEqual(5, game.game_map.distance_between_locations([0, 0], [4, 3]), "The distance between 0,0 and 16,9 should be 5")
        self.assertEqual(0, len(game.game_map.get_locations_in_range([-500,-500], 10)), "Invalid tiles are being marked as in range")
        self.assertEqual(1, len(game.game_map.get_locations_in_range([13,13], 0)), "A location should be in range of itself")
    
    def test_get_units(self):
        game = self.make_turn_0_map()
        self.assertEqual(0, len(game.game_map[13,13]), "There should not be a unit on this location")
        for _ in range(3):
            game.game_map.add_unit("EI", [13,13])
        self.assertEqual(3, len(game.game_map[13,13]), "Information seems not to be stacking")
        for _ in range(3):
            game.game_map.add_unit("FF", [13,13])
        self.assertEqual(1, len(game.game_map[13,13]), "Towers seem to be stacking")
        
    def test_get_units_in_range(self):
        game = self.make_turn_0_map()
        self.assertEqual(1, len(game.game_map.get_locations_in_range([13,13], 0)), "We should be in 0 range of ourself")
        self.assertEqual(37, len(game.game_map.get_locations_in_range([13,13], 3.5)), "Wrong number of tiles in range")

    def _test_get_attackers(self):
        game = self.make_turn_0_map()
        
        self.assertEqual([], game.get_attackers([13,13], 0), "Are we being attacked by a ghost?")
        game.game_map.add_unit("DF", [12,12], 0)
        self.assertEqual([], game.get_attackers([13,13], 0), "Are we being attacked by a friend?")
        game.game_map.add_unit("EF", [13,12], 1)
        self.assertEqual([], game.get_attackers([13,13], 0), "Are we being attacked by a support?")
        game.game_map.add_unit("FF", [14,12], 1)
        self.assertEqual([], game.get_attackers([13,13], 0), "Are we being attacked by a wall?")
        game.game_map.add_unit("DF", [12,14], 1)
        self.assertEqual(1, len(game.get_attackers([13,13], 0)), "We should be in danger")
        game.game_map.add_unit("DF", [13,14], 1)
        game.game_map.add_unit("DF", [14,14], 1)
        self.assertEqual(3, len(game.get_attackers([13,13], 0)), "We should be in danger from 3 places")

    def test_print_unit(self):
        game = self.make_turn_0_map()

        game.game_map.add_unit("FF", [14,13], 1)
        got_string = str(game.game_map[14,13][0])
        expected_string = "Enemy FF, health: 75.0 location: [14, 13] removal:  upgrade: False "
        self.assertEqual(got_string, expected_string, "Expected {} from print_unit test got {} ".format(expected_string, got_string))

    def test_future_MP(self):
        game = self.make_turn_0_map()

        self.future_turn_testing_function(game, 8.3, 1)
        self.future_turn_testing_function(game, 11.6, 2)
        self.future_turn_testing_function(game, 13.7, 3)

    def future_turn_testing_function(self, game, expected, turns):
        actual = game.project_future_MP(turns)
        self.assertAlmostEqual(actual, expected, 0, "Expected {} MP {} turns from now, got {}".format(expected, turns, actual))

