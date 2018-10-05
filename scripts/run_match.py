import os
import subprocess
import sys

file_dir = os.path.dirname(os.path.realpath(__file__))
parent_dir = os.path.join(file_dir, os.pardir)
parent_dir = os.path.abspath(parent_dir)

def runSingleGame(process_command):
    print("Start run a match")
    p = subprocess.Popen(
        process_command,
        shell=True,
        stdout=sys.stdout,
        stderr=sys.stderr
        )
    p.daemon = 1
    p.wait()
    print("Finished running match")

default_algo = parent_dir + "/algos/starter-algo/run.sh"
algo1 = default_algo
algo2 = default_algo
if len(sys.argv) > 1:
    algo1 = sys.argv[1]
if len(sys.argv) > 2:
    algo2 = sys.argv[2]

print("Algo 1: ", algo1)
print("Algo 2:", algo2)

runSingleGame("cd {} && java -jar engine.jar work {} {}".format(parent_dir, algo1, algo2))