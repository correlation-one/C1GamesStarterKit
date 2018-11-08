#!/usr/bin/env python

'''
------------------------------------------------------------------------------------------------
Author: @Isaac
Last Updated: 8 Nov 2018
Contact: Message @Isaac at https://forum.c1games.com/
Copyright: CC0 - completely open to edit, share, etc

Short Description: 
This is a file to help display data about Terminal matches.
(NOTE: currently views matches that end with the same health as a tie, does not track time spent)
------------------------------------------------------------------------------------------------

README:

This program assumes this file is in the contributions/scripts directory

You can call this by opening Powershell or Terminal the same way you would start a game.
Then, you can run it by executing:
>py [PATH_TO_FILE]/get_results.py
where PATH_TO_FILE is the path to this file.

Just running this should output that looks something like this:
Getting Results:

-----------------------------------------------------------------------------------
Showing p1-18-10-2018-13-51-45-1539892305554--547739375.replay
-----------------------------------------------------------------------------------
my-bot:
|
|      End Stats:
|      |               stationary_resource_spent : 343.0
|      |                dynamic_resource_spoiled : 381.1
|      |                                 crashed : False
|      |              dynamic_resource_destroyed : 25.0
|      |                  dynamic_resource_spent : 29.0
|      |       stationary_resource_left_on_board : 0.0
|      |                           points_scored : 4.0
|      |                  total_computation_time : 58238

starter-algo-ZIPME:
|
|      End Stats:
|      |               stationary_resource_spent : 101.0
|      |                dynamic_resource_spoiled : 125.1
|      |                                 crashed : False
|      |              dynamic_resource_destroyed : 222.0
|      |                  dynamic_resource_spent : 312.0
|      |       stationary_resource_left_on_board : 98.0
|      |                           points_scored : 30.0
|      |                  total_computation_time : 103

By default, this will run the replay file that was created the most recently.

----------------------------------------------------------------------------------------
-f: Run specific replay files

You can specify which file you would like to run by:
>py scripts/contributions/get_results.py -f [REPLAY_FILE].replay

where REPLAY_FILE is the file you'd like to look at. You can list as many files as you would like and it will run on each file. For example:
>py scripts/contributions/get_results.py -f [REPLAY_FILE].replay [REPLAY_FILE].replay [REPLAY_FILE].replay

----------------------------------------------------------------------------------------
-n: Run a number of replay files from most recent to olders (by date modified)

You can specify how many replays back you would like to run (by date) using the -n parameter. Example:
>py scripts/contributions/get_results.py -n 3

would run the last 3 games you ran

----------------------------------------------------------------------------------------
-avg: Print average data fro a single replay (not very useful right now)

You can output the averages for health, bits, cores, etc for a single match by using the following:
>py scripts/contributions/get_results.py -avg health

The only (currently) accepted parameters for -avg are:
	- health
	- bits
	- cores
	- cores_spent
	- bits_spent
	- cores_on_board

You can include 1, 2, or all in your output. For example:
>py scripts/contributions/get_results.py -avg health bits cores

----------------------------------------------------------------------------------------
-g: Graphing (require matplotlib)

You can install matplotlib by doing:
>pip3 install matplotlib

If you install matplotlib you can graph the following for individual matches:
	- health
	- bits
	- cores
	- cores_spent
	- bits_spent
	- cores_on_board

Simply do:
>py scripts/contributions/get_results.py -g [PARAMETERS]
Where PARAMETERS is a list of the above options you would like to graph

For example:
>py scripts/contributions/get_results.py -g health

You can get more specfic and choose when you would like a new graph, using ':' as a delimiter.

For example:
>py scripts/contributions/get_results.py -g health : bits cores

would show 2 graphs. The first would show health and the second would plot bits and cores on the same graph.

(I recommend just trying a bunch of combinations with ':' to get familiar with this).

----------------------------------------------------------------------------------------

All of the commands above can be combined in any order. For example, if I wanted to run the
last replay file and output the average heath and graph the number of bits, I would run:
>py scripts/contributions/get_results.py -avg health -g bits

If you forget anything you can see all possible commands by:
>py scripts/contributions/get_results.py -h

----------------------------------------------------------------------------------------

There are essentially 2 paths this program takes, whether you are looking at 1 replay or many.
If you are looking at 1, it prints out information for that replay.
The moment you add more it then prints a summary for those replays (currently only wins).
You can force the program to print information for each individual replay by using the -v (verbose) flag.

For example:
>py scripts/contributions/get_results.py -a -g health wins -v

Will display and graph (health) for each individual replay, as well as display the summary
information and graph the number of wins for each algo.

In contrast:
>py scripts/contributions/get_results.py -a -g health wins

Will only display a summary and show the graph for wins (health graph parameter is simply
ignored).

Note that the ':' still works for separating graphs when using the -v (verbose) flag.
For example:
>py scripts/contributions/get_results.py -a -g health : bits : cores wins -v

The program also automatically formats the graph input so these run the same:
>py scripts/contributions/get_results.py -n 2 -g health : bits : cores wins -v
>py scripts/contributions/get_results.py -n 2 -g health : bits : cores : wins -v
>py scripts/contributions/get_results.py -n 2 -g : : : :: typo health : : bits : cores : : wins : : : : -v

----------------------------------------------------------------------------------------

Everything is output using std.stderr.write, meaning it is safe to import and print
this from your within game (although there is not really a reason to, since it looks at
all the data after the replay is completed).

I plan on adding more to this file, specifically the ability to graph much more
data and get more useful statistics.

If you have any suggestions/questions let me know :) - @Isaac
'''

