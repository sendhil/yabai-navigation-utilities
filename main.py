#!/user/bin/env python3

from typing import Any, Optional
from dataclasses import dataclass
import sys
import logging
import json
import subprocess
import argparse


@dataclass
class Options(object):
    app_name: str
    skip_focus: bool


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


def main():
    options = get_options()

    results = call_yabai(["-m", "query", "--windows"])

    window_id: Optional[int] = None
    for result in results:
        if result["app"] == options.app_name:
            window_id = result["id"]

    if window_id is None:
        raise "Obsidian not found"

    space_index: Optional[int] = None
    results = call_yabai(["-m", "query", "--spaces"])
    for result in results:
        if result["has-focus"]:
            space_index = result["index"]

    if space_index is None:
        raise "Could not find current space"

    call_yabai(["-m", "window", str(window_id), "--space", str(space_index)])

    if not options.skip_focus:
        call_yabai(["-m", "window", str(window_id), "--focus"])


if __name__ == "__main__":
    main()
