#!/usr/bin/env python

'''
------------------------------------------------------------------------------------------------
Author: @Isaac
Last Updated: 7 Nov 2018
Contact: Message @Isaac at https://forum.c1games.com/
Copyright: CC0 - completely open to edit, share, etc

Short Description: 
This is a python script to run a bunch of algos against each other with a single command.
This is intended for when you have worked out all bugs and are testing to see if a new strategy really is better than an old one.
------------------------------------------------------------------------------------------------

README:

This program assumes this file is in the contributions/scripts directory

This program was originally built to run matches repeatedly, but I modified it since games are
mostly deterministic per comments of @n-sanders. If you want the original (PowerShell) code you can see it here:
https://forum.c1games.com/t/running-multiple-games/225

This script takes an input of algos and runs them in an arena format, matching each against
the others in every combination.

There are a variety of ways you can tell it what algos to run; I will give an example of each.

1st:
>py scripts/contributions/run_arena.py -a

This will run every single algo you have in the /algos/ directory against each other

2nd:
>py scripts/contributions/run_arena.py -s algo1 algo2 algo3 algo4 [...]

Where algo1,2,3,4,... are names of folders of algos (the same way you would run 1 match
except you list as many algos as you want to compete).

3rd:
>py scripts/contributions/run_arena.py -f algos.txt

Where algos.txt is a text file containing a list of all the algos you'd like to
compete. So an example file could look like this:

algos.txt:
algo1
algo2
algo3
...


Lastly, the final argument you can (and should) in combination with each of these
is -b, for batch_size. This controls how many games can run at one time to keep
this from melting your computer. The default is 5.

For example:
>py scripts/contributions/run_arena.py -a -b 6

This would run every single game like before, but 6 games at a time.

DO NOT RUN WITH A LARGE BATCH SIZE (like >15, depending on your computer) or else it will take forever and crash.


At the end I also run the get_results.py script that outputs some data. I recommend having
matplotlib installed for graphs, etc.

You can do much more with the get_results.py script that is not shown here and I plan
on expanding its capabilities.

If you have questions just ask me on the forums - @Isaac
'''

import sys
try:
	import os
	import subprocess
	import argparse
	import itertools
	import time
	import copy
	import multiprocessing as mp
except ImportError as e:
	print("WARNING: Module not found, full error:\n")
	print(str(e))
	sys.exit()


# Runs a single game
def run_single_game(process_command, algo1, algo2, max_name_len):
	p = subprocess.Popen(
		process_command,
		shell=True,
		stdout=subprocess.PIPE,
		stderr=subprocess.PIPE
		)
	output, error = p.communicate()
	# daemon necessary so game shuts down if this script is shut down by user
	p.daemon = 1
	p.wait()
	print("{: <30}{: <{fill}}   vs   {}".format('Finished running match:', algo1, algo2, fill=str(max_name_len)))

	# print (''.join(['{}\n'.format(x) for x in str(output).split('\\r\\n')])[1:])
	if str(error) != "b''":
		print ('Error with match - {} {}:\n\tError:\n{}'.format(algo1, algo2, error))

def run_match(arg1='', arg2='', max_name_len=0):
	# Get location of this run file
	file_dir = os.path.dirname(os.path.realpath(__file__)).replace('\\contributions', '')
	parent_dir = os.path.join(file_dir, os.pardir)
	parent_dir = os.path.abspath(parent_dir)

	# Get if running in windows OS
	is_windows = sys.platform.startswith('win')

	# Set default path for algos if script is run with no params
	default_algo = parent_dir + "\\algos\\starter-algo-ZIPME\\run.ps1" if is_windows else parent_dir + "/algos/starter-algo-ZIPME/run.sh" 
	algo1 = default_algo
	algo2 = default_algo

	# If script run with params, use those algo locations when running the game
	if arg1 != '':
		algo1 = arg1
	if arg2 != '':
		algo2 = arg2

	# If folder path is given instead of run file path, add the run file to the path based on OS
	# trailing_char deals with if there is a trailing \ or / or not after the directory name
	if is_windows:
		if "run.ps1" not in algo1:
			trailing_char = "" if algo1.endswith("\\") else "\\"
			algo1 = algo1 + trailing_char + "run.ps1"
		if "run.ps1" not in algo2:
			trailing_char = "" if algo2.endswith("\\") else "\\"
			algo2 = algo2 + trailing_char + "run.ps1"
	else:
		if "run.sh" not in algo1:
			trailing_char = "" if algo1.endswith('/') else "/"
			algo1 = algo1 + trailing_char + "run.sh"
		if "run.sh" not in algo2:
			trailing_char = "" if algo2.endswith('/') else "/"
			algo2 = algo2 + trailing_char + "run.sh"

	run_single_game("cd {} && java -jar engine.jar work {} {}".format(parent_dir, algo1, algo2), algo1.split('\\')[-2].replace('algos/',''),  algo2.split('\\')[-2].replace('algos/',''), max_name_len)