pltInstalled = False

try:
	import os
	import sys
	import json
	import glob
	import math
	import argparse
except ImportError as e:
	sys.stderr.write("WARNING: Module not found, full error:\n\n")
	sys.stderr.write(e)

try:
	import matplotlib.pyplot as plt
	pltInstalled = True
except ImportError:
	try:
		usrIn = input('Matplotlib not found.\nWould you like this program to try and install matplotlib? (y/n) ')
		if usrIn.lower() == 'y' or usrIn.lower() == 'yes':
			import subprocess
			subprocess.run(['python', '-m', 'pip', 'install', 'matplotlib'])

			import matplotlib.pyplot as plt
			pltInstalled = True
			sys.stderr.write("\n\n")
	except:
		pltInstalled = False

# handles all the arguments
def ParseArgs():
	ap = argparse.ArgumentParser(add_help=False, formatter_class=argparse.RawTextHelpFormatter)
	ap.add_argument('-h', '--help', action='help', help='show this help message and exit\n\n')
	ap.add_argument(
		"-n", "--num",
		default=1,
		help="number of files (in order of date created) to analyze\n\n")
	ap.add_argument(
		"-a", "--all",
		action='store_true',
		help="runs every replay file in replay folder\n\n")
	ap.add_argument(
		"-v", "--verbose",
		action='store_true',
		help="will force the program to run each replay seperately and print information individual games\n\n")
	ap.add_argument(
		"-avg", "--averages",
		nargs="*",
		default=[],
		help="data you would like the average of (not very useful right now)\nValid Options:\n\t- health\n\t- bits\n\t- cores\n\t- cores_spent\n\t- bits_spent\n\t- cores_on_board\n\n")
	ap.add_argument(
		"-f", "--file",
		nargs="*",
		default=[],
		help="specify a replay file (or multiple) you'd like to analyze\n\n")
	ap.add_argument(
		"-g", "--graph",
		nargs="*",
		default=[],
		help="specify what data you would like to be graphed - you must have matplotlib installed\n\nValid Options For Single Game:\n\t- health\n\t- bits\n\t- cores\n\t- cores_spent\n\t- bits_spent\n\t- cores_on_board\n\nValid Options For Multiple Games:\n\t- wins\n\n")
	return vars(ap.parse_args())


