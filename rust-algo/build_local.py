import subprocess
import json
import shutil
import platform
import os

from json.decoder import JSONDecodeError
from os import path

def get_metadata():
    try:
        with open(path.relpath('algo.json')) as metadata:
            return json.loads(metadata.read())
    except FileNotFoundError as e:
        print("file not found: {}".format(e))
        return None
    except JSONDecodeError as e:
        print("json decode errror: {}".format(e))
        return None

def compile_rust():
    # read metadata
    metadata = get_metadata()
    if metadata is None:
        return False
    
    # focus on language-specific metadata
    metadata = metadata.get('rust-specific', {})

    # build the command
    command = ['cargo']

    if 'toolchain' in metadata:
        toolchain = metadata['toolchain']
        if toolchain != "stable":
            command.append('+' + metadata['toolchain'])

    command.append('build')

    if 'package' in metadata:
        package = metadata['package']
        command.append('--package')
        command.append(package)
        command.append('--bin')
        command.append(package)
    else:
        print("no package")
        return False

    release = metadata.get('release', False)
    if release:
        print("release mode")
        command.append('--release')

    # run cargo compilation
    print("running: {}".format(command))
    subprocess.check_output(command)

    # find the algo target dir
    algo_target = metadata.get('compile-target', 'algo-target')

    # move the built binary into the algo target directory
    if platform.system() == 'Windows':
        executable = package + ".exe"
    else:
        executable = package
    if release:
        binary = os.path.join('target', 'release', executable)
    else:
        binary = os.path.join('target', 'debug', executable)
    if platform.system() == 'Windows':
        destination_file = 'algo.exe'
    else:
        destination_file = 'algo'
    move_to = os.path.join(algo_target, destination_file)
    print("moving {} to {}".format(binary, move_to))
    shutil.move(str(binary), str(move_to))
    print("moved")

    return True


if __name__ == '__main__':
    abspath = os.path.abspath(__file__)
    dname = os.path.dirname(abspath)
    os.chdir(dname)

    result = compile_rust()

    if not result:
        print("!--build failure--!")

