import sys


BANNER_TEXT = "---------------- Starting Your Algo --------------------"


def get_command():
    """Gets input from stdin
    
    """
    return sys.stdin.readline()

def send_command(cmd):
    """Sends your turn to standard output.
    Should usually only be called by 'GameState.submit_turn()'

    """
    sys.stdout.write(cmd.strip() + "\n")
    sys.stdout.flush()

def debug_write(*msg):
    """Prints a message to the games debug output

    Args:
        msg: The message

    """
    #Printing to STDERR is okay and printed out by the game but doesn't effect turns.
    sys.stderr.write(", ".join(map(str, msg)).strip() + "\n")
    sys.stderr.flush()