class Graph:
	numRows, numCols = 0,0
	fig, ax, arg = None, None, None
	pos = (0,0)
	emptyPlots = []

	verbose_options = ['health', 'bits', 'cores', 'cores_spent', 'bits_spent', 'cores_on_board']
	summary_options = ['wins']

	@staticmethod
	def init(arg):
		Graph.clear()

		numSubPlots = arg.count(':') + 1
		r = math.floor(math.sqrt(numSubPlots))
		c = math.ceil(numSubPlots/r)

		fig_size = [6.4, 4.8]
		max_x, max_y = 15, 9
		fig_size = [fig_size[0] * c, fig_size[1] * r]
		if fig_size[0] > max_x: fig_size[0] = max_x
		if fig_size[1] > max_y: fig_size[1] = max_y
		plt.rcParams["figure.figsize"] = fig_size

		Graph.fig, Graph.ax = plt.subplots(nrows=r, ncols=c)

		if r == 1:
			Graph.ax = [Graph.ax]
		if c == 1:
			Graph.ax = [Graph.ax]

		Graph.emptyPlots = [(x, y) for y in range(r) for x in range(c)]

	@staticmethod
	def advance():
		x,y = Graph.pos
		try:
			Graph.ax[y][x+1]
			Graph.pos = (x+1 , y)
		except IndexError:
			Graph.ax[y+1][0]
			Graph.pos = (0, y+1)

	@staticmethod
	def resetPos():
		Graph.pos = (0,0)

	@staticmethod
	def addToPlot(data, lbl, xlabel, ylabel):
		x,y = Graph.pos
		Graph.ax[y][x].plot(data, label=lbl)

		Graph.ax[y][x].set_xlabel(xlabel)
		Graph.ax[y][x].set_ylabel(ylabel)
		Graph.ax[y][x].legend(loc='best')

		Graph.removePos()

	@staticmethod
	def addBar(y_pos, data, lbls, y_ticks, ylabel, title, rot=60):
		x,y = Graph.pos
		Graph.ax[y][x].bar(y_pos, data, align='center', width=0.65)

		Graph.ax[y][x].set_xticks(y_pos)
		Graph.ax[y][x].set_xticklabels(lbls, rotation=rot)
		Graph.ax[y][x].set_yticks(y_ticks)
		Graph.ax[y][x].set_ylabel(ylabel)
		Graph.ax[y][x].set_title(title)

		Graph.removePos()

	@staticmethod
	def removePos():
		try:
			Graph.emptyPlots.remove(Graph.pos)
		except ValueError:
			pass

	@staticmethod
	def removeEmpty():
		for (x,y) in Graph.emptyPlots:
			Graph.ax[y][x].axis('off')

	@staticmethod
	def show():
		plt.tight_layout()
		Graph.removeEmpty()
		plt.show()

	@staticmethod
	def clear():
		plt.close()

