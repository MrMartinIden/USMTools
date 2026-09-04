import argparse
import os
import pathlib
import sys
from os.path import splitext

from .parsers.pack import PackParser
from .parsers.pcpack import PCPackParser
from .parsers.xbpack import XBPackParser

PARSERS: dict[str, PackParser] = {
    ".PCPACK": PCPackParser(),
    ".XBPACK": XBPackParser(),
}


def scan_pack_files(input_path: str):
    path = pathlib.Path(input_path)
    valid_suffixes = {".pcpack", ".xbpack", ".ps2pack"}

    if path.is_dir():
        for p in sorted(path.iterdir()):
            if p.suffix.lower() in valid_suffixes:
                yield str(p)
    elif path.is_file():
        if path.suffix.lower() in valid_suffixes:
            yield str(path)
        else:
            sys.exit("Error: input file is not a supported pack file (.pcpack, .xbpack, .ps2pack)")
    else:
        sys.exit("Error: input path not found")


def list_pack(file: str):
    _, ext = splitext(file)

    parser = PARSERS.get(ext)
    if parser is None:
        print(f"No parser registered for {ext} pack files.")
        return

    parser.list(file)


def extract_pack(file: str):
    _, ext = splitext(file)

    parser = PARSERS.get(ext)
    if parser is None:
        print(f"No parser registered for {ext} pack files.")
        return

    parser.extract(file)


def main():
    p = argparse.ArgumentParser(
        prog="unpack",
        description="Unpack or list PACK files from a file or a directory.",
    )

    p.add_argument("input", help=".PACK file or directory of .PACK files")

    p.add_argument(
        "-l",
        "--list",
        action="store_true",
        default=False,
        help="List contents instead of extracting",
    )

    args = p.parse_args()

    input_path = os.path.abspath(args.input)

    packs = list(scan_pack_files(input_path))
    if not packs:
        sys.exit("No .pack files found.")

    do_list = args.list

    for pack in packs:
        if do_list:
            list_pack(pack)
        else:
            extract_pack(pack)

    print("\nDone.")


if __name__ == '__main__':
    main()
