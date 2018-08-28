# Step-by-step Startup:

1. Download `starter-algo.zip` and unzip the folder
2. Open the file ‘algo_strategy.py’
3. In this file, you can see a starter algo strategy, with various examples of basic algo functionality and comments explaining how to customize the algo.
4. When you are done, you can rename the ‘unzipped’ folder (starter-algo) whatever you want. This will be the name of your Algo! Note: Renaming other files could cause problems.
5. That’s it! Your zipped algo is ready to compete in the arena!

# Detailed Documentation for Creators

## Some of the common parameters taken or returned by functions

### Unit type strings:
These strings each represent one of our 6 units
- “PI” for Ping, “EI” for EMP, “SI” for Scrambler
- “FF” for Filter, “DF” for Destructor, “EF” for Encryptor

### Location:
A list with two integers corresponding to the x, y coordinate of a tile in the grid
- Example: [9,13]

### player_id:
0 indicates you, 1 indicates your opponent

## GameMap (game_map)

This class is a representation of the current game state, and contains many helper methods to simplify placing units, determining paths, and other common actions.
The starting strategy many algos are based off of creates ‘game_map’, which can be used to access these methods. Examples of using game_map to use these methods can be seen within the starter strategy.

### Useful Attributes of Game Map

- game_map.arena_size - An integer 28, the size of the game board
- game_map.map - A 2 dimensional list representing each tile in the arena. Each tile is a list containing the units currently on that tile. The Unit class is described in detail below. The origin is in the bottom left corner
- game_map.turn_number - The turn number. Begins at 0, and increases by one after each action phase.
- game_map.my_integrity - Your currently remaining integrity
- game_map.enemy_integrity - Your enemies currently remaining integrity

### Useful Methods of Game Map

Note on methods in python: ‘self’ refers to the class instance on which the method is invoked, and is automatically passed when we call a function using game map.
For example, to call a theoretical method `fubar(self, location)` on `GameMap` we would write `game_map.fubar([9, 13])`.

send_messages():
- Effect: Submit your turn after you are done deploying units.

get_resource(self, resource_type, enemy_resource = False):
- Input: A string representing a resource. 'bits' or 'cores'. Optionally, pass 'True' for enemy_resource.
- Output: The amount of that resource that you have available. If you passed True, get the enemy's resource instead.

number_affordable(self, unit_type):
- Input: A unit type string.
- Output: The maximum number of that unit you can afford (integer)

can_afford(self, unit_type):
- Input: A unit type string
- Output: True if you have enough resources to afford the unit, otherwise False

power_in_future(self, turns_in_future = 1, player_id = 0):
- Input: A number of turns in the future, a player_id
- Output: The amount of power the player will have after not spending any for a certain number of turns

power_gained_on_turn(self, turn_number):
- Input: A turn number
- Output: The amount of power that will be gained at the start of that turn. 

can_spawn(self, unit_type, location):
- Input: A unit type string, a location
- Output: True if we can create that unit at that location, otherwise False.

attempt_spawn(self, unit_type, location):
- Input: A unit type string, a location
- Output: True if we can spawn the unit, otherwise False
- Effect: If successful, spend resources equal to the provided unit’s cost and spawn the unit at the location

attempt_spawn_multiple(self, unit_type, locations):
- Input: A unit type string, a list of locations
- Output: An integer equal to the number of successful attempts to spawn a unit
- Effect: Spawn a unit of the provided type at each location provided, and spend resources equal to the total cost of the units successfully spawned.

attempt_remove(self, location):
- Input: A location with a friendly firewall on it
- Effect: Flag the firewall at the given location to be removed

attempt_remove_multiple(self, locations):
- Input: A list of locations with friendly firewalls
- Effect: Flag the firewalls at the given locations to be removed

type_cost(self, unit_type):
- Input: A unit type string
- Output: The cost to generate this unit

in_arena_bounds(self, location):
- Input: A location
- Output: True if the location is in bounds, False otherwise

contains_stationary_unit(self, location)
- Input: A location
- Output: A unit if there is a unit at the given location, False otherwise
- Note: An expression like `contains_stationary_unit(location) is True` returns False at all times as this function never produces the value True.