# Stores data pertaining to an individual Algo
class Algo:
	def __init__(self, name):
		self.name = name
		self.wins = 0
		self.cores_on_board = {}
		self.replays = {} 	# this effectively holds all raw json information

	# NOTE: eq will return true when comparing to strings of the same name - this is intentional to be able to use: str in listOfAlgos syntax.
	def __eq__(self, other):
		if type(other) == str:
			return self.name == other
		return self.name == other.name
	def __toString(self):
		return self.name
	def __str__(self):
		return self.__toString()
	def __repr__(self):
		return self.__toString()

	def getAverage(self, arg, replay):
		avg = 0.0
		div = 0.0

		for replay in self.replays:
			div += len(self.replays[replay])
			for turn in self.replays[replay]:
				if turn == 'endStats': continue
				avg += float(self.replays[replay][turn][arg])

		try:
			return avg / div
		except ZeroDivisionError:
			sys.stderr.write("Error: Dividing by zero")
			return -1

	def addData(self, replay, turn, arg, data, cumulative=False):
		if replay in self.replays:
			if turn in self.replays[replay]:
				pass
			else:
				self.replays[replay][turn] = {}
		else:
			self.replays[replay] = {}
			self.replays[replay][turn] = {}

		if cumulative:
			try:
				self.replays[replay][turn][arg] = self.replays[replay][turn-1][arg] + data
			except KeyError:
				self.replays[replay][turn][arg] = data
		else:
			self.replays[replay][turn][arg] = data


	def recordFinalData(self, replay, other):
		selfHP = list(self.replays[replay].items())[-1][1]['health']
		otherHP = list(other.replays[replay].items())[-1][1]['health']

		if selfHP > otherHP:
			self.wins += 1

	def addEndStats(self, replay, endStats):
		self.replays[replay]['endStats'] = endStats;

	def printBlock(self, header, data):
		hLen = 7

		sys.stderr.write('|\n|{: >6}{}:\n'.format('', header))
		for arg in data:
			val = round(data[arg], 1) if type(data[arg]) == int or type(data[arg]) == float else data[arg]
			sys.stderr.write('|{: >{fill}}{: >40} : {}\n'.format('|', arg, val, fill=hLen))

	def printAvgs(self, options, arg, replay):
		data = {}
		if len(options[arg]) > 0:
			for lbl in options[arg]:
				try:
					data[lbl] = self.getAverage(lbl, replay)
				except KeyError:
					sys.stderr.write('Invalid parameter \'{}\'\n'.format(lbl))

			self.printBlock('Averages', data)

	def printEndStats(self, replay):
		del self.replays[replay]['endStats']['name']
		self.printBlock('End Stats', self.replays[replay]['endStats'])

	def dispData(self, options, replay):
		sys.stderr.write('{}:\n'.format(self))
		for arg in options:
			if arg == 'avg':
				self.printAvgs(options, arg, replay)
			elif arg == 'endStats':
				self.printEndStats(replay)
		sys.stderr.write('\n')

	def addPlot(self, options, replay, xlabel='Turn #', ylabel='Value'):
		disp = False
		for lbl in options:
			if lbl == ':':
				Graph.advance()
			else:
				disp = True
				data = [self.replays[replay][turn][lbl] for turn in self.replays[replay] if turn != 'endStats']
				Graph.addToPlot(data, '{}\'s {}'.format(self, lbl), xlabel, ylabel)
		Graph.resetPos()

		return disp


