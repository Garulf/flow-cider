from dataclasses import dataclass
import argparse

import bump
import build


class BuildArgs(argparse.Namespace):
    zip: bool = True
    install: bool = False


def main(args: argparse.Namespace):
    print("Bumping version...")
    try:
        bump.main(args)
    except SystemExit:
        raise
    build_args = BuildArgs()
    print("Building...")
    build.main(build_args)


if __name__ == '__main__':
    main(bump.parse_args())
