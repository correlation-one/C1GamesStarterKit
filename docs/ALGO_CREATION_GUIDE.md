# Step-by-step Startup:

1. Download `starter-algo.zip` and unzip the folder
2. Open the file ‘algo_strategy.py’
3. In this file, you can see a starter algo strategy, with various examples of basic algo functionality and comments explaining how to customize the algo.
4. When you are done, you can rename the ‘unzipped’ folder (starter-algo) whatever you want. This will be the name of your Algo! Note: Renaming other files could cause problems.
5. That’s it! Your zipped algo is ready to compete in the arena!

# Detailed Documentation for Creators

## Some of the common parameters taken or returned by functions

### Location:
A list with two integers corresponding to the x, y coordinate of a tile in the grid
- Example: [9,13]

### player_id:
0 indicates you, 1 indicates your opponent

## GameMap (game_map)

This class is a representation of the current game state, and contains many helper methods to simplify placing units, determining paths, and other common actions.
The starting strategy many algos are based off of creates ‘game_map’, which can be used to access these methods. Examples of using game_map to use these methods can be seen within the starter strategy.

## GameUnit

The GameUnit class represents one unit. You will most often access it by getting the list of units on a given tile via game_map.map[x,y] then getting a unit from this list.

##Whats next?
This guide is designed to help you get an Algo you can be proud of into the Arena as quickly as possible, but to unlock the full potential of your algo you will have to dive deeper. We leave it as an additional challange to our top engineers to figure out how access game states during the action phase or previous turns, to rewrite our functions more efficiantly, or to otherwise push the limits on algo creation.
