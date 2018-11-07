'''

This is a file to help display data about Terminal matches.
This file should be in the scripts/contributions/ directory.

You can call this by opening Powershell or Terminal the same way you would start a game.
Then, you can run it by executing:
>py [PATH_TO_FILE]/[FILE_NAME].py
where FILE_NAME is the name of this file.

Just running this should output that looks something like this:
Getting Results:

-----------------------------------------------------------------------------------
Showing replays\p1-18-10-2018-13-51-45-1539892305554--547739390.replay
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

You can specify which file you would like to run by:
>py scripts/contributions/[FILE_NAME].py -f [REPLAY_FILE].replay
where REPLAY_FILE is the file you'd like to look at. You can list as many files as you would like and it will run on each file. For example:
>py scripts/contributions/[FILE_NAME].py -f [REPLAY_FILE].replay [REPLAY_FILE].replay [REPLAY_FILE].replay

You can also specify how many replays back you would like to run (by date) using the -n parameter. Example:
>py scripts/contributions/[FILE_NAME].py -n 3
would run the last 3 games you ran

----------------------------------------------------------------------------------------

You can output the averages for health, bits, and cores for a single match by using the following:
>py scripts/contributions/[FILE_NAME].py -avg health
The only (currently) accepted parameters for -avg are:
	- health
	- bits
	- cores
You can include 1, 2, or all 3 in your output. For example:
>py scripts/contributions/[FILE_NAME].py -avg health bits cores

----------------------------------------------------------------------------------------

Lastly, if you install matplotlib you can graph (currently) health, bits, and cores for individual matches.

Simply do:
>py scripts/contributions/[FILE_NAME].py -g [PARAMETERS]
Where PARAMETERS can be health, bits, or cores (you can do 2, or all 3 as well on one graph)

For example:
>py scripts/contributions/[FILE_NAME].py -g health


All of the commands above can be combined in any order and way. For example, if I wanted to run the last 2 replay files and only output the average heath and graph the number of bits, I would run:
>py scripts/contributions/[FILE_NAME].py -n 2 -avg health -g bits

If you forget you can also see the possible commands by:
>py scripts/contributions/[FILE_NAME].py -h

----------------------------------------------------------------------------------------

There are essentially 2 decision paths possible, whether you are looking at 1 replay or many.
If you are looking at 1, it prints out information for that replay.
The moment you add more (through any arg) it then prints a summary for those replays.
You can force the program to print information for each individual replay by using the -v flag.

For example:
>py scripts/contributions/[FILE_NAME].py -a -v -g health wins

Will display and graph (health) for each individual replay, as well as display the summary
information and graph the number of wins for each algo.

In contrast:
>py scripts/contributions/[FILE_NAME].py -a -g health wins

Will only display a summary and show the graph for wins (health graph parameter is simply
ignored).


I plan on adding more to this file, specifically the ability to graph much more
data and get more broad statistics.

If you have any suggestions/questions let me know :) - @Isaac

'''

pltInstalled = False

try:
	import os
	import sys
	import json
	import glob
	import argparse
except ImportError as e:
	sys.stderr.write("WARNING: Module not found, full error:\n\n")
	sys.stderr.write(e)

try:
	import matplotlib.pyplot as plt
	pltInstalled = True
except ImportError:
	pass

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
		help="will force the program to run each replay seperately and print detailed information\n\n")
	ap.add_argument(
		"-avg", "--averages",
		nargs="*",
		default=[],
		help="data you would like the average of (not very useful right now)\nValid Options:\n\t- health\n\t- bits\n\t- cores\n\n")
	ap.add_argument(
		"-f", "--file",
		nargs="*",
		default=[],
		help="specify a replay file (or multiple) you'd like to analyze\n\n")
	ap.add_argument(
		"-g", "--graph",
		nargs="*",
		default=[],
		help="specify what data you would like to be graphed - you must have matplotlib installed\nValid Options:\n\t- health\n\t- bits\n\t- cores\n\t- wins (for multiple replays)\n\n")
	return vars(ap.parse_args())