# handles all the arguments
def parse_args():
	ap = argparse.ArgumentParser(add_help=False, formatter_class=argparse.RawTextHelpFormatter)
	ap.add_argument('-h', '--help', action='help', help='show this help message and exit\n\n')
	ap.add_argument(
		"-a", "--all",
		action='store_true',
		help="if added will run every combination of all algos in the directory\n\n")
	ap.add_argument(
		"-s", "--specific",
		nargs='*',
		default=[],
		help="will run every combination of algos added\n\n")
	ap.add_argument(
		"-f", "--file",
		default='',
		help="will run every combination of algos in a specified file\n\n")
	ap.add_argument(
		"-b", "--batch",
		type=int,
		default=5,
		help="number of games to run at a single time (on seperate threads)\n\n")
	return vars(ap.parse_args())

# called by the -a arg, runs every algo in directory
def run_all():
	algos_dir = os.path.dirname(os.path.realpath(__file__)).replace('scripts\\contributions', '')+'algos\\'
	algos = os.listdir(algos_dir)
	matches = itertools.combinations(algos, 2)
	return matches

# called by the -s arg, runs the specified algos
def run_specific(algos):
	matches = itertools.combinations(algos, 2)
	return matches

# called by the -f arg, runs the algos in the passed file
def run_from_file(filePath):
	try:
		algos = [x.strip() for x in tuple(open(filePath, 'r'))]
		matches = itertools.combinations(algos, 2)
		return matches
	except FileNotFoundError:
		print ('File {} was not found'.format(filePath))
		sys.exit()

# returns the number of processess that are active
def get_num_running(processes):
	c = 0
	for i, proc in processes.items():
		if proc.is_alive():
			c += 1
	return c

# starts a subprocess for each match up to batch_size and then starts them as they finish
def run_matches(matches, batch_size):
	tmp = copy.deepcopy(matches)
	max_name_len = len(max(tmp, key=lambda e:len(e[0]))[0])

	algos = []
	processes = {}
	i = 0
	for match in matches:
		algos.append((match[0],match[1]))
		algo1 = 'algos/{}'.format(match[0])
		algo2 = 'algos/{}'.format(match[1])
		processes[i] = mp.Process(target=run_match, args=(algo1, algo2, max_name_len))
		i += 1

	for i in range(len(processes)):
		print ('{: <30}{: <{fill}}   vs   {}'.format('Starting match:', algos[i][0], algos[i][1], fill=str(max_name_len)))
		processes[i].start()
		i += 1
		while get_num_running(processes) >= batch_size:
			time.sleep(.1)

	while get_num_running(processes) > 0:
			time.sleep(.1)

	print ()
	print ('Finished all matches!')
	print ()

if __name__ == '__main__':
	args = parse_args() # get command line arguments

	if args['all']:
		print ('Running all algos')
		matches = run_all()
	elif len(args['specific']) > 0:
		matches = run_specific(args['specific'])
	elif args['file'] != '':
		matches = run_from_file(args['file'])
	else:
		print ('No arguments - no action taken')
		sys.exit()

	tmp = copy.deepcopy(matches)
	run_matches(matches, args['batch'])		# run all matches

	# if get_results is avalible, run a summary of the matches played
	try:
		args = {	'all':		False, 				\
					'verbose':	False, 				\
					'averages':	[], 				\
					'file':		[],					\
					'graph':	['wins'],	\
					'num':		len(list(tmp))		\
				}
		from get_results import main
		main(args)
	except Exception as e:
		print (e)
