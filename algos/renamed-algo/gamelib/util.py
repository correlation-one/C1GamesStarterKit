import sys


BANNER_TEXT = "---------------- Starting Your Algo --------------------"


def get_command():
    return sys.stdin.readline()


def send_command(cmd):
    sys.stdout.write(cmd.strip() + "\n")
    sys.stdout.flush()


# Printing to STDERR is okay and printed out by the game but doesn't effect turns.
def debug_write(*msg):
    sys.stderr.write(", ".join(map(str, msg)).strip() + "\n")
    sys.stderr.flush()


def point_in_list(point, check_points):
    for p in check_points:
        if int(point[0]) == int(p[0]) and int(point[1]) == int(p[1]):
            return True
    return False
