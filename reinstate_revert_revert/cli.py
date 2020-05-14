import sys

from reinstate_revert_revert.parser import Parser


def main():
    Parser().run(sys.argv[1:])
