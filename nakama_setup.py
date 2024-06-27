import subprocess
import pathlib
import shlex
from nakama_dependency_list import pacs

try:
    for pac in pacs:
        print(f"starting {pac} install")
        cmd = f"pip install {pac}"
        open_process = subprocess.Popen(shlex.split(cmd))
        open_process.wait()
        print(f"done installing {pac}")
except Exception as e:
    print(e)
    print("something wrong while installing dependecies, call for help!")
