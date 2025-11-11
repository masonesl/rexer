import sys

from lib.core import CoreIter
from lib.regex import Regex


if __name__ == "__main__":
    # first 2 args will be main.py and {path}/rexer
    if len(sys.argv) < 3:
        raise Exception("No arguments to parse")

    CoreIter(sys.argv[2:]).foreach(lambda s: print(Regex(s)))