# Stores data from a single replay and creates the Algo classes
class Replay:
	def __init__(self, fName, algos):
		self.fname = fName;
		self.ref = None
		self.turns = {}
		self.validTurns = []

		self.loadData()				# handles loading all the data from file into python variables
		self.unpackData(algos)		# stores relevant data after it has been loaded

	def __eq__(self, other):
		return self.fname == other.fname
	def __toString(self):
		return self.fname
	def __str__(self):
		return self.__toString()
	def __repr__(self):
		return self.__toString()

	def loadData(self):
		with open(self.fname) as f:
			for line in f:
				line = line.replace("\n", "")
				line = line.replace("\t", "")

				if (line != ''):
					data = json.loads(line)

					try:
						data['debug']
						self.ref = data
					except:
						turnNum = data['turnInfo'][1]
						frameNum = data['turnInfo'][2]
						self.turns[(turnNum, frameNum)] = data
						if (turnNum, frameNum) not in self.validTurns:
							self.validTurns.append((turnNum, frameNum))

	def getCoresOnBoard(self, filters, encryptors, destructors):
		return len(filters) + len(encryptors) * 4 + len(destructors) * 3

	def getBitsSpent(self, algo, spawn):
		p_index = 1 if algo == self.algo1 else 2
		pings = [x for x in spawn if x[3] == p_index and x[1] == 3]
		emps = [x for x in spawn if x[3] == p_index and x[1] == 4]
		scramblers = [x for x in spawn if x[3] == p_index and x[1] == 5]
		return len(pings) + len(emps) * 3 + len(scramblers)

	def getCoresSpent(self, algo, spawn):
		p_index = 1 if algo == self.algo1 else 2
		filters = [x for x in spawn if x[3] == p_index and x[1] == 0]
		encryptors = [x for x in spawn if x[3] == p_index and x[1] == 1]
		destructors = [x for x in spawn if x[3] == p_index and x[1] == 2]
		return len(filters) + len(encryptors) * 4 + len(destructors) * 3

	def addDataToAlgo(self, algo, t, f, stats, units, spawn):
		algo.addData(self.fname, t, 'health', stats[0])
		algo.addData(self.fname, t, 'cores', stats[1])
		algo.addData(self.fname, t, 'bits', stats[2])

		filters, encryptors, destructors, pings, emps, scramblers, removes = units

		algo.addData(self.fname, t, 'cores_on_board', self.getCoresOnBoard(filters, encryptors, destructors))

		if f == 0:
			algo.addData(self.fname, t, 'cores_spent', self.getCoresSpent(algo, spawn), True)
			algo.addData(self.fname, t, 'bits_spent', self.getBitsSpent(algo, spawn), True)

	def unpackData(self, algos):
		try:
			self.algo1, self.algo2 = self.createAlgos(algos)

			for t, f in self.getValidTurns():
				turn = self.getTurn(t, f)

				turnInfo = turn['turnInfo']
				events = turn['events']
				spawn = events['spawn']

				p1Stats = turn['p1Stats']
				p1Units = turn['p1Units']

				p2Stats = turn['p2Stats']
				p2Units = turn['p2Units']

				self.addDataToAlgo(self.algo1, t, f, p1Stats, p1Units, spawn)
				self.addDataToAlgo(self.algo2, t, f, p2Stats, p2Units, spawn)

			self.algo1.recordFinalData(self.fname, self.algo2)
			self.algo2.recordFinalData(self.fname, self.algo1)
			self.algo1.addEndStats(self.fname, self.turns[self.validTurns[-1]]['endStats']['player1'])
			self.algo2.addEndStats(self.fname, self.turns[self.validTurns[-1]]['endStats']['player2'])
		except Exception as e:
			sys.stderr.write(str(e))

	# only creates a new algo class if that algo does not already exist. Otherwise data is added to the existing one
	def createAlgos(self, algos):
		endStats = self.turns[self.validTurns[-1]]['endStats']
		p1Algo = endStats['player1']['name']
		p2Algo = endStats['player2']['name']

		if p1Algo not in algos:
			algo1 = Algo(p1Algo)
			algos.append(algo1)
		else:
			algo1 = algos[algos.index(p1Algo)]

		if p2Algo not in algos:
			algo2 = Algo(p2Algo)
			algos.append(algo2)
		else:
			algo2 = algos[algos.index(p2Algo)]

		return algo1, algo2

	def getAlgos(self):
		return [self.algo1, self.algo2]

	def getValidTurns(self):
		return self.validTurns
	def getTurns(self):
		return self.turns
	def getTurn(self, turn, frame=-1):
		return self.turns[(turn, frame)]

# handles opening multiple games (replays)
class FileHandler:
	def __init__(self):
		self.replays = []
		self.algos = []

	def getAlgoWinSummary(self):
		fillLen = len(max(self.algos, key=lambda e:len(e.name)).name) + 9
		rtn = 'Wins by algo:\n|\n'
		for algo in sorted(self.algos, key=lambda e:-1*e.wins):
			rtn += '|{: >{fill}} : {}\n'.format(algo.name, algo.wins, fill=fillLen)

		return rtn

	def getReplays(self):
		return self.replays

	def getLastReplay(self):
		return self.replays[0] if len(self.replays) > 0 else None

	def getReplay(self, i=0):
		if i >= len(self.replays):
			sys.stderr.write("Invalid replay")
			return None
		return self.replays[i]

	def __latestReplays(self, num=1, a=False):
		replay_dir = os.path.dirname(os.path.realpath(__file__)).replace('scripts\\contributions', '')+'replays\\'
		files = glob.glob('{}*.replay'.format(replay_dir))
		files = sorted(files, key=os.path.getctime, reverse=True)
		if a:
			return files
		return files[:num]

	def loadFiles(self, num=1, a=False, fNames=[]):
		if len(fNames) > 0:
			for fName in fNames:
				if fName.find('replays') == -1:
					self.replays.append(Replay('replays/'+fName, self.algos))
				else:
					self.replays.append(Replay(fName, self.algos))
		else:
			for fName in self.__latestReplays(num, a):
				self.replays.append(Replay(fName, self.algos))

	def addPlot(self, lbl):
		if lbl == 'wins':
			wins = []
			lbls = []

			for algo in self.algos:
				wins.append(algo.wins)
				lbls.append(algo.name)

			y_pos = range(len(self.algos))
			y_ticks = range(max(wins)+2)
			while len(y_ticks) > 20:
				y_ticks = [x for x in y_ticks if x % 2 == 0]

			Graph.addBar(y_pos, wins, lbls, y_ticks, '# of Wins', 'Number of Wins per Algo')
		elif lbl == ':':
			Graph.advance()


