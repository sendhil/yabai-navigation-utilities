#!/user/bin/env python3

from typing import Any, Optional
from dataclasses import dataclass
import config
import sys
import logging
import json
import subprocess
import argparse


@dataclass
class Options(object):
    app_name: str
    skip_focus: bool


@dataclass
class WindowDetails(object):
    window_id: int
    space_id: int


def get_options() -> Options:
    parser = argparse.ArgumentParser()
    parser.add_argument("-a", "--app", help="App Name")
    parser.add_argument("-s",
                        "--skip-focus",
                        action="store_true",
                        help="Skip focusing on Window")
    parser.add_argument("-v",
                        "--verbose",
                        action="store_true",
                        help="Verbose mode to aid in debugging")

    if len(sys.argv) == 1:
        parser.print_help(sys.stderr)
        sys.exit(1)

    args = vars(parser.parse_args())

    return Options(app_name=args['app'], skip_focus=args['skip_focus'])


def call_yabai(args) -> Any:
    if args[0] != "yabai":
        args = ["yabai"] + args

    logging.debug(f"Calling Yabai With Args: {args}")
    command_output = subprocess.run(
        args, stdout=subprocess.PIPE).stdout.decode('utf-8')

    if len(command_output) > 0:
        logging.debug(f"Output from Yabai: {command_output}")
        return json.loads(command_output)
    else:
        logging.debug("No output from Yabai")
        return None


def get_window_data() -> Any:
    return call_yabai(["-m", "query", "--windows"])


def get_spaces_data() -> Any:
    return call_yabai(["-m", "query", "--spaces"])


def find_current_space() -> int:
    space_index: Optional[int] = None
    for space in get_spaces_data():
        if space["has-focus"]:
            space_index = space["index"]

    if space_index is None:
        raise Exception("Could not find current space")

    return space_index


def find_app_window(app_name: str) -> WindowDetails:
    window_details: Optional[WindowDetails] = None
    for window in get_window_data():
        if window["app"] == app_name:
            window_details = WindowDetails(window_id=window["id"],
                                           space_id=window["space"])

    if window_details is None:
        raise Exception(f"Could not find app {app_name}")

    return window_details


def move_window_to_current_space(window_details: WindowDetails):
    call_yabai([
        "-m", "window",
        str(window_details.window_id), "--space",
        str(find_current_space())
    ])


def focus_on_window(window_id: int):
    call_yabai(["-m", "window", str(window_id), "--focus"])


def main():
    options = get_options()
    window_details = find_app_window(options.app_name)
    move_window_to_current_space(window_details)

    # Focus on window
    if not options.skip_focus:
        focus_on_window(window_details.window_id)


if __name__ == "__main__":
    main()
