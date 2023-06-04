import json
import time
from typing import TypedDict, Union
from pathlib import Path
import subprocess
import sys
import zipapp
import shutil
import zipfile
import argparse

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
SOURCE = 'src'
PLUGIN_DIR = 'plugin'
BUILD = '.build'
DIST = '.dist'
PLUGIN_MANIFEST = "plugin.json"
HOME_DIR = Path.home()
FL_PLUGIN_DIR = HOME_DIR.joinpath(
    'AppData', 'roaming', 'FlowLauncher', 'Plugins')

WATCHING = False


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


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument('--install', action='store_true')
    parser.add_argument('--zip', action='store_true')
    parser.add_argument('--watch', action='store_true')
    parser.add_argument('--version', action='store_true')
    return parser.parse_args()


def install_dependencies(path: str = BUILD):
    subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-r',
                           'requirements.txt', '-t', path])


def convert_name(name: str) -> str:
    return name.replace('_', '-').replace(" ", "-").lower()


def plugin_manifest(source_path: Union[str, Path]) -> PluginManifest:
    with open(Path(source_path) / PLUGIN_MANIFEST) as f:
        return json.load(f)


def zip_plugin(plugin_json: PluginManifest,
               distribute_path: Union[Path, str]) -> str:
    version = plugin_json['Version']
    name = convert_name(plugin_json['Name'])
    zip_name = f'{name}-{version}.zip'
    with zipfile.ZipFile(zip_name, 'w') as zip_file:
        for file in Path(distribute_path).iterdir():
            if file.is_file():
                zip_file.write(file, arcname=file.name)
    return zip_name


def install_plugin(plugin_json: PluginManifest,
                   distribute_path: Union[Path, str]) -> str:
    name = convert_name(plugin_json['Name'])
    plugin_dir_name = f"{name}-{plugin_json['Version']}"
    plugin_install_dir = Path(FL_PLUGIN_DIR / plugin_dir_name)
    plugin_install_dir.mkdir(exist_ok=True)
    try:
        shutil.copytree(distribute_path, plugin_install_dir,
                        dirs_exist_ok=True)
    except shutil.Error:
        print("Some files failed to copy")
    return str(plugin_install_dir)


def create_zipapp(source: Union[str, Path], plugin_manifest: PluginManifest) -> str:
    name = convert_name(plugin_manifest['Name'])
    zipapp_name = f'{name}.pyz'
    plugin_dir = Path(source) / PLUGIN_DIR
    shutil.copytree(plugin_dir, BUILD, dirs_exist_ok=True,
                    ignore=shutil.ignore_patterns(PLUGIN_MANIFEST))
    install_dependencies()
    dist = Path(DIST)
    if dist.exists():
        # remove files in dist
        shutil.rmtree(dist)
    dist.mkdir(exist_ok=True)
    zipapp.create_archive(BUILD, dist / zipapp_name)
    shutil.copytree(SOURCE, dist,
                    ignore=shutil.ignore_patterns(
                        PLUGIN_DIR, plugin_manifest['Name']),
                    dirs_exist_ok=True)
    return zipapp_name


def update_on_change(watch_path: str):
    class OnChangeHandler(FileSystemEventHandler):

        def on_any_event(self, event):
            if event.event_type in ['created', 'modified', 'deleted']:
                print(f'Change detected: {event.src_path}')
                if event.is_directory:
                    return
                main(parse_args())

    observer = Observer()
    event = OnChangeHandler()
    observer.schedule(event, watch_path, recursive=True)
    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()


def main(args: argparse.Namespace) -> None:
    global WATCHING
    if args.watch and not WATCHING and not args.version:
        WATCHING = True
        print(f"Watching for changes in {SOURCE}...")
        update_on_change(SOURCE)

    else:
        p_manifest = plugin_manifest(SOURCE)
        if args.version:
            print(p_manifest['Version'])
            return
        zipapp_name = create_zipapp(SOURCE, p_manifest)
        print(f'Successfully created {zipapp_name}!')
        if args.zip:
            zip_filename = zip_plugin(p_manifest, DIST)
            print(f'Successfully created {zip_filename}!')
        if args.install:
            install_dir = install_plugin(p_manifest, DIST)
            print(f'Successfully installed to: {install_dir}!')
        # print bell
        print('\a')


if __name__ == "__main__":
    main(parse_args())