# Stores data pertaining to an individual Algo
class Algo:
	def __init__(self, name):
		self.name = name
		self.wins = 0
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

	def addData(self, replay, turn, arg, data):
		if replay in self.replays:
			if turn in self.replays[replay]:
				pass
			else:
				self.replays[replay][turn] = {}
		else:
			self.replays[replay] = {}
			self.replays[replay][turn] = {}

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

	def addPlot(self, options, replay):
		avalible = ['health', 'bits', 'cores']
		disp = False
		for lbl in options:
			if lbl in avalible:
				disp = True
				data = [self.replays[replay][turn][lbl] for turn in self.replays[replay] if turn != 'endStats']
				plt.plot(data, label='{}\'s {}'.format(self, lbl))

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

	def unpackData(self, algos):
		try:
			self.algo1, self.algo2 = self.createAlgos(algos)

			for t, f in self.getValidTurns():
				turn = self.getTurn(t, f)

				turnInfo = turn['turnInfo']
				p1Stats = turn['p1Stats']
				p2Stats = turn['p2Stats']

				self.algo1.addData(self.fname, t, 'health', p1Stats[0])
				self.algo1.addData(self.fname, t, 'cores', p1Stats[1])
				self.algo1.addData(self.fname, t, 'bits', p1Stats[2])

				self.algo2.addData(self.fname, t, 'health', p2Stats[0])
				self.algo2.addData(self.fname, t, 'cores', p2Stats[1])
				self.algo2.addData(self.fname, t, 'bits', p2Stats[2])

			self.algo1.recordFinalData(self.fname, self.algo2)
			self.algo2.recordFinalData(self.fname, self.algo1)
			self.algo1.addEndStats(self.fname, self.turns[self.validTurns[-1]]['endStats']['player1'])
			self.algo2.addEndStats(self.fname, self.turns[self.validTurns[-1]]['endStats']['player2'])
		except Exception as e:
			print (e)

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

	def addPlot(self, options):
		if 'wins' in options:
			wins = []
			lbls = []

			for algo in self.algos:
				wins.append(algo.wins)
				lbls.append(algo.name)

			y_pos = range(len(self.algos))
			y_ticks = range(max(wins)+2)
			while len(y_ticks) > 20:
				y_ticks = [x for x in y_ticks if x % 2 == 0]

			plt.bar(y_pos, wins, align='center', width=0.65)
			plt.xticks(y_pos, lbls, rotation=60)
			plt.yticks(y_ticks)
			plt.ylabel('# of Wins')
			plt.title('Number of Wins per Algo')
			plt.tight_layout()


# displays detailed data for every replay stored in the fileManager fh.
def run_every_replay_verbose(fh, graphingEnabled, options):
	for replay in fh.getReplays():
		sys.stderr.write('{:->90}\n'.format(''))
		sys.stderr.write('Showing {}\n'.format(replay.fname.replace('replays/', '')))
		sys.stderr.write('{:->90}\n'.format(''))

		disp = False

		try:
			for algo in replay.getAlgos():
				algo.dispData(options, replay.fname)

				if graphingEnabled:
					if algo.addPlot(options['graph'], replay.fname):
						disp = True
		except Exception as e:
			sys.stderr.write('Error parsing file\n')
			sys.stderr.write(str(e)+'\n')


		if graphingEnabled:
			plt.ylabel('Value')
			plt.xlabel('Turn #')
			plt.legend(loc='best')
			plt.tight_layout()

			if disp:
				plt.show()
			else:
				plt.clf()

		sys.stderr.write('\n')

# displayed aggregate data over many matches and replay files
def run_every_replay_agg(fh, graphingEnabled, options):
	sys.stderr.write('{:->90}\n'.format(''))
	sys.stderr.write('Summary of {} matches:\n'.format(len(fh.getReplays())))
	sys.stderr.write('{:->90}\n'.format(''))
	sys.stderr.write(fh.getAlgoWinSummary())

	if graphingEnabled:
		fh.addPlot(options)
		plt.show()


def main(args):
	fh = FileHandler()
	fh.loadFiles(int(args['num']), args['all'], args['file']) #loads the files - all JSON reading is here

	# check to see if matplotlib is installed
	graphingEnabled = True if len(args['graph']) > 0 else False
	if graphingEnabled and not pltInstalled:
		sys.stderr.write("WARNING: matplotlib not installed - no graphs will be shown\n\n")
		graphingEnabled = False

	# these options are passed to let the algo know what to display and add to the plots
	options = {
				'avg':		args['averages'],
				'endStats':	None,
				'graph':	args['graph']
			  }

	# checks the arguments to see what inforation should be displayed
	if args['all']:
		run_every_replay_verbose(fh, graphingEnabled, options) if args['verbose'] else ''
		run_every_replay_agg(fh, graphingEnabled, options['graph'])
	elif int(args['num']) == 1:
		run_every_replay_verbose(fh, graphingEnabled, options)
	elif int(args['num']) > 1 or len(args['file']) > 0:
		run_every_replay_verbose(fh, graphingEnabled, options) if args['verbose'] else ''
		run_every_replay_agg(fh, graphingEnabled, options['graph'])

	sys.stderr.write('\n\n')


if __name__ == '__main__':
	args = ParseArgs() # get command line arguments
	main(args)
