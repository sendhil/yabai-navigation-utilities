#!/user/bin/env python3

from base64 import decode
from typing import Any, Optional, List, Dict
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

    if args["verbose"]:
        logging.basicConfig(level=logging.DEBUG)

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
                                           app=app_name,
                                           space_id=window["space"])

    if window_details is None:
        raise Exception(f"Could not find app {app_name}")

    return window_details


def move_window_to_space(window_details: WindowDetails, space_id: int):
    call_yabai([
        "-m", "window",
        str(window_details.window_id), "--space",
        str(space_id)
    ])


def focus_on_window(window_id: int):
    call_yabai(["-m", "window", str(window_id), "--focus"])


def get_current_window() -> WindowDetails:
    window_details: Optional[WindowDetails] = None

    for window in get_window_data():
        if window["has-focus"]:
            window_details = WindowDetails(window_id=window["id"],
                                           app=window["app"],
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

        # Check if window is stale, if so remove, and reset index
        current_valid_windows = get_window_data()

        # Flatten current windows to speed up lookup
        valid_window_map: Dict[int, str] = {}
        for window in current_valid_windows:
            valid_window_map[window["id"]] = window["app"]

        # Filter out invalid windows
        windows_to_preserve: List[WindowDetails] = []
        for window in window_state.windows:
            if window.window_id in valid_window_map:
                windows_to_preserve.append(window)
            else:
                logging.debug(f"Found invalid window {window} - removing.")
                window_state.current_window_index = -1
        window_state.windows = windows_to_preserve

        return window_state


def hide_window(window_details: WindowDetails):
    logging.debug(f"Hiding Window : {window_details}")
    move_window_to_space(window_details=window_details,
                         space_id=window_details.space_id)


def show_window(window_details: WindowDetails):
    logging.debug(f"Showing Window : {window_details}")
    move_window_to_space(window_details=window_details,
                         space_id=find_current_space())
    focus_on_window(window_details.window_id)


def main():
    options = get_options()

    if options.store_window:
        logging.debug("Attempting to store window")
        current_window: Optional[WindowDetails] = None
        for window in get_window_data():
            if window["has-focus"]:
                current_window = WindowDetails(window_id=window["id"],
                                               app=window["app"],
                                               space_id=window["space"])

        if not current_window:
            raise Exception("Could not find current window")

        logging.debug(f"Storing window : {current_window}")

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
            logging.debug(f"Added {current_window} from stored Windows")
        else:
            logging.debug(f"Removed {current_window} from stored Windows")

        window_state.windows = new_windows
        save_window_state(window_state)
    else:
        logging.debug("Toggling window")
        window_state = retrieve_saved_window_state()

        # Check index.
        current_window_index = window_state.current_window_index

        if current_window_index >= len(
                window_state.windows) or current_window_index < -1:
            logging.debug("Resetting current_window_index")
            current_window_index = -1

        # 1. Hide Current Window
        if current_window_index > -1:
            hide_window(window_state.windows[current_window_index])

        # 2. Show Next Window
        if current_window_index < len(window_state.windows) - 1:
            show_window(window_state.windows[current_window_index + 1])
            current_window_index += 1
        else:
            current_window_index = -1
            logging.debug(
                "Hit the end of the list, starting over at the beginning.")

        window_state.current_window_index = current_window_index
        save_window_state(window_state)


if __name__ == "__main__":
    main()
