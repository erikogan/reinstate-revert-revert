import argparse

from reinstate_revert_revert.parser import Parser


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("file", help="contains a log message to process", nargs="+")
    parser.add_argument(
        "-e",
        "--encoding",
        help="character encoding for the file(s) [DEFAULT: UTF-8]",
        default="UTF-8",
    )
    args = parser.parse_args()

    Parser(encoding=args.encoding).run(args.file)
