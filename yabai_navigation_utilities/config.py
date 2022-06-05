import os
import json
from os.path import join
from typing import Any

# Loosely based on https://github.com/CITGuru/ConfigStore/blob/master/pyconfigstore/utils.py


def write_config(jsonData):
    create_config_dir('yabai-window-utils')
    with open(get_config_path(), 'w') as fp:
        json.dump(jsonData, fp)


def get_config() -> Any:
    create_config_dir('yabai-window-utils')
    if not os.path.exists(get_config_path()):
        return None
    with open(get_config_path(), 'r') as fp:
        return json.loads(json.load(fp))


def get_base_config_dir() -> str:
    base_config_dir = os.environ["HOME"]
    if os.getenv("XDG_CONFIG_HOME"):
        base_config_dir = os.getenv("XDG_CONFIG_HOME")

    return join(base_config_dir, ".localconfig", "configstore")


def get_config_path() -> str:
    return join(get_base_config_dir(), 'yabai-window-utils.json')


def create_config_dir(name):
    base_config_dir = get_base_config_dir()

    if not os.path.exists(base_config_dir):
        os.makedirs(base_config_dir, 0o777)
