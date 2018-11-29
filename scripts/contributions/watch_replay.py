#!/usr/bin/env python

'''
------------------------------------------------------------------------------------------------
Author: @Isaac
Last Updated: 14 Nov 2018
Contact: Message @Isaac at https://forum.c1games.com/
Copyright: CC0 - completely open to edit, share, etc

Short Description: 
This is a python script to visualize replay files in a similar format to the online version.
You can also run games and watch them as they play (this is slow).
Lastly, it allows you to save these visualizations in video format.
------------------------------------------------------------------------------------------------

README:

This program assumes this file is in the contributions/scripts directory

This script takes an input of a replay file and displays it visually.
Alternatively, it can run a match and you can visualize it as the game engine runs.

There are a variety of ways you can tell it how to run; I will give an example of each.

The default is (runs latest replay):
>py scripts/contributions/watch_replay.py

----------------------------------------------------------------------------------------
-f: Run a specific replay file

You can specify which file you would like to run by:
>py scripts/contributions/watch_replay.py -f [REPLAY_FILE].replay

where REPLAY_FILE is the file you'd like to look at. You can list more than one, but it will
NOT display more than one replay.

----------------------------------------------------------------------------------------
-b: Blitting

You can specify whether to use blitting with this flag:
>py scripts/contributions/watch_replay.py -b

Blitting will improve the performance of the graphing, but comes at the cost of several features:
- You will not be able to use or see the slider
- You may notice small graphical glitches with text updating (will not show if you do not use the keyboard inputs)
- If you run the program in real-time the player names will not update (the winner name will be displayed correctly).

----------------------------------------------------------------------------------------
-run: Real-time watching

This means you will run and watch a game in real time.
The program will start a match like you normally would, but will also open the visualizer when possible.

You can specify the algos you would like to run like normal:
>py scripts/contributions/watch_replay.py -run algos/my-bot1 algos/my-bot2

You cannot save a game if you watch it in real-time.
The slider will not appear until the game has completed (you can still use the keyboard commands).
If you use blitting, the player names will not update.

----------------------------------------------------------------------------------------
-s: Save

You can specify if you would like to save the replay.
This saves a direct copy of what you would see if you ran the program normally.

You must specify the name the file should be saved as. For example:
>py scripts/contributions/watch_replay.py -s awesome_video

This may take a while and seem to hang, but it has to go through the entire replay as if you were watching it.

There are three possible file formats to save the replay in: .mp4, .gif, .html
Two of these formats (.mp4, .gif) have dependencies outside of this script.
This script will automatically detect the type of encoder (writer) depending on the extension you give unless
you specify otherwise.

.mp4:
>py scripts/contributions/watch_replay.py -s awesome_video.mp4

This will run the script and save the replay in .mp4 format, but require the installation of 3rd party software, ffmpeg.
This runs on ffmpeg, which can be downloaded here: https://www.ffmpeg.org/download.html

As long as you have ffmpeg installed and in your PATH, this format should work.
This script will let you know if it cannot use it.


.gif:
>py scripts/contributions/watch_replay.py -s awesome_video.gif

This will run the script and save the replay in .gif format, but requires the python module Pillow.
If you ask for a .gif file this program will ask if you want to install Pillow.


.html:
>py scripts/contributions/watch_replay.py -s awesome_video.html

This one is pretty cool, it will generate a folder (awesome_video_frames) with every single frame
stored as an image and then generate an html file to view the files in video format.

If you want the individual frames, use this option.
This option also does not have any dependencies (as far as I know).


There are two arguments specific to -s that you can use to specify more with the save option

-------------
-w: Writers

This specifies the writer to use (which results in the output file format).
You can specify more than one, and it will create a save for each of the parameters you provide.

For example (these are the same):
>py scripts/contributions/watch_replay.py -s awesome_video -w pillow
>py scripts/contributions/watch_replay.py -s awesome_video.gif

But if you wanted to also save it as a .mp4:
>py scripts/contributions/watch_replay.py -s awesome_video -w pillow ffmpeg

Valid inputs for this are:
	Writer | File Type

	ffmpeg | .mp4
	pillow | .gif
	html   | .html

You can still supply an extension name when you do this, but it will be overwritten (you will be notified):
For example:
>py scripts/contributions/watch_replay.py -s awesome_video.mp4 -w pillow ffmpeg

would output (assuming dependencies installed):
>This may take a little while and seem to hang
>
>You used extension .mp4, but .gif is the valid type for pillow. Using .gif:
>Saving file awesome_video.gif
>Done saving file: awesome_video.gif
>
>Saving file awesome_video.mp4
>Done saving file: awesome_video.mp4

-------------
-kt: Keep Trying

This flag changes the behavior of the script if a dependency fails when saving.

By default, if ffmpeg is not accessible the program simply skips it.
However, if you add the -kt flag it will continue to try the other avalible options.

For example, assuming ffmpeg is not installed:
>py scripts/contributions/watch_replay.py -s awesome_video.mp4

output:
>This may take a little while and seem to hang
>
>ffmpeg not installed or in PATH, skipping

But with -kt:
>py scripts/contributions/watch_replay.py -s awesome_video.mp4 -kt

output:
>This may take a little while and seem to hang
>
>ffmpeg not installed or in PATH, skipping
>
>You used extension .mp4, but .gif is the valid type for pillow. Using .gif:
>Saving file awesome_video.gif
>Done saving file: awesome_video.gif

The default priority order for checking next is ffmpeg, then pillow, and html last.
If you want to change the order just:
1. Ctrl-Find in this script:	this is the default order of priority for running a save
2. Change the order of the list to be the priority you want

----------------------------------------------------------------------------------------

I cannot stress enough that this program is slow and unoptimized. Expect slowness :).
I have included the same speeds on the normal visualizer in case people have better machines
than me, but it doesn't appear to do much past a point.

A much faster way of viewing replays (other than skipping) is using the fast-fwd option
(holding down Ctrl). This is something I did not program; I believe (100% guessing) that
matplotlib skips frames resulting in the speed-up, which is great :).

If you have suggestions on improving speeds please let me know.
Please forgive the ugliness as this is my first large project with matplotlib - suggestions are loved and appreciated :).

If you have any questions just ask me on the forums - @Isaac
'''

try:
	import os
	import sys
	import time
	import json
	import glob
	import random
	import warnings
	import argparse
	import subprocess
	import multiprocessing as mp