is_blocked(self, location):
- Input: A location
- Output: True if the location has a firewall built on it, False otherwise

filter_blocked_locations(self, locations):
- Input: A list of locations. Example: [[1,1], [13,25], [25,2]]
- Output: The same list, but with any blocked tiles removed. Blocked tiles are tiles that are out of bounds or that have firewalls built on them.

flip_over_x_axis(self, location):
- Input: A location
- Output: The location flipped over the x axis

flip_over_y_axis(self, location):
- Input: A location
- Output: The location flipped over the y axis

get_units(self, location):
- Input: A location
- Output: A list of units on that location. If the tile contains a firewall flagged for removal, the list will also contain a "RM" at the location

distance_between_locations(self, location1, location2):
- Input: Two locations
- Output: The distance between them (in tiles)

get_locations_in_range(self, location, radius):
- Input: A location, a radius
- Output: All of the locations that a unit at the provided `location` with range equal to `radius` will be able to target. The ranges you will most likely use are 5 (the range of the EMP), 3 (the range of other units), and 1.5 (the range of a self-destruct).

get_attackers(self, location, player_id):
- Input: A location and play_id of the 'defending' player
- Output: Each enemy tower that can attack this location

get_target(self, unit):
- Input: A game_unit
- Output: An instance of the `GameUnit` class representing the unit that the input unit would attack this frame
- Reminder: Detailed target priority can be found in the 'deep dive' game rules

get_edge_locations(self, quadrant_description):
- Input: A string, either ‘top_right’, ‘top_left’, ‘bottom_left’ or ‘bottom_right’
- Output: A list containing each of the tiles on the requested edge

find_path_to_edge(self, start_location, target_edge):
- Input: A location that a unit might stand at and a string representing one of the 4 edges (as seen above in get_edge_locations)
- Output: A list of locations, each representing the next step a unit will take when attempting to reach the target edge, in the order that they will take them, as well as a boolean 'True' or 'False' indicating weather we successfully reach the target location.
- Notes: This represents the ‘best guess’, as your opponent can place firewalls during their turn that you will not know about when you attempt pathfinding. In addition, for best use, it is recommended that the start_location is on some edge, the target_edge provided is the opposite edge. This will most accurately simulate a units real behavior.

find_path_to_location(self, start_location, target_location, player_id):
- Input: A location a soldier might be located at, a location the soldier wishes to reach, and the ID of the player who owns the soldier
- Output: A list of locations, each representing the next step a soldier will take when attempting to reach the target location, in the order the soldier will take them, as well as a boolean 'True' or 'False' indicating weather we successfully reach the target location.
- Notes: In addition to the notes for the find_path_to_edge function, keep in mind that there is no guarantee that the soldiers in game will want to path to the provided location.

get_map_copy(self, map_delta = None):
- Input: An optional map delta, representing changes to the game map. Should be in the form of a list of changes. Each change should be in the form [firewall_type, location].
- Output: A new GameMap, which you can change at will to generate hypothetical game states. Especially useful for testing how a unit will path given some hypothetical changes to the map.

## GameUnit

The GameUnit class represents one unit. You will most often access it by getting the list of units on a given tile via game_map.map[x][y] then getting a unit from this list.

### Useful attributes for GameUnits:

Note: Writing to these values can cause issues, and will likely make your algo fail.

- unit.type: A string corresponding to the Unit, “PI", “EI”, “SI”, “FF”, “EF” or “DF”
- unit.player_id: Always 1 if the unit is controlled by you or 2 if it is controlled by your enemy.
- unit.stationary: True if the unit is a firewall, False otherwise.
- unit.stability: An integer, the current stability of the unit
- unit.max_stability: An integer, the maximum stability of the unit
- unit.pending_removal: A bool, True if this unit is going to be removed soon, otherwise False

##Whats next?
This guide is designed to help you get an Algo you can be proud of into the Arena as quickly as possible, but to unlock the full potential of your algo you will have to dive deeper. We leave it as an additional challange to our top engineers to figure out how access game states during the action phase or previous turns, to rewrite our functions more efficiantly, or to otherwise push the limits on algo creation.
