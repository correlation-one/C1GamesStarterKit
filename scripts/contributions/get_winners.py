'''

This is a python script to check all replay files in the /replays folder.
It looks at each file and simply looks for a string to see which player won.

This program assumes this file is in the scripts directory
It also assumes the "replays" folder exists.
You can change this of course, but that is on you :).

If you have questions just ask me on the forums (https://c1playtestforum.com/) - @Isaac

'''

try:
	import os

	replayDir = os.getcwd().replace('scripts/contributions','') + '/replays'			# Gets the main directory

	# Initialize counters
	p1WinCnt = 0
	p2WinCnt = 0
	unknown = 0

	# Loop through every file in "replays" directory
	for filename in os.listdir(replayDir):
		if filename.endswith(".replay"):
			with open(replayDir+'\\'+filename, 'r') as file:
				data = file.read()
				if (data.find('"winner":1') != -1): p1WinCnt += 1
				elif (data.find('"winner":2') != -1): p2WinCnt += 1
				else: unknown += 1

	# Print results
	print ('Player 1 Wins: {}'.format(p1WinCnt))
	print ('Player 2 Wins: {}'.format(p2WinCnt))

	if (unknown > 0): print ('Could not find winner: {}'.format(unknown))

	print ()
except Exception as e:
	print (e)