except ImportError as e:
	sys.stderr.write("WARNING: Module not found, full error:\n\n")
	sys.stderr.write(e)

try:
	import matplotlib.pyplot as plt
	import matplotlib.animation as animation
	from matplotlib.patches import Circle, Wedge, Polygon
	from matplotlib.collections import PatchCollection
	from matplotlib.widgets import Slider
except ImportError:
	usr_in = input('Matplotlib not found.\nWould you like this program to try and install matplotlib? (y/n) ')
	if usr_in.lower() == 'y' or usr_in.lower() == 'yes':
		subprocess.run(['python', '-m', 'pip', 'install', 'matplotlib'])

		try:
			import matplotlib.pyplot as plt
			import matplotlib.animation as animation
			from matplotlib.patches import Circle, Wedge, Polygon
			from matplotlib.collections import PatchCollection
			from matplotlib.widgets import Slider

			sys.stderr.write('\n\n')
		except ImportError as e:
			sys.stderr.write('\n\n{}\n\n'.format(str(e)))
			sys.stderr.write('Failed: Check to make sure you have all core dependencies installed (usually TkAgg).\n\n')
			sys.exit()


global FILTER, ENCRYPTOR, DESTRUCTOR, PING, EMP, SCRAMBLER, MAX_HP, GET_VERTS, SPEED, BLIT
FILTER = 0
ENCRYPTOR = 1
DESTRUCTOR = 2
PING = 3
EMP = 4
SCRAMBLER = 5
MAX_HP = {FILTER:60, ENCRYPTOR:30, DESTRUCTOR:75, PING:15, EMP:5, SCRAMBLER:40}
SPEED = {'1':.25, '2':.5, '3':1, '4':2, '5':4, '6':8} # speed versions, key is user input (number)


# returns a rotated angle (created to make health deplete from vertical angle)
def rotate(angle, theta=90):
	return angle + theta

# returns the vertice points around a center point x,y for a ping
def ping_verts(x, y):
	p1 = 0
	p2 = .2
	p3 = .06
	verts = [(-p2,p1),(-p3,p3),(p1,p2),(p3,p3),(p2,p1),(p3,-p3),(p1,-p2),(-p3,-p3)]
	return [(a+x, b+y) for (a,b) in verts]

# returns the vertice points around a center point x,y for an emp
def emp_verts(x,y):
	p1 = 0
	p2 = .5
	p3 = .12
	verts = [(-p3,p1),(-p2,p2),(p1,p3),(p2,p2),(p3,p1),(p2,-p2),(p1,-p3),(-p2,-p2)]
	return [(a+x, b+y) for (a,b) in verts]

# returns the vertice points around a center point x,y for a scambler
def scrambler_verts(x,y):
	p1 = 0
	p2 = .35
	p3 = .25
	verts = [(-p3,p1),(-p2,p2),(p1,p3),(p2,p2),(p3,p1),(p2,-p2),(p1,-p3),(-p2,-p2)]
	return [(a+x, b+y) for (a,b) in verts]

GET_VERTS = {PING:ping_verts, EMP:emp_verts, SCRAMBLER:scrambler_verts}


# handles all the arguments
def parse_args():
	ap = argparse.ArgumentParser(add_help=False, formatter_class=argparse.RawTextHelpFormatter)
	ap.add_argument('-h', '--help', action='help', help='show this help message and exit\n\n')
	ap.add_argument(
		'-f', '--file',
		nargs='*',
		default=[],
		help="specify a replay file you'd like to watch\n\n")
	ap.add_argument(
		'-b', '--blit',
		action='store_true',
		help="will tell the program to use blit - will improve performance, but you will not be able to see or use the slider and there will be minor text glitches when fast forwarding, etc (you can still use all the keyboard commands)\n\n")
	ap.add_argument(
		'-run', '--run_match',
		nargs='+',
		default=['empty'],
		help="specify whether to watch a replay in real-time (runs a match) - you supply algo names as arguments just like when normally running a match\n\n")
	ap.add_argument(
		'-s', '--save',
		default='',
		help="specify whether to save replay as an .mp4 file - you must supply a file name (it may take a little while)\n\n")
	ap.add_argument(
		'-w', '--writers',
		nargs='+',
		default=['empty'],
		help="specify the type of writer(s) to use (video save format) - flag only works if you are saving a replay\n\nValid Options:\n\t- ffmpeg\n\t- pillow\n\t- html\n\n")
	ap.add_argument(
		'-kt', '--keep_trying',
		action='store_true',
		help="forces the save file to keep trying different writers until one works - flag only works if you are saving a replay\n\n")
	return vars(ap.parse_args())