# displays detailed data for every replay stored in the fileManager fh.
def run_every_replay_verbose(fh, graphingEnabled, options):
	for replay in fh.getReplays():
		sys.stderr.write('{:->75}\n'.format(''))
		sys.stderr.write('Showing {}\n'.format(replay.fname.split('\\')[-1]))
		sys.stderr.write('{:->75}\n'.format(''))

		if graphingEnabled:
			disp = False
			Graph.init(options['graph_verbose'])

		try:
			for algo in replay.getAlgos():
				algo.dispData(options, replay.fname)

				if graphingEnabled:
					if algo.addPlot(options['graph_verbose'], replay.fname):
						disp = True
		except Exception as e:
			sys.stderr.write('Error parsing file\n')
			sys.stderr.write(str(e)+'\n')


		if graphingEnabled:
			if disp:
				Graph.show()

		sys.stderr.write('\n')

# displayed aggregate data over many matches and replay files
def run_every_replay_agg(fh, graphingEnabled, options):
	sys.stderr.write('{:->75}\n'.format(''))
	sys.stderr.write('Summary of {} matches:\n'.format(len(fh.getReplays())))
	sys.stderr.write('{:->75}\n'.format(''))
	sys.stderr.write(fh.getAlgoWinSummary())

	if graphingEnabled:
		if len(options) == 0:
			options = ['wins']
		Graph.init(options)
		for option in options:
			fh.addPlot(option)
		Graph.show()

# parses the graphing arguments, seperates them into single (v) or multiple (s) results with the ':' delimiter
def getGraphOptions(options):
	v = []
	s = []

	vBreak = False
	sBreak = False
	for o in options:
		if o in Graph.verbose_options:
			v.append(o)
			vBreak = True
		elif o in Graph.summary_options:
			s.append(o)
			sBreak = True
		elif o == ':':
			if vBreak:
				v.append(':')
			if sBreak:
				s.append(':')

			vBreak = False
			sBreak = False

	if len(v) > 0:
		if v[0] == ':': v.pop(0)
		if v[-1] == ':': v.pop(-1)
	if len(s) > 0:
		if s[0] == ':': s.pop(0)
		if s[-1] == ':': s.pop(-1)

	return (v, s)

def main(args):
	verbose_options, summary_options = getGraphOptions(args['graph'])

	fh = FileHandler()
	fh.loadFiles(int(args['num']), args['all'], args['file']) #loads the files - all JSON reading is here

	# check to see if matplotlib is installed
	graphingEnabled = True if len(args['graph']) > 0 else False
	if graphingEnabled and not pltInstalled:
		sys.stderr.write("\n\nWARNING: matplotlib not installed - no graphs will be shown\n\n")
		graphingEnabled = False

	# these options are passed to let the algo know what to display and add to the plots
	options = {
				'avg':				args['averages'],
				'endStats':			None,
				'graph_verbose':	verbose_options,
				'graph_summary':	summary_options
			  }

	# checks the arguments to see what inforation should be displayed
	if args['all']:
		run_every_replay_verbose(fh, graphingEnabled, options) if args['verbose'] else ''
		run_every_replay_agg(fh, graphingEnabled, options['graph_summary'])
	elif int(args['num']) == 1:
		run_every_replay_verbose(fh, graphingEnabled, options)
	elif int(args['num']) > 1 or len(args['file']) > 0:
		run_every_replay_verbose(fh, graphingEnabled, options) if args['verbose'] else ''
		run_every_replay_agg(fh, graphingEnabled, options['graph_summary'])

	sys.stderr.write('\n\n')


if __name__ == '__main__':
	args = ParseArgs() # get command line arguments
	main(args)
