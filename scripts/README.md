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
$ python3 run_match.py java-algo/algo-target java-algo/algo-target
```
On Windows:
```
$ scripts\run_match.ps1 java-algo/algo-target python-algo
$ py -3 run_match.py
```

#### Uploading your algo

Zip your algo with the platform-appropriate `zipalgo` binary, found in the `scripts` directory. This
will generate a deflated zip archive, while ignoring globs found in a .zipignore file in the directory 
being zipped. The .zipignore file works like a .gitignore file, but excludes files from the zip archive.

For example, you can run:

./scripts/zipalgo_mac python-algo my-python-algo.zip
