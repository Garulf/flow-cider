import argparse
from typing import List, Tuple


FLAG_CHAR = ':'
CHOICES = ["songs", "albums"]


def parse_args(input: str) -> Tuple[argparse.Namespace, List[argparse.Action]]:
    parser = argparse.ArgumentParser(prefix_chars=FLAG_CHAR, add_help=False)
    parser.add_argument('query', type=str, nargs='*',
                        help='Query to search for')
    parser.add_argument(':limit', type=int, default=20, nargs='?',
                        help='Limit of results to return for each type')
    parser.add_argument(':by', type=str, nargs='?', help='Filter by [artist]')
    parser.add_argument(':type', type=str, nargs='?',
                        help=f'Filter by [{"|".join(CHOICES)}]')

    return parser.parse_intermixed_args(input.split()), parser._actions


if __name__ == "__main__":
    args, actions = parse_args("test this :limit 10")
    for item in actions:
        print(item)
