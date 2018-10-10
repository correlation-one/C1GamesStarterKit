# This is a PowerShell script to run a bunch of games with a single command.
# This is intended for when you have worked out all bugs and are testing to see if a new strategy really is better than an old one.

# This program assumes this file is in the scripts directory
# You can change this of course, but that is on you :).

# Inside $runprog you can see that there is the execution "scripts/run_match.ps1 algos/my-bot algos/starter-algo" (line 48).
# This should be the same command you use to start your game locally. So change "my-bot" to be whatever the name is of your algo directory.

# The script at the end is a seperate python file that looks at all the replay files and tells you how many each player won.

# You call this script in PowerShell by running .\[THIS_FILE_NAME] [NUM_OF_GAMES] [BATCH_SIZE]

# An example would be: .\run_multiple 20 5
# This would run the game 20 times with only 5 games running at a time.

# You can leave out a batch size and the default is set to 5 (of course you can edit this below)
# so this command would do the same thing: .\run_multiple 20

# DO NOT RUN WITH A LARGE BATCH SIZE (like >15, depending on your computer) or else it will take forever and crash

# If you have questions just ask me on the forums (https://c1playtestforum.com/) - @Isaac


$global:completed = 0		# Number of games that have finished
$global:running = 0			# Number of games currently running
$dir = [System.IO.Path]::GetDirectoryName($MyInvocation.MyCommand.Path)		#Get the current directory of this script

# Set batch size defaults - sets how many games can run at one time
If (!$args[1]) {
	$global:batch = 5
}
ElseIf ($args[1] -lt 0) {
	$global:batch = 5
}
Else {
	$global:batch = $args[1]
}

# Main loop that runs each game - each loop starts a game in a new powershell (not visible)
For ($i = 1; $i -lt $args[0]+1; $i++) {
	Write-Host "started game #$i"
	
	# This is the program that is run, so essentially just starts the game
	$runprog = {
		param($num,$path)
		cd $path
		cd ..
		cd ..
		scripts/run_match.ps1 algos/starter-algo algos/starter-algo | Out-Null				# Edit this to change the algo you are running
	}
	$job = Start-Job $runprog -ArgumentList $i,$dir 		# Start the new powershell
	$global:running++										# Add 1 to the number of running programs
	
	# This is triggered when the associated game ends
	$jobEvent = Register-ObjectEvent $job StateChanged -MessageData $i -Action {
		Write-Host ("finished game #$($event.MessageData)")
		$global:completed++				# Add to our completed counter
		$global:running--				# Remove the number of running games by 1
		$jobEvent | Unregister-Event	# Remove the job
	}
	
	# if the number of games running equals the batch size - wait here
	While (($global:batch - $global:running) -eq 0) {}
}

# Wait for it all to complete
While ($global:completed -lt $args[0]) {}

Write-Host "FINISHED ALL GAMES!`n"

# This script looks at all the replay files and prints out the number of winners
py scripts/contributions/get_winners.py
