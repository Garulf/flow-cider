from enum import Enum
from dataclasses import dataclass
import argparse
from pathlib import Path
import subprocess
from typing import Optional, TypedDict
import json

SOURCE = 'src'
MANIFEST = 'plugin.json'
MANIFEST_PATH = Path(SOURCE) / MANIFEST


class PluginManifest(TypedDict):
    ID: str
    ActionKeyword: str
    Name: str
    Description: str
    Author: str
    Version: str
    Language: str
    Website: str
    IcoPath: str
    ExecuteFileName: str


class BumpType(Enum):
    MAJOR = 'major'
    MINOR = 'minor'
    PATCH = 'patch'

    def __str__(self) -> str:
        return self.value


def read_version() -> str:
    with open(MANIFEST_PATH) as f:
        return json.load(f)['Version']


def change_version(bump_type: BumpType, version: str) -> str:
    """Bump the version according to the given bump type."""
    major, minor, patch = version.split('.')
    if bump_type == BumpType.MAJOR:
        major = str(int(major) + 1)
        minor = '0'
        patch = '0'
    elif bump_type == BumpType.MINOR:
        minor = str(int(minor) + 1)
        patch = '0'
    elif bump_type == BumpType.PATCH:
        patch = str(int(patch) + 1)
    else:
        raise ValueError(f'Invalid bump type: {bump_type}')
    return '.'.join([major, minor, patch])


def write_version(version: str):
    """Write the new version to the manifest."""
    with open(MANIFEST_PATH) as f:
        manifest = json.load(f)
    manifest['Version'] = version
    with open(MANIFEST_PATH, 'w') as f:
        json.dump(manifest, f, indent=4)


def commit_version(current_version: str, new_version: str):
    """Commit the version change."""
    subprocess.check_call(['git', 'add', MANIFEST_PATH])
    subprocess.check_call(
        ['git', 'commit', '-m', f'Bumped version from {current_version} to {new_version}'])


def tag_version(version: str):
    """Tag the current commit with the given version."""
    subprocess.check_call(['git', 'tag', version])


def check_dirty():
    """Return true if uncommitted changes exist."""
    try:
        subprocess.check_call(['git', 'diff', '--quiet'])
    except subprocess.CalledProcessError:
        raise SystemExit(
            'Uncommitted changes exist. Commit or discard them before bumping the version.')


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument('bump_type', type=BumpType, choices=BumpType)
    parser.add_argument('-d', '--dry-run', action='store_true',
                        help='Do not write the new version to the manifest.')
    parser.add_argument('-c', '--commit', action='store_true', default=True,
                        help='Commit the version change.')
    parser.add_argument('-t', '--tag', action='store_true', default=True,
                        help='Tag the current commit with the new version.')
    return parser.parse_args()


def main(args: argparse.Namespace):
    """Execute the script."""
    current_version = read_version()
    new_version = change_version(args.bump_type, current_version)
    if current_version == new_version:
        raise SystemExit(f'No change in version from {current_version}')
    if args.commit:
        check_dirty()
    if not args.dry_run:
        write_version(new_version)
    if args.commit and not args.dry_run:
        commit_version(current_version, new_version)
    if args.tag and args.commit and not args.dry_run:
        tag_version(new_version)
    if args.tag and not args.commit:
        raise SystemExit('Cannot tag without committing.')
    print(f'Bumped version from {current_version} to {new_version}')


if __name__ == '__main__':
    main(parse_args())
