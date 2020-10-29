# C1GamesStarterKit

Welcome to the C1 Terminal Starter Kit! The repository contains a collection of scripts and 
language-specific starter algos, to help you start your journey to develop the ultimate algo.

For more details about competitions and the game itself please check out our
[main site](https://terminal.c1games.com/rules).

## Manual Play

We recommend you familiarize yourself with the game and its strategic elements, by playing manually,
before you start your algo. Check out [the playground](https://terminal.c1games.com/playground).

## Algo Development

To test your algo locally, you should use the test_algo_[OS] scripts in the scripts folder. Details on its use is documented in the README.md file in the scripts folder.

For programming documentation of language specific algos, see each language specific README.
For documentation of the game-config or the json format the engine uses to communicate the current game state, see json-docs.html

For advanced users you can install java and run the game engine locally. Java 10 or above is required: [Java Development Kit 10 or above](http://www.oracle.com/technetwork/java/javase/downloads/jdk10-downloads-4416644.html).

All code provided in the starterkit is meant to be used as a starting point, and can be overwritten completely by more advanced players to improve performance or provide additional utility.

## Windows Setup

If you are running Windows, you will need Windows PowerShell installed. This comes pre-installed on Windows 10.
Some windows users might need to run the following PowerShell commands in adminstrator mode (right-click the 
PowerShell icon, and click "run as administrator"):
    
    `Set-ExecutionPolicy Unrestricted`
    
If this doesn't work try this:
    
    `Set-ExecutionPolicy Unrestricted CurrentUser`
    
If that still doesn't work, try these below:
    
    `Set-ExecutionPolicy Bypass`
    `Set-ExecutionPolicy RemoteSigned`
    
And don't forget to run the PowerShell as admin.

## Uploading Algos

Simply select the folder of your algo when prompted on the [Terminal](https://terminal.c1games.com) website. Make sure to select the specific language folder such as "python-algo" do not select the entire starterkit itself.

## Troubleshooting

For detailed troubleshooting help related to both website problems and local development check out [the troubleshooting section](https://terminal.c1games.com/rules#Troubleshooting).

#### Python Requirements

Python algos require Python 3 to run. If you are running Unix (Mac OS or Linux), the command `python3` must run on 
Bash or Terminal. If you are running Windows, the command `py -3` must run on PowerShell.
   
#### Java Requirements

Java algos require the Java Development Kit. Java algos also require [Gradle]
(https://gradle.org/install/) for compilation.
   
## Running Algos

To run your algo locally or on our servers, or to enroll your algo in a competition, please see the [documentation 
for the Terminal command line interface in the scripts directory](https://github.com/correlation-one/AIGamesStarterKit/tree/master/scripts)