# stores all information for a single unit on the graph
class Unit:
	def __init__(self, t, x, y, hp, p, ID, count, ax):
		self.x = x 										# x position on the graph
		self.y = y 										# y position on the graph
		self.unit_type = t 								# the type of unit (a constant declare in global)
		self.stability = hp 							# stability of unit
		self.p_index = p 								# player index
		self.ID = ID 									# unique id for unit (from engine.java)
		self.owner = True if p == 1 else False			# boolean to keep track of owner
		self.polygons = []								# all polygons that make up that unit
		self.patches = []								# these are what get drawn to the animation (contain polygons themselves)
		self.color = {True:'C0', False:'r'}				# constants for player color

		self.create_patches(count, ax)					# adds patches to the graph based on type
		self.set_color()								# sets the color and alpha based on type and health

	# equality is determined by ID
	def __eq__(self, other):
		if type(other) == str: return self.ID == other
		return self.ID == other.ID

	def __repr__(self):
		return "'{}'".format(self.ID)

	# creates and adds all units to the graph
	def create_patches(self, count, ax):
		if self.unit_type == FILTER:
			wedge = Wedge((self.x,self.y), .2, rotate(0), rotate(360), width=0.07)

			self.polygons.append(wedge)
			self.patches.append(ax.add_patch(wedge))
			self.set_wedge_shape()

		elif self.unit_type == ENCRYPTOR:
			inner_wedge = Wedge((self.x,self.y), .12, rotate(0), rotate(360), width=0.03)
			outer_wedge = Wedge((self.x,self.y), .37, rotate(0), rotate(360), width=0.15)

			self.polygons.append(inner_wedge)
			self.polygons.append(outer_wedge)
			self.patches.append(ax.add_patch(inner_wedge))
			self.patches.append(ax.add_patch(outer_wedge))
			self.set_wedge_shape()

		elif self.unit_type == DESTRUCTOR:
			inner_wedge = Wedge((self.x,self.y), .2, rotate(0), rotate(360), width=0.07)
			outer_wedge = Wedge((self.x,self.y), .45, rotate(0), rotate(360), width=0.01)

			self.polygons.append(inner_wedge)
			self.polygons.append(outer_wedge)
			self.patches.append(ax.add_patch(inner_wedge))
			self.patches.append(ax.add_patch(outer_wedge))
			self.set_wedge_shape()

		elif self.unit_type == PING or \
			 self.unit_type == EMP or \
			 self.unit_type == SCRAMBLER:
				verts = GET_VERTS[self.unit_type](self.x, self.y)
				polygon = Polygon(verts, True)

				self.polygons.append(polygon)
				self.patches.append(ax.add_patch(polygon))
				self.check_stability(count, ax)

	# returns a radius based upon the stability and max stability of a mobile unit
	def hp_to_r(self, stability):
		return min((stability - MAX_HP[self.unit_type])/50, .5)

	# returns an angle based upon the stability and max stability of a static unit
	def hp_to_angle(self, stability):
		return int(rotate(360 * (stability / MAX_HP[self.unit_type])))

	# sets the wedge angle based upon a static unit's stability
	def set_wedge_shape(self):
		angle = self.hp_to_angle(self.stability)
		for patch in self.patches:
			patch.set_theta2(angle)

	# sets the postition of a unit on the graph
	def set_pos(self, x, y):
		self.x = x
		self.y = y
		for patch in self.patches:
			if type(patch) == Polygon: patch.set_xy([(x, y) for (x,y) in GET_VERTS[self.unit_type](x, y)])
			elif type(patch) == Circle: patch.center = x, y

	# sets the color of a unit based on type
	def set_color(self):
		for patch in self.patches:
			patch.set_color(self.color[self.owner])
			patch.set_antialiased(True)

			if self.unit_type == EMP or \
			   self.unit_type == SCRAMBLER:
				patch.set_fill(False)

		if self.unit_type == ENCRYPTOR:
			self.patches[1].set_alpha(0.3)

		if self.stability > MAX_HP[self.unit_type]:
			self.patches[1].set_fill(False)
			self.patches[1].set_alpha(0.5)

	# checks the stability and if greater than max for a mobile unit adds a new Circle
	def check_stability(self, count, ax):
		if self.stability > MAX_HP[self.unit_type]:
			if len(self.patches) == 1:
				extra_wedge = Circle((self.x,self.y), self.hp_to_r(self.stability), linewidth=4)
				self.patches.append(ax.add_patch(extra_wedge))
				self.polygons.append(extra_wedge)
			else:
				self.patches[1].set_radius(self.hp_to_r(self.stability))

			if count != 1:
				self.patches[1].set_visible(False)
		else:
			if len(self.patches) > 1:
				self.polygons[1].set_visible(False)

	# updates all the values of a unit (count is necessary otherwise alpha is messed up)
	def update(self, x, y, stability, p_index, ID, count, ax):
		self.stability = stability

		if self.unit_type == FILTER or \
		   self.unit_type == ENCRYPTOR or \
		   self.unit_type == DESTRUCTOR:
			self.set_wedge_shape()

		elif self.unit_type == PING or \
			 self.unit_type == EMP or \
			 self.unit_type == SCRAMBLER:
				self.set_pos(x,y)
				self.check_stability(count, ax)

		self.set_color()

	# removes the unit from the graph
	def remove(self):
		for polygon in self.polygons:
			polygon.remove()


# holds all units (patches) and handles their creation/destruction on the board
class PatchWrapper:
	def __init__(self):
		self.units = {}		# stores every unit currently on the board with each ID as the key
		self.loc = {}		# stores the number of units at a location with each location tuple (x,y) as the key
		self.lbls = []		# stores the text labels if a location has more than 1 unit

	# creates a unit and stores it in self.units
	def create_unit(self, unit_type, pos, stability, p_index, ID, count, ax):
		x,y = pos
		self.units[ID] = Unit(unit_type, x, y, stability, p_index, ID, count, ax)

	# removes a unit by ID from both the board and self.units
	def remove_unit(self, ID):
		for key, val in self.units.items():
			if val == ID:
				self.units[ID].remove()
				self.units.pop(ID, None)
				break

	# clears the entire board - not used anymore (very inefficient mode of updating)
	def clear_board(self):
		self.loc = {}

		for ID in self.units:
			self.units[ID].remove()
		
		self.units = {}
		self.remove_lbls()

	# removes all number labels from the board and from self.lbls
	def remove_lbls(self):
		for lbl in self.lbls:
			lbl.remove()
		self.lbls = []

	# removes all previous labels and creates new ones at locations with more than one unit, then resets self.loc
	def update_lbls(self, ax):
		self.remove_lbls()
		for pos, val in self.loc.items():
			if val > 1:
				self.plot_text(val, pos, ax)
		self.loc = {}

	# updates all units
	def update_units(self, units, ax):
		ids = [u[4] for u in units]

		# get all units that are no longer on the board
		# (you cannot use the engines remove since using the slider does not remove them)
		remove = []
		for unit in self.units.values():
			if unit not in ids:
				remove.append(unit.ID)

		# remove all the units (cannot do it from the above loop - RuntimeError)
		for ID in remove:
			self.remove_unit(ID)

		# loop through all the units given by the engine
		for unit_raw in units:
			unit_type, (x, y), stability, p_index, ID = unit_raw

			# update the board locations count of units
			try:
				self.loc[(x,y)] += 1
			except KeyError:
				self.loc[(x,y)] = 1

			# if a unit already exists, update it. If not, create it
			try:
				self.units[ID].update(x, y, stability, p_index, ID, self.loc[(x,y)], ax)
			except KeyError:
				self.create_unit(unit_type, (x,y), stability, p_index, ID, self.loc[(x,y)], ax)


	# adds the count lable to a position on the board
	def plot_text(self, txt, pos, ax):
		x,y = pos
		self.lbls.append(ax.text(x+.4, y-.4, str(txt), fontsize=10))

	# return all the patches that need to be updated every animation
	def values(self):
		return [patch for unit in self.units.values() for patch in unit.patches]


