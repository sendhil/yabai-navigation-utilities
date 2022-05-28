#!/user/bin/env python3

from base64 import decode
from typing import Any, Optional, List
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
    store_window: bool
    toggle_window: bool


# TODO: Remove pickling and do this by hand
@dataclass
class WindowDetails(object):
    window_id: int
    app: Optional[str]
    space_id: int


@dataclass
class WindowState(object):
    windows: List[WindowDetails]
    current_window_index: int


def get_options() -> Options:
    parser = argparse.ArgumentParser()

    group = parser.add_mutually_exclusive_group()
    group.add_argument("-s",
                       "--store",
                       action="store_true",
                       help="toggle store current window")
    group.add_argument("-t",
                       "--toggle",
                       action="store_true",
                       help="toggle current window visibility")
    parser.add_argument("-a", "--app", help="App Name")
    parser.add_argument("-v",
                        "--verbose",
                        action="store_true",
                        help="Verbose mode to aid in debugging")

    if len(sys.argv) == 1:
        parser.print_help(sys.stderr)
        sys.exit(1)

    args = vars(parser.parse_args())

    return Options(app_name=args['app'],
                   store_window=args['store'],
                   toggle_window=args['toggle'])


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


def get_current_window() -> WindowDetails:
    window_details: Optional[WindowDetails] = None

    for window in get_window_data():
        if window["has-focus"]:
            window_details = WindowDetails(window_id=window["id"],
                                           name=window["app"],
                                           space_id=window["space"])

    if not window_details:
        raise Exception("Could not store window")

    return window_details


def save_window_state(window_state):
    json_data = json.dumps(window_state,
                           default=lambda o: o.__dict__,
                           indent=4)

    config.write_config(json_data)


def retrieve_saved_window_state():
    decoded_config = config.get_config()
    if decoded_config is None:
        return WindowState(windows=[], current_window_index=-1)
    else:
        window_state = WindowState(**decoded_config)
        # TODO - Clean this up
        window_state.windows = [
            WindowDetails(**item) for item in window_state.windows
        ]
        return window_state


def main():
    options = get_options()

    if options.store_window:
        current_window: Optional[WindowDetails] = None
        for window in get_window_data():
            if window["has-focus"]:
                current_window = WindowDetails(window_id=window["id"],
                                               app=window["app"],
                                               space_id=window["space"])

        if not current_window:
            raise Exception("Could not find current window")

        window_state = retrieve_saved_window_state()
        new_windows: List[WindowDetails] = []
        found_window = False
        # Filter out the current window from the list
        for window in window_state.windows:
            if window.window_id == current_window.window_id and window.app == current_window.app:
                found_window = True
            else:
                new_windows.append(window)

        # Save the window since it's not currently in our list
        if not found_window:
            new_windows.append(current_window)

        window_state.windows = new_windows
        save_window_state(window_state)

        exit(0)
    else:
        print("TOGGLE WINDOW")
        decoded_config = config.get_config()
        window_state = WindowState(**decoded_config)

        exit(0)

    window_details = find_app_window(options.app_name)
    move_window_to_current_space(window_details)
    focus_on_window(window_details.window_id)


if __name__ == "__main__":
    main()
