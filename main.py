import sys

from lib.core import CoreIter
from lib.dfa import Dfa
from lib.nfa import Nfa
from lib.regex import Regex


if __name__ == "__main__":
    # first 2 args will be main.py and {path}/rexer
    if len(sys.argv) < 3:
        raise Exception("No arguments to parse")

    (CoreIter(sys.argv[2:])
        .map(lambda s: Regex(s))
        .map(lambda r: Nfa().with_regex(r))
        .map(lambda s: Dfa.from_nfa(s))
        .foreach(lambda s: print(s)))