# this class is for the right side (information side) except for the plot (see Plot class)
class Info:
	def __init__(self, endStats, ax, slider_exists=False):
		self.lbls = []											# holds every text object that needs to be updated
		self.color = {True:'C0', False:'r', 1:'C0', 2:'r'}		# color reference based on player index
		self.ax = ax 											# reference to the right plt axes

		# if in runtime mode, endStats don't exist, so we don't know a winner yet
		if endStats != None:
			self.winner = endStats['winner']
			self.winner_name = endStats['player1']['name'] if self.winner == 1 else endStats['player2']['name']

		# posisition references to make moving around easier
		y_init = .95
		offset = .05
		list_pos = [y_init - ((x+1)*offset) for x in range(4)]
		self.y_pos = {	'health'	: 	list_pos[0],
						'cores'		:	list_pos[1],
						'bits'		:	list_pos[2],
						'time'		:	list_pos[3],
						1			:	y_init,
						2			:	y_init
					 }

		self.x_pos = {	1			:	.06,
						2			:	.506,
					 }

		self.hide_graph()						# remove everything from the ax
		self.disp_reference(slider_exists)		# display the keyboard reference
		self.disp_static(endStats)				# display text that won't change

	# adds a data value to the information page (health, cores, etc)
	def add_data(self, d_dype, p_index, data, fontsize=14):
		self.lbls.append(self.ax.text(self.x_pos[p_index]+.15, self.y_pos[d_dype], str(data), fontsize=fontsize, verticalalignment='bottom', horizontalalignment='left'))

	# clear all dynamic text
	def clear_info(self):
		for lbl in self.lbls:
			lbl.remove()

		self.lbls = []

	# display all text that won't change
	def disp_static(self, endStats):
		# if endStats don't exist use default values, otherwise use endStates for names
		if endStats != None:
			self.ax.text(self.x_pos[1], self.y_pos[1], endStats['player1']['name'], fontsize=18, verticalalignment='bottom', horizontalalignment='left', color=self.color[1])
			self.ax.text(self.x_pos[2], self.y_pos[2], endStats['player2']['name'], fontsize=18, verticalalignment='bottom', horizontalalignment='left', color=self.color[2])
		else:
			self.ax.text(self.x_pos[1], self.y_pos[1], 'player1', fontsize=18, verticalalignment='bottom', horizontalalignment='left', color=self.color[1])
			self.ax.text(self.x_pos[2], self.y_pos[2], 'player2', fontsize=18, verticalalignment='bottom', horizontalalignment='left', color=self.color[2])

		# add all data labels (health, bits, cores, etc)
		for lbl, pos in self.y_pos.items():
			if type(lbl) == str:
				self.ax.text(self.x_pos[1], self.y_pos[lbl], '{}:'.format(lbl), fontsize=14, verticalalignment='bottom', horizontalalignment='left')
				self.ax.text(self.x_pos[2], self.y_pos[lbl], '{}:'.format(lbl), fontsize=14, verticalalignment='bottom', horizontalalignment='left')

	# removes the axis from the ax
	def hide_graph(self):
		self.ax.axis('off')

	# display the keyboard reference
	def disp_reference(self, slider_exists):
		self.ax.text(.5, .215, 'Keyboard Commands:', fontsize=13, verticalalignment='bottom', horizontalalignment='center')
		self.ax.text(0.2, .075, '\nSpace/Enter:\nArrow Keys:\nCtrl+Arrow Keys:\n<,> and numbers 1-6:\nHold Ctrl', fontsize=12, verticalalignment='bottom', horizontalalignment='left')
		self.ax.text(.8, .075, 'Pause and Play\nNext/Previous Frame\nNext/Previous Turn\nChange Speed\nFast-Fwd', fontsize=12, verticalalignment='bottom', horizontalalignment='right')

		# if the slider doesn't exist, don't show the prompt for it
		if not BLIT and slider_exists:
			self.ax.text(.5, .03, 'You can also scrub the turn slider with your mouse', fontsize=12, verticalalignment='bottom', horizontalalignment='center')

	# remove previous information and add all new data
	def update(self, p1Stats, p2Stats):
		self.clear_info()

		self.add_data('health', 1, int(p1Stats[0]))
		self.add_data('cores', 1, p1Stats[1])
		self.add_data('bits', 1, p1Stats[2])
		self.add_data('time', 1, p1Stats[3])

		self.add_data('health', 2, int(p2Stats[0]))
		self.add_data('cores', 2, p2Stats[1])
		self.add_data('bits', 2, p2Stats[2])
		self.add_data('time', 2, p2Stats[3])

	# if the end of game is reached, show the winner
	def show_winner(self):
		try:
			self.lbls.append(self.ax.text(.5, .67, '{} wins!'.format(self.winner_name), color=self.color[self.winner], verticalalignment='bottom', horizontalalignment='center', fontsize=24))
		except TypeError:
			print ('tried and failed to show winner - no endStats')


# this contains all data for the health plot on the right side
class Plot:
	def __init__(self, data, ax, frame=0):
		ax.clear() 													# clear the plot

		self.ax = ax 												# reference to the ax containing the plot
		self.data = data 											# all known health data, tuple containing two lists, player1 and player2 healths
		self.lines = []												# the lines of the plot

		self.ax.set_ylabel('Health')								# set the y_axis label
		self.ax.set_xlabel('Frame')									# set the x_axis label
		line, = self.ax.plot(self.data[0][:0], color='C0')			# create and get a line reference from the plot
		self.lines.append(line)
		line, = self.ax.plot(self.data[1][:0], color='r')			# create and get a line reference from the plot
		self.lines.append(line)
		self.ax.set_yticks(list(range(0, 36, 5)))					# set the y_labels and scale

		self.lines[0].set_xdata(list(range(0, 100)))				# set the x_range for the line to always be 100
		self.lines[1].set_xdata(list(range(0, 100)))				# set the x_range for the line to always be 100

		self.ax.set_xlim(0, 100)									# set the x_range for the plot to always be 100

		self.update(frame)											# update the plot

	# sets the lines for the plot based upone the current frame
	def update(self, frame, data=None):

		# handles initial values
		frame = int(frame) if frame > 0 else 0
		frames = frame if frame > 100 else 100
		x_0 = frame - 100 if frame > 100 else 0

		nulls = [None for x in range(100 - frame)]					# extra values for beginning, size must match

		# if we specify data, use that, otherwise use the cached values.
		# this is used if running in real-time and not all data is known
		if data == None:
			line1 = nulls + self.data[0][x_0:frame]
			line2 = nulls + self.data[1][x_0:frame]
		else:
			self.data = data
			line1 = nulls + self.data[0][x_0:frame]
			line2 = nulls + self.data[1][x_0:frame]

		self.ax.set_xticklabels(list(range(x_0, frames+1, 20)))		# updates the x_labels

		self.lines[0].set_ydata(line1)								# set the data for line1
		self.lines[1].set_ydata(line2)								# set the data for line2


