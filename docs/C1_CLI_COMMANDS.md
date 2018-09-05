### Using the C1 CLI

In the below examples, we assume your working directory is C1GamesStarterKit and you are storing
your algos in the algos/ directory

#### Creating your first algo

Fork the provided `starter-algo` to create a modifiable base of your own. You will likely want to
give your algos descriptive names but for this example we will create an algo called
`my-algo`.

    $ scripts/fork_algo.sh algos/starter-algo algos/my-algo

Modify the files in `algos/my-algo/` to create your own strategy.

#### Running matches locally between algos

Easily run a match between two local algos using the `run_match.sh` script. The resulting replay
file will be saved in the replays/ directory and can be uploaded and watched on
https://terminal.c1games.com/playground.

For example, if you wanted to run `starter-algo` against the `my-algo` of your own creation in
the command line, you can cd into the C1GamesStarterKit and run the following command:

    $ scripts/run_match.sh algos/starter-algo algos/my-algo

This will also save a replay file in replays/, which you can upload on our site to watch your game

#### Uploading your algo

Zip the entire algo directory or run the `archive_algo.sh` script to zip an algo. It will be saved in
the /dist directory and can then be uploaded on terminal.c1games.com/myalgos to compete in ranked matches.

While using C1GamesStarterKit as your working directory, to zip an algo in the algos folder, you can use

    $ scripts/archive_algo.sh algos/my-algo dist/my-algo.zip

### Custom Config

Customize the "debug" values in game-configs.json to control the level of error/debug information printed during a match.

