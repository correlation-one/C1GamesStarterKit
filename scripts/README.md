## Terminal Command Line Interface

These guides assume that your working directory is the root of this repository.

#### Creating your algo

Once you have selected one of the supported algo languages within this repository, such as `python-algo` 
or `java-algo`, refer to the README within that directory for language-specific instructions for 
creating an algo.

If you want, you can duplicate the algo directories, and create your algo by modifying the copy. 
This allows you to compare your algo to, and run your algo against, the original starter algo.

#### Testing your algo locally

You can test your algo locally for simple syntax and semantic errors without having to run the game engine by using our new test_algo scripts: test_algo_mac test_algo_linux test_algo_windows depending on your operating system.
Code for this script located at https://github.com/correlation-one/test_algo

To run the script follow this format: ./scripts/test_algo_mac {algo directory} {replay location (Optional)}
The way the script works is that it runs your algo and feeds it test states from a replay file. Your algo will send its turns but the states will be based on the replay not what your algo does. So you should be able to quickly test for syntax and semantic errors before you upload to the website for detailed strategic testing.

You can also use this script to test what your algo does given a specific state by pointing it to a replay that contains that state. So if your algo seems to crash in a specific replay, just download the replay and use this script to see the errors in your algo locally.

Note if using a compiled language (java, rust) make sure the {algo directory} argument points to where the compiled algo lives that contains the run.sh, which defaults to the algo-target folder.

Examples: 

On Unix:
```
$ ./scripts/test_algo_mac python-algo/
$ ./scripts/test_algo_mac java-algo/algo-target/
$ ./scripts/test_algo_mac java-algo/algo-target/ ~/Downloads/my_replay.replay
```
On Windows:
```
> .\scripts\test_algo_windows.exe .\rust-algo\algo-target\
> .\scripts\test_algo_windows.exe .\rust-algo\algo-target\ C:\Users\Justin\Downloads\my_replay.replay
```

#### Running local matches

We recommend using the test_algo scripts to quickly test for errors and use the website to test your algo thoroughly however for advanced users they may wish to play matches locally. For example, to play your algo against itself when doing machine learning. This section describes how to do that.

This repository includes the game engine, `engine.jar`, in which games are run. You can use this to run
a game between two algos, which will create a .replay file that you can view on 
[https://terminal.c1games.com/playground](https://terminal.c1games.com/playground)

We provide scripts to make the running of the matches easier: `run_match.sh` for unix, `run_match.ps1` 
for windows, and `run_match.py` for any environment which supports python. The `run_match.py` script is 
recommended as it is more robust and easier to use.

Simply:
- If applicable, compile your algos (read language-specific README)
- Run the script with the two directories which contain the `run.sh` entrypoint, 
or leave argument empty to default to python-algo.
- The replay file will appear in the `replays` directory.

For example, you can run,

On Unix:
```
$ scripts/run_match.sh python-algo java-algo/algo-target
$ python3 ./scripts/run_match.py java-algo/algo-target java-algo/algo-target
```
On Windows:
```
$ scripts\run_match.ps1 java-algo/algo-target python-algo
$ py -3 run_match.py
```

For details on modifying how a game is run locally including what is displayed, and time limits, check out the game-configs.json file in the parent directory. Documentation on what the variables do is available on [the doc server](https://docs.c1games.com/json-docs.html#config).


#### Uploading your algo

Zip your algo with the platform-appropriate `zipalgo` binary, found in the `scripts` directory. This
will generate a deflated zip archive, while ignoring globs found in a .zipignore file in the directory 
being zipped. The .zipignore file works like a .gitignore file, but excludes files from the zip archive.

For example, you can run:

./scripts/zipalgo_mac python-algo my-python-algo.zip
