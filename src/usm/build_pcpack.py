import argparse
import os
import sys
from os.path import splitext

from .parsers.pcpack import PCPackParser


def main():
    p = argparse.ArgumentParser(
        prog="pack",
        description="Build PACK file from directory with assets.",
    )

    p.add_argument("input", help=".PACK file")

    args = p.parse_args()

    input_path = os.path.abspath(args.input)
    if not input_path:
        sys.exit("No .pack files found.")

    name_pak, ext = splitext(input_path)

    if ext != ".PCPACK":
        sys.exit("File must be contain *.PCPACK extension")

    parser = PCPackParser()
    pack = parser.read(input_path)
    parser.build(name_pak, pack)


if __name__ == '__main__':
    main()
