# SPDX-FileCopyrightText: Xavier Loux (BleuRaven)
#
# SPDX-License-Identifier: GPL-3.0-or-later

# ----------------------------------------------
#  Blender For UnrealEngine
#  https://github.com/xavier150/Blender-For-UnrealEngine-Addons
# ----------------------------------------------

import sys
import json
from pathlib import Path
from typing import Dict, Any
from . import config


def json_load(json_file: object) -> Dict[str, Any]:
    # Changed in Python 3.9: The keyword argument encoding has been removed.
    if sys.version_info >= (3, 9):
        return json.load(json_file)  # type: ignore
    else:
        return json.load(json_file, encoding="utf8")


def json_load_file(json_file_path: Path) -> Dict[str, Any]:
    if sys.version_info[0] < 3:
        with open(json_file_path, "r") as json_file:
            return json_load(json_file)
    else:
        with open(json_file_path, "r", encoding="utf8") as json_file:
            return json_load(json_file)

def print_debug_step(*args: object):
    if config.print_debug_steps:
        print(*args)