# this class contains all information regarding the entire window
class Graph:
	def __init__(self, data, frames_in_turn, healths, writers, keep_trying, save='', fh=None):

		# pretty clear, if no data, raise an Error
		if len(data) < 1:
			raise RuntimeError('no data')

		self.fh = fh 																# reference to file handler
		self.real_time = False if self.fh == None else True 						# tracks whether real-time

		plt.style.use('dark_background')											# sets black background

		plt.rcParams["figure.figsize"] = (16,8)										# resizes the window
		self.fig, ax = plt.subplots(nrows=1, ncols=2)								# splits the plot into two halves and gets the references
		self.board_ax, self.info_ax = ax 											# assign left and right side references
		self.plot_ax = self.fig.add_subplot(324)									# add the plot and assing it's reference

		self.general_init(data, frames_in_turn, healths)							# handles general initialization (called again if in real-time)

		self.head = (0,-1)															# tracks the current turn, frame pair
		self.end_of_game = False													# end of game flag
		self.is_manual = False														# stores whether the user is manually moving the slider, keyboard, etc
		self.single_advance = False													# true when user is scrubbing, but still want to move forward one frame
		self.stop_slider_evt = False												# stop the slider event from triggereing when the code changes it

		self.patches = PatchWrapper()												# creates the PatchWrapper object

		self.stream = self.data_stream()											# gets a data_reference - this passes all data to the animation

		self.setup_board()															# initialize static parts of the board

		self.fig.canvas.mpl_connect('key_press_event', self.keyboard_input)			# connect keyboard events to the keyboard_input function

		# if in real-time, use a generator function to update number of frames, otherwise frames is static
		if not self.real_time:
			self.anim = animation.FuncAnimation(self.fig, self.update, init_func=self.init, frames=self.num_frames, interval=100, blit=BLIT, repeat=False)
		else:
			self.frame_generator = self.gen_frames()
			self.anim = animation.FuncAnimation(self.fig, self.update, init_func=self.init, frames=self.frame_generator, interval=100, blit=BLIT, repeat=False)

		self.change_play_speed('3')													# initialize the playback speed ('3' is default)

		# if you don't save, show the plot. Otherwise save the animation (nothing is shown)
		if save == '':
			self.show()
		else:
			self.save_animation(save, writers, keep_trying)

	# saves all animations passed from the command line
	def save_animation(self, save_name, writers, keep_trying):
		print ('This may take a little while and seem to hang')

		# reference dictionaries to converte values based on input
		ex_to_writer = {'gif':'pillow', 'mp4':'ffmpeg', 'html':'html'}
		check_writer = {'ffmpeg':self.check_ffmpeg, 'pillow':self.check_pillow, 'html':lambda:True}

		# seperate the file name from the extension
		try: name, given_ext = save_name.split('.')
		except ValueError: name, given_ext = save_name, ''

		default = ['ffmpeg', 'pillow', 'html']		# this is the default order of priority for running a save

		# when this block finishes, attempts is a list of possible attempts in order of priority
		attempts = [ex_to_writer[given_ext]] if given_ext != '' and given_ext in ex_to_writer.keys() else default
		attempts = attempts if 'empty' in writers else writers
		attempts = attempts + [w for w in default if w not in attempts] if keep_trying else attempts

		# loop through and save all attempts until input is complete
		complete = 0
		for i, writer in enumerate(attempts):
			try:
				# if we can create that type of writer, make it
				print ()
				if check_writer[writer]():
					self.create_animation(writer, name, given_ext)
					complete += 1

				# check and make sure we haven't finished (based on whether we keep trying or not)
				if len(writers) <= complete: keep_trying = False
				else: keep_trying = True

				if not keep_trying: break
			except KeyError:
				print ('{} is not a valid writer. Options are:\n\t- ffmpeg  (for .mp4 videos)\n\t- pillow  (for gifs)\n\t- html    (for browser view and individual frames)'.format(writer))

	# creates an animation of a writer type
	def create_animation(self, writer, name, given_ext):
		extension = self.get_extension(writer, given_ext)
		print ('Saving file {}.{}'.format(name, extension))
		try:
			self.anim.save('{}.{}'.format(name, extension), writer=writer)
			print ('Done saving file: {}.{}'.format(name, extension))
		except Exception as e:
			print ('Unknown error. Full Output:')
			print (str(e))

	# returns the extension that must be used for the appropriate writer
	def get_extension(self, writer, given_ext):
		extensions = {'pillow':'gif', 'ffmpeg':'mp4', 'html':'html'}
		if given_ext != extensions[writer] and given_ext != '':
			print ('You used extension .{0}, but .{2} is the valid type for {1}. Using .{2}:'.format(given_ext, writer, extensions[writer]))

		return extensions[writer]

	# confirms whether ffmpeg is avaliable as a writer
	def check_ffmpeg(self):
		ffmpeg_process = subprocess.Popen('ffmpeg', shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
		_,err = ffmpeg_process.communicate()
		err = str(err).replace("b'",'').replace('b"','').replace('"','').replace("'",'').replace('\\n','').replace('\\r','').replace('\\','').replace('"','')

		# covers both Ubuntu and Windows users (fingers-crossed)
		# if anyone knows a better way to check for ffmpeg let me know, or add it here :)
		if err == 'ffmpeg is not recognized as an internal or external command,operable program or batch file.':
			print ('ffmpeg not installed or in PATH, skipping')
			return False
		elif err.find('Command ffmpeg not found') != -1:
			print ('ffmpeg not installed or in PATH, skipping')
			return False
		return True

	# confirms whether pillow is avaliable as a writer and offers to import it if not
	def check_pillow(self):
		try:
			import PIL
			return True
		except ImportError:
			usr_in = input('Pillow not found.\nWould you like this program to try and install Pillow? (y/n) ')
			if usr_in.lower() == 'y' or usr_in.lower() == 'yes':
				subprocess.run(['python', '-m', 'pip', 'install', 'Pillow'])

				try:
					import PIL
					print ()
					return True
				except ImportError as e:
					sys.stderr.write('\n\n{}\n\n'.format(str(e)))
					sys.stderr.write('Failed to import Pillow.\n\n')
					return False
			return False

	# extension of __init__(), called every frame when real-time
	def general_init(self, data, frames_in_turn, healths):
		self.data = data 													# dict with keys of (turn, frame) tuple and values of a Frame object
		self.frames_in_turn = frames_in_turn								# dict with keys of turn and values of number of frames in that turn
		self.healths = healths												# all known health data, tuple containing two lists, player1 and player2 healths
		self.num_frames = len(self.data)									# the number of total frames
		self.slider_exists = False											# begin by assuming the slider does not exist

		self.plot = Plot(self.healths, self.plot_ax)						# create the Plot object (plots the health)

		# try and get endStats, if not then file is still being created by engine (game is still running)
		try:
			last_frame = max(self.data, key=lambda f: (f[0], f[1]))			# the last frame of the entire match (single number)
			endStats = self.data[last_frame].data['endStats']				# here is where the error would be thrown - if endStats exists

			# From here on we know we have all data for entire game - endStats exists

			# if blit is on, do not create the slider
			if not BLIT:
				self.slider = Slider(self.fig.add_axes([0.6, 0.03, 0.3, 0.03]), 'Turn Slider', 0, self.num_frames, valfmt='%1i', valstep=1, color='w')
				self.slider.on_changed(self.slider_active)
				self.slider_exists = True 									# tracks whether the slider exists

			self.info = Info(endStats, self.info_ax, True)					# create the Info (right side) with endStates information
			self.real_time = False											# not longer running in real-time
		except KeyError as e:
			self.info = Info(None, self.info_ax)							# endStats doesn't exist, create Info with default values

	# change the interval speed between frames
	def change_play_speed(self, speed):
		self.speed = speed
		self.anim.event_source.interval = 100./SPEED[self.speed]

	# setup all initial static values for the board (axis and board points)
	def setup_board(self):
		self.board_ax.set_xticks(range(-1, 29))
		self.board_ax.set_yticks(range(-1, 29))
		self.board_ax.tick_params(axis=u'both', which=u'both',length=0)
		self.board_ax.set_xticklabels(['']+list(range(28)))
		self.board_ax.set_yticklabels(['']+list(range(28)))
		[spine.set_visible(False) for n, spine in self.board_ax.spines.items()]
		self.board_ax.set_title('Local Match Visualizer')

		self.plot_references()

		# matplotlib throws a warning for tight_layout because it doesn't work for
		# specific situations - we can ignore this warning
		with warnings.catch_warnings():
			warnings.simplefilter("ignore")
			plt.tight_layout()

	# handles all keyboard input - pretty self explanatory
	# this also handles changing the head based on the keyboard input
	# for example, 'right' means advance the head by 1 (hence self.single_advance = True)
	def keyboard_input(self, evt):
		if evt.key == ' ' or evt.key == 'enter':
			self.is_manual = False if self.is_manual else True
		elif evt.key == 'ctrl+right':
			self.is_manual = True
			if self.head[0]+1 in self.frames_in_turn:
				self.head = self.head[0]+1, 0
			else:
				self.head = self.head[0], self.frames_in_turn[self.head[0]]-3
		elif evt.key == 'ctrl+left':
			self.is_manual = True
			if self.head[1] == 0:
				if self.head[0] != 0:
					self.head = self.head[0]-1, 0
			else:
				self.head = self.head[0], 0
		elif evt.key == 'right':
			self.is_manual = True
			self.single_advance = True
		elif evt.key == 'left':
			self.is_manual = True
			self.single_advance = True
			self.backwards()
		elif evt.key in ['1','2','3','4','5','6']:
			self.change_play_speed(evt.key)
		elif evt.key == '<' or evt.key == ',':
			speed = str(int(self.speed)-1) if int(self.speed) > 1 else self.speed
			self.change_play_speed(speed)
		elif evt.key == '>' or evt.key == '.':
			speed = str(int(self.speed)+1) if int(self.speed) < 6 else self.speed
			self.change_play_speed(speed)

		# only update the slider if it exists
		if not BLIT and self.slider_exists:
			self.update_slider(self.head)
		self.update()							# something was changed, so update the board

	# converts a global frame value to a turn, frame pair
	def val_to_frame_turn(self, val):
		turn = 0
		frame = 0
		for i in self.frames_in_turn.values():
			if val < i: break
			val -= i
			turn += 1
		frame = val - 1

		try:
			self.data[(int(turn), int(frame))]
		except KeyError:
			if frame > 0:
				frame -= 1

		return (int(turn), int(frame))

	# converts a turn, frame pair into a global frame value
	def frame_turn_to_val(self, turns, frames):
		val = 0
		for i in self.frames_in_turn.values():
			if turns < 1: break
			val += i
			turns -= 1
		val += frames
		return int(val)

	# this is triggered every time the slider value changes for any reason
	def slider_active(self, val):
		if self.stop_slider_evt:					# don't update again if value was changed by code and not user
			return
		self.head = self.val_to_frame_turn(val)		# update the head based on the slider value
		self.is_manual = True 						# user changed something
		self.update(val)							# update the board

	# this sets the value of the slider every time the board updates, but suppresses the event (user did not select slider)
	def update_slider(self, pair):
		turns, frames = pair
		self.stop_slider_evt = True
		if self.end_of_game: self.slider.set_val(int(self.frame_turn_to_val(turns, frames))+2)
		else: self.slider.set_val(int(self.frame_turn_to_val(turns, frames)))
		self.stop_slider_evt = False

	# move backwards a single frame
	def backwards(self):

		# don't update - the user has paused the game
		if self.is_manual and not self.single_advance:
			return

		val = self.frame_turn_to_val(self.head[0], self.head[1])
		self.head = self.val_to_frame_turn(val)

		if self.head[0] < 0: self.head = 0, self.head[1]
		if self.head[1] < 0: self.head = self.head[0], -1

		# only update the slider if it exits
		if not BLIT and self.slider_exists:
			self.update_slider(self.head)
		self.single_advance = False				# reset the single advance (used with arrow keys)

	# this is the main function that moves the head forward
	def advance(self):
		
		# don't update - the user has paused the game
		if self.is_manual and not self.single_advance:
			return

		# while you can, increment the frame by 1
		try:
			self.data[self.head[0],self.head[1]+1]
			self.head = self.head[0], self.head[1]+1
		except KeyError:
			# outside of frames for that turn, try incrementing turn by 1
			try:
				self.data[self.head[0]+1,-1]
				self.head = self.head[0]+1, -1
			except KeyError as e:
				# outside both turns and frames - must be the end of game
				self.end_of_game = True


		# only update the slider if it exits
		if not BLIT and self.slider_exists:
			self.update_slider(self.head)
		self.single_advance = False				# reset the single advance (used with arrow keys)


	# this is the main function that supplies data to the matplotlib animation object
	def data_stream(self):
		while True:

			# everything in this block (real-time) is extrememly inefficient, becuase it has to constantly load new data
			if self.real_time:
				self.info_ax.clear()															# clear the inforation side

				self.fh.load_files(1,False,args['file']) 										# load latest replay (again)
				replay = self.fh.get_last_replay()												# get latest replay (again)

				# user paused game, don't advance
				if not self.is_manual:
					self.advance()

				self.general_init(replay.frames, replay.frames_in_turn, replay.healths)			# call general initialization

				# this is for the first call - cannot send before yield is reached (function called)
				try:
					self.frame_generator.send(self.num_frames)		# send the inverval generator the number of frames loaded
				except TypeError:
					pass

			# get the data
			p1Units = self.data[self.head]['p1Units']
			p2Units = self.data[self.head]['p2Units']
			p1Stats = self.data[self.head]['p1Stats']
			p2Stats = self.data[self.head]['p2Stats']

			units = self.cache_units(p1Units, 1) + self.cache_units(p2Units, 2)						# format the unit data into how it is passed to my functions
			self.patches.update_units(units, self.board_ax)											# update all the units
			self.patches.update_lbls(self.board_ax)													# update all the unit count labels

			self.info.update(p1Stats, p2Stats)														# update the information board
			self.plot.update(self.frame_turn_to_val(self.head[0], self.head[1]))					# update the health plot

			self.advance()																			# move the head forward 1
			self.check_end_of_game()																# if end of game, display winner

			yield self.patches.values() + self.patches.lbls + self.info.lbls + self.plot.lines		# send all dynamic data to the matplotlib animator

	# called by the animator everytime it's interval finishes
	def update(self, i=0):
		# self.patches.clear_board()	# inefficient, no longer used
		return next(self.stream) 		# sends the data to the animator

	# if blit is used, animator requires an init function to get intial graph values
	def init(self):
		return next(self.stream)

	# generator function to give the animator the number of total frames when running real-time
	def gen_frames(self):
		while True:
			num = yield
			yield num

	# format all of the raw unit data into how my functions recieve it
	def cache_units(self, units, p_index):
		filters, encryptors, destructors, pings, emps, scramblers, removes = units
		units_new = []
		for unit in filters: units_new.append((FILTER, (unit[0], unit[1]), unit[2], p_index, unit[3]))
		for unit in encryptors: units_new.append((ENCRYPTOR, (unit[0], unit[1]), unit[2], p_index, unit[3]))
		for unit in destructors: units_new.append((DESTRUCTOR, (unit[0], unit[1]), unit[2], p_index, unit[3]))
		for unit in pings: units_new.append((PING, (unit[0], unit[1]), unit[2], p_index, unit[3]))
		for unit in emps: units_new.append((EMP, (unit[0], unit[1]), unit[2], p_index, unit[3]))
		for unit in scramblers: units_new.append((SCRAMBLER, (unit[0], unit[1]), unit[2], p_index, unit[3]))

		return units_new

	# checks if reached the final frame - if so, display winner
	def check_end_of_game(self):
		self.end_of_game = False
		try:
			self.data[self.head[0]+1,-1]
		except KeyError as e:								# outside of turn limit
			try:
				self.data[self.head[0],self.head[1]+1]		
			except KeyError as e:							# outside of frame limit
				self.end_of_game = True 					# must be end of game

		if self.end_of_game: self.info.show_winner()		# show the winner if it is the end of game

	# show the matplotlib window
	def show(self):
		plt.show()

	# plots all the little green dots for position references
	def plot_references(self):
		refs = []
		for pos in self.__empty_grid():
			refs.append(Circle(pos, .02))
		colors = [100*random.random() for x in range(len(refs))]
		p = PatchCollection(refs, color='lightgreen')
		self.board_ax.add_collection(p)

	# should look familiar... :)
	def in_arena_bounds(self, location):
		"""Checks if the given location is inside the diamond shaped game board.

		Args:
			* location: A map location

		Returns:
			True if the location is on the board, False otherwise
		
		"""
		x, y = location
		full_board = 28
		half_board = 14

		row_size = y + 1
		startx = half_board - row_size
		endx = startx + (2 * row_size) - 1
		top_half_check = (y < half_board and x >= startx and x <= endx)

		row_size = (full_board - 1 - y) + 1
		startx = half_board - row_size
		endx = startx + (2 * row_size) - 1
		bottom_half_check = (y >= half_board and x >= startx and x <= endx)

		return bottom_half_check or top_half_check

	# should look familiar... :)
	def __empty_grid(self):
		grid = []
		for x in range(28):
			for y in range(28):
				if self.in_arena_bounds((x,y)):
					grid.append((x,y))
		return grid


# a simple data storage class to hold the data for a single frame
class Frame:
	def __init__(self, t, f, data):
		self.turn = t 					# the turn for this frame
		self.frame = f 					# the local frame for this frame
		self.data = data 				# the data for this frame

	def __repr__(self):
		return ('({}, {})'.format(self.turn, self.frame))

	def __getitem__(self, key):
		return self.data[key]


# Stores data from a single replay
class Replay:
	def __init__(self, f_name):
		self.fname = f_name 			# the file name of the replay
		self.ref = None					# stores the raw dict data as a reference
		self.frames = {}				# dict containing all data, keys are turn, frame tuple with Frame objects as values
		self.frames_in_turn = {}		# number of frames in each turn
		self.healths = ([], [])			# contains the healths for player1 and player2

		self.load_data()				# handles loading all the data from file into python variables

	def __eq__(self, other):
		return self.fname == other.fname
	def __string(self):
		return self.fname
	def __str__(self):
		return self.__string()
	def __repr__(self):
		return self.__string()

	# loads all data from a replay into the python variables
	def load_data(self):
		with open(self.fname) as f:
			i = 0
			for line in f:
				line = line.replace("\n", "")
				line = line.replace("\t", "")

				if (line != ''):
					data = json.loads(line)

					try:
						data['debug']
						self.ref = data
					except:
						turn_num = data['turnInfo'][1]
						frame_num = data['turnInfo'][2]
						self.frames[(turn_num, frame_num)] = Frame(turn_num, frame_num, data)

						self.healths[0].append(data['p1Stats'][0])
						self.healths[1].append(data['p2Stats'][0])

						try:
							self.frames_in_turn[turn_num] += 1
						except KeyError:
							self.frames_in_turn[turn_num] = 1

# handles opening multiple games (replays)
class FileHandler:
	def __init__(self):
		self.replays = []		# all of the replays loaded

	def get_replays(self):
		return self.replays

	def get_last_replay(self):
		return self.replays[0] if len(self.replays) > 0 else None

	def get_replay(self, i=0):
		if i >= len(self.replays):
			sys.stderr.write("Invalid replay")
			return None
		return self.replays[i]

	def __latest_replays(self, num=1, a=False):
		replay_dir = '{}/../../replays/'.format(os.path.dirname(os.path.realpath(__file__)))
		files = glob.glob('{}*.replay'.format(replay_dir))
		files = sorted(files, key=os.path.getctime, reverse=True)
		if a:
			return files
		return files[:num]

	def load_files(self, num=1, a=False, f_names=[]):
		self.replays = []
		if len(f_names) > 0:
			for f_name in f_names:
				if f_name.find('replays') == -1:
					self.replays.append(Replay('replays/'+f_name))
				else:
					self.replays.append(Replay(f_name))
		else:
			for f_name in self.__latest_replays(num, a):
				self.replays.append(Replay(f_name))


# This is all almost directly copied from run_match.py

# Runs a single game
def run_single_game(process_command):
	print("Start run a match")
	p = subprocess.Popen(
		process_command,
		shell=True,
		stdout=sys.stdout,
		stderr=sys.stderr
		)
	# daemon necessary so game shuts down if this script is shut down by user
	p.daemon = 1
	p.wait()
	print("Finished running match")

def run_match(a1='', a2=''):
	# Get location of this run file
	file_dir = os.path.dirname(os.path.realpath(__file__))
	parent_dir = os.path.abspath('{}/..'.format(os.path.join(file_dir, os.pardir)))

	# Get if running in windows OS
	is_windows = sys.platform.startswith('win')
	print("Is windows: {}".format(is_windows))

	# Set default path for algos if script is run with no params
	default_algo = parent_dir + "/algos/starter-algo-ZIPME/run.ps1" if is_windows else parent_dir + "/algos/starter-algo-ZIPME/run.sh" 
	algo1 = default_algo
	algo2 = default_algo

	if a1 != '':
		algo1 = a1
	if a2 != '':
		algo2 = a2

	# If folder path is given instead of run file path, add the run file to the path based on OS
	# trailing_char deals with if there is a trailing \ or / or not after the directory name
	if is_windows:
		if "run.ps1" not in algo1:
			trailing_char = "" if algo1.endswith("\\") else "/"
			algo1 = algo1 + trailing_char + "run.ps1"
		if "run.ps1" not in algo2:
			trailing_char = "" if algo2.endswith("\\") else "/"
			algo2 = algo2 + trailing_char + "run.ps1"
	else:
		if "run.sh" not in algo1:
			trailing_char = "" if algo1.endswith('/') else "/"
			algo1 = algo1 + trailing_char + "run.sh"
		if "run.sh" not in algo2:
			trailing_char = "" if algo2.endswith('/') else "/"
			algo2 = algo2 + trailing_char + "run.sh"

	print("Algo 1: ", algo1)
	print("Algo 2:", algo2)

	match = mp.Process(target=run_single_game, args=("cd {} && java -jar engine.jar work {} {}".format(parent_dir, algo1, algo2),))
	match.start()

def main(args):
	global BLIT
	BLIT = args['blit']				# get whether blit is enabled
	save = args['save']				# get whether  save is enabled
	writers = args['writers']		# get save modes
	keep_trying = args['keep_trying']		# get whether to keep trying writer types

	if args['run_match'][0] != 'empty':
		# inside here we are now running a match and displaying real-time data

		# warn the user about run-time and saving
		if save != '':
			print ('\n\nWARNING: You specified a save file, but nothing will be saved since this is running real time. Wait for the match to end.')
		elif 'empty' not in writers:
			print ('\n\nWARNING: You specified a writer mode, but nothing will be saved since this is running real time. Wait for the match to end.')
		elif keep_trying:
			print ('\n\nWARNING: You specified keep trying writers, but nothing will be saved since this is running real time. Wait for the match to end.')

		fh = FileHandler()																		# create a file handler object
		fh.load_files(1,False,args['file'])														# load latest replay
		previous_replay = str(fh.get_last_replay())												# get the replay that was last created

		if len(args['run_match']) > 1: run_match(args['run_match'][0], args['run_match'][1])	# run the match with both algos specified
		else: run_match(args['run_match'][0])													# run the match with one algo specified

		# wait to open visualizer until a new replay has been created
		while str(fh.get_last_replay()) == previous_replay:
			fh.load_files()
			time.sleep(.5)

		# keep trying to load the replay file until it is capable of getting data from it - then start the visualizer
		while True:
			try:
				fh.load_files(1,False,args['file'])
				replay = fh.get_last_replay()
				animatedReplay = Graph(replay.frames, replay.frames_in_turn, replay.healths, writers, keep_trying, fh=fh)		# create our Graph object
				break
			except RuntimeError:																		# we raised this error when data was nothing in Graph init()
				time.sleep(.5)
	else:
		# here we know the replay file is already created an finished

		# warn the user about saving
		if save == '' and 'empty' not in writers:
			print ('You specified a writer type, but it will not be used since you are not saving the animation')
		elif save == '' and keep_trying:
			print ('You specified to keep trying writers, but it will not be used since you are not saving the animation')

		fh = FileHandler()																			# create a file handler object
		fh.load_files(1,False,args['file'])															# load latest replay
		replay = fh.get_last_replay()																# get latest replay

		animatedReplay = Graph(replay.frames, replay.frames_in_turn, replay.healths, writers, keep_trying, save=save)		# create our Graph object


if __name__ == '__main__':
	args = parse_args() # get command line arguments
	main(args)			# run program
	# print (animation.writers.list())
