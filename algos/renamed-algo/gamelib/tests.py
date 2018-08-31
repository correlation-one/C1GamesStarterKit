import unittest
import json
from .game import GameMap, GameUnit
import gamelib.game as game

class BasicTests(unittest.TestCase):

    def make_turn0_map(self):
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
        "turnIntervalForFoodSchedule": 5,
        "suddenDeathFoodCapGrowthRate": 5.0,
        "foodGrowthRate": 1,
        "foodSpoilPerRound": 0.33333,
        "stepsRequiredSelfDestruct": 5
        }
        '''
        turn0 = '''{"p2Units":[[],[],[],[],[],[],[]],"turnInfo":[0,0,-1],"p1Stats":[30.0,50.0,5.0,0],"p1Units":[[],[],[],[],[],[],[]],"p2Stats":[30.0,50.0,5.0,0],"events":{"selfDestruct":[],"breach":[],"damage":[],"shield":[],"move":[],"spawn":[],"death":[],"attack":[],"melee":[]}}'''
        return game.GameMap(json.loads(config), turn0)

    def test_basic(self):
        self.assertEqual(True, True, "It's the end of the world as we know it, and I feel fine")

    def test_simple_fields(self):
        game_map = self.make_turn0_map()
        self.assertEqual(5, game_map.get_resource('bits'), "I should have 5 bits")
        self.assertEqual(50, game_map.get_resource('cores'), "I should have 50 cores")
        self.assertEqual(5, game_map.get_resource('bits', True), "My opponent should have 5 bits")
        self.assertEqual(50, game_map.get_resource('cores', True), "My opponent should have 50 cores")
        self.assertEqual(0, game_map.turn_number, "The map does not have a turn_number, or we can't read it")
        self.assertEqual(30, game_map.my_integrity, "My integrity is not working")
        self.assertEqual(30, game_map.enemy_integrity, "My opponent has no integrity!")

    def test_spawning(self):
        game_map = self.make_turn0_map()
        self.assertEqual(True, game_map.attempt_spawn("SI", [13, 0]), "We cannot spawn a soldier!")
        self.assertEqual(False, game_map.attempt_spawn("SI", [13, 13]), "We can spawn a soldier in the middle of the map?!?!")
        self.assertEqual(False, game_map.can_spawn("FF", [14, 14]), "Apparently I can place towers on my opponent's side")
        self.assertEqual(True, game_map.attempt_spawn("DF", [13, 6]), "We cannot spawn a tower!")
        self.assertEqual(2, game_map.attempt_spawn_multiple("SI", [[13, 0], [13, 0], [13, 5]]), "More or less than 2 units were spawned!")
        self.assertEqual([("DF", 13, 6)], game_map.temp_build, "Build queue is wrong!")
        self.assertEqual([("SI", 13, 0), ("SI", 13, 0), ("SI", 13, 0)], game_map.temp_deploy, "Deploy queue is wrong!")

    def test_trivial_functions(self):
        game_map = self.make_turn0_map()
        self.assertEqual([13,13], game_map.flip_over_x_axis([13,14]), "Flip over X seems wrong, or board size changed from 28")
        self.assertEqual([13,13], game_map.flip_over_y_axis([14,13]), "Flip over Y seems wrong, or board size changed from 28")
        self.assertEqual(1, game_map.distance_between_locations([0, 0], [0,-1]), "The distance between 0,0 and 0,-1 should be 1")
        self.assertEqual(1, game_map.distance_between_locations([-1, -1], [-2,-1]), "The distance between -1,-1 and -2,-1 should be 1")
        self.assertEqual(5, game_map.distance_between_locations([0, 0], [4, 3]), "The distance between 0,0 and 16,9 should be 5")
        self.assertEqual(0, len(game_map.get_locations_in_range([-500,-500], 10)), "Invalid tiles are being marked as in range")
        self.assertEqual(1, len(game_map.get_locations_in_range([13,13], 0)), "A location should be in range of itself")
    
    def test_get_units(self):
        game_map = self.make_turn0_map()
        self.assertEqual(0, len(game_map.get_units([13,13])), "There should not be a unit on this location")
        for i in range(3):
            game_map.add_unit_to_map("EI", [13,13])
        self.assertEqual(3, len(game_map.get_units([13,13])), "Information seems not to be stacking")
        for i in range(3):
            game_map.add_unit_to_map("FF", [13,13])
        self.assertEqual(1, len(game_map.get_units([13,13])), "Towers seem to be stacking")
        
    def test_map_copy(self):
        game_map = self.make_turn0_map()
        test_copy = game_map.get_map_copy()
        test_copy2 = game_map.get_map_copy([["FF", [0,0]], ["EF", [5,5]], ["DF", [13,13]], ["FF", [13,13]]])
        self.assertEqual(0, len(test_copy.get_units([13,13])), "There is a unit at 13,13 in test_copy where there should not be")
        self.assertEqual(1, len(test_copy2.get_units([13,13])), "Passing map delta to get_map_copy not working")

        test_copy.add_unit_to_map("FF", [13,13])
        test_copy2.map[13][13] = []
        self.assertEqual(1, len(test_copy.get_units([13,13])), "Force_put_unit doesn't seem to work")
        self.assertEqual(0, len(test_copy2.get_units([13,13])), "Failed to remove a unit")

    def test_get_units_in_range(self):
        game_map = self.make_turn0_map()
        self.assertEqual(1, len(game_map.get_locations_in_range([13,13], 0)), "We should be in 0 range of ourself")
        self.assertEqual(37, len(game_map.get_locations_in_range([13,13], 3)), "Wrong number of tiles in range")

    def test_get_attackers(self):
        game_map = self.make_turn0_map()

        self.assertEqual([], game_map.get_attackers([13,13], 0), "Are we being attacked by a ghost?")
        game_map.add_unit_to_map("DF", [12,12], 0)
        self.assertEqual([], game_map.get_attackers([13,13], 0), "Are we being attacked by a friend?")
        game_map.add_unit_to_map("EF", [13,12], 1)
        self.assertEqual([], game_map.get_attackers([13,13], 0), "Are we being attacked by an encryptor?")
        game_map.add_unit_to_map("FF", [14,12], 1)
        self.assertEqual([], game_map.get_attackers([13,13], 0), "Are we being attacked by a filter?")
        game_map.add_unit_to_map("DF", [12,14], 1)
        self.assertEqual(1, len(game_map.get_attackers([13,13], 0)), "We should be in danger")
        game_map.add_unit_to_map("DF", [13,14], 1)
        game_map.add_unit_to_map("DF", [14,14], 1)
        self.assertEqual(3, len(game_map.get_attackers([13,13], 0)), "We should be in danger from 3 places")


    def test_get_target(self):
        game_map = self.make_turn0_map()
        test_unit = GameUnit("PI", game_map.config, 1, 13, 13)

        self.assertEqual(None, game_map.get_target(test_unit))
        game_map.add_unit_to_map("FF", [14,13], 1)
        self.assertEqual(None, game_map.get_target(test_unit))

        game_map.add_unit_to_map("FF", [15,13], 2)
        test_target = game_map.get_target(test_unit)
        self.assertEqual([15,13], [test_target.x, test_target.y])
        game_map.add_unit_to_map("PI", [16,13], 2)
        test_target = game_map.get_target(test_unit)
        self.assertEqual([16,13], [test_target.x, test_target.y])
        game_map.add_unit_to_map("PI", [14,14], 2)
        game_map.add_unit_to_map("PI", [12,12], 2)
        game_map.add_unit_to_map("PI", [12,14], 2)
        game_map.add_unit_to_map("PI", [14,12], 2)
        test_target = game_map.get_target(test_unit)
        self.assertEqual([12,12], [test_target.x, test_target.y])
        game_map.map[14][12][0].stability = 1
        test_target = game_map.get_target(test_unit)
        self.assertEqual([14,12], [test_target.x, test_target.y])

    def test_print_unit(self):
        game_map = self.make_turn0_map()

        game_map.add_unit_to_map("FF", [14,13], 1)
        got_string = str(game_map.get_units([14,13])[0])
        expected_string = "FF:14-13-{}-1".format(game_map.get_units([14,13])[0].stability)
        self.assertEqual(got_string, expected_string, "Expected {} from print_unit test got {}".format(expected_string, got_string))

    def test_future_bits(self):
        game_map = self.make_turn0_map()

        self.future_turn_testing_function(game_map, 8.34, 1)
        self.future_turn_testing_function(game_map, 10.54, 2)
        self.future_turn_testing_function(game_map, 12.04, 3)
        self.future_turn_testing_function(game_map, 13.04, 4)
        self.future_turn_testing_function(game_map, 14.68, 5)
        self.future_turn_testing_function(game_map, 17.34, 9)
        self.future_turn_testing_function(game_map, 18.56, 10)

        self.assertEqual(game_map.bits_gained_on_turn(0), 5, "Expected {} power gain on turn {}, got {}".format(5, 0, game_map.bits_gained_on_turn(0)))
        self.assertEqual(game_map.bits_gained_on_turn(1), 5, "Expected {} power gain on turn {}, got {}".format(5, 1, game_map.bits_gained_on_turn(1)))
        self.assertEqual(game_map.bits_gained_on_turn(5), 6, "Expected {} power gain on turn {}, got {}".format(6, 10, game_map.bits_gained_on_turn(10)))
        self.assertEqual(game_map.bits_gained_on_turn(10), 7, "Expected {} power gain on turn {}, got {}".format(7, 20, game_map.bits_gained_on_turn(20)))

    def future_turn_testing_function(self, game_map, expected, turns):
        actual = game_map.bits_in_future(turns)
        self.assertAlmostEqual(actual, expected, 0, "Expected {} power {} turns from now, got {}".format(expected, turns, actual))
