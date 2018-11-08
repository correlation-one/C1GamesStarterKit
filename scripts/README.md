## Terminal Command Line Interface

These guides assume that your working directory is the root of this repository.

#### Creating your algo

Once you have selected one of the supported algo languages within this repository, such as `python-algo` 
or `java-algo`, refer to the README within that directory for language-specific instructions for 
creating an algo.

If you want, you can duplicate of of the algo directories, and create your algo by modifying the copy. 
This allows you to compare your algo to, and run your algo against, the original starter algo.

#### Running local matches

This repository includes the game engine, `engine.jar`, in which games are run. You can use this to run
a game between two algos, which will create a .replay file that you can view on 
[https://terminal.c1games.com/playground](https://terminal.c1games.com/playground)

We provide scripts to make the running of the matches easier: `run_match.sh` for unix, `run_match.ps1` 
for windows, and `run_match.py` for any environment which supports python. 

Simply:
- If applicable, compile your algos (read language-specific README)
- Run the script with the two directories which contain the `run.sh` entrypoint
- The replay file will appear the the `replays` directory.

For example, you can run:

```
$ scripts/run_match.sh python-algo java-algo/algo-target
```

#### Uploading your algo

Zip your algo with the platform-appropriate `zipalgo` binary, found in the `scripts` directory. This
will generate a deflated zip archive, while ignoring globs found in a .zipignore file in the directory 
being zipped. The .zipignore file works like a .gitignore file, but excludes files from the zip archive.

For example, you can run:

./scripts/zipalgo_mac python-algo my-python-algo.zip




### Using the C1 CLI

In the below examples, we assume your working directory is C1GamesStarterKit and you are storing
your algos in the algos/ directory

#### Creating your first algo

Fork the provided `starter-algo` to create a modifiable base of your own. You will likely want to
give your algos descriptive names but for this example we will create an algo called
`my-algo`.

    $ scripts/fork_algo.sh algos/starter-algo-ZIPME algos/my-algo

Modify the files in `algos/my-algo/` to create your own strategy.

#### Running matches locally between algos

Easily run a match between two local algos using the `run_match.sh` script. The resulting replay
file will be saved in the replays/ directory and can be uploaded and watched on
https://terminal.c1games.com/playground.

For example, if you wanted to run `starter-algo` against the `my-algo` of your own creation in
the command line, you can cd into the C1GamesStarterKit and run the following command:

    $ scripts/run_match.sh algos/starter-algo-ZIPME algos/my-algo

This will also save a replay file in replays/, which you can upload on our site to watch your game

#### Uploading your algo

Zip the entire algo directory or run the `archive_algo.sh` script to zip an algo. It will be saved in
the /dist directory and can then be uploaded on terminal.c1games.com/myalgos to compete in ranked matches.

While using C1GamesStarterKit as your working directory, to zip an algo in the algos folder, you can use

    $ scripts/archive_algo.sh algos/my-algo dist/my-algo.zip

### Custom Config

Customize the "debug" values in game-configs.json to control the level of error/debug information printed during a match.
