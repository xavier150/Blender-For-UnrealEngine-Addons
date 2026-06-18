# SPDX-FileCopyrightText: Xavier Loux (BleuRaven)
#
# SPDX-License-Identifier: GPL-3.0-or-later

# ----------------------------------------------
#  BBPL -> BleuRaven Blender Python Library
#  https://github.com/xavier150/BBPL
# ----------------------------------------------

import os
import addon_utils
from typing import Tuple
from .. import __internal__


def get_addon_version(addon_name: str) -> Tuple[int, int, int]:
    version = (0, 0, 0)
    for mod in addon_utils.modules():  # type: ignore
        if mod.bl_info['name'] == addon_name:  # type: ignore
            return mod.bl_info.get('version', (0, 0, 0))  # type: ignore
    return version

def get_addon_version_str(addon_name: str) -> str:
    version = get_addon_version(addon_name)
    return '.'.join([str(x) for x in version])

def get_addon_file(addon_name: str) -> str:
    for mod in addon_utils.modules():  # type: ignore
        if mod.bl_info['name'] == addon_name:  # type: ignore
            return mod.__file__  # type: ignore
    return "Not Found"

def get_addon_path(addon_name: str) -> str:
    for mod in addon_utils.modules():  # type: ignore
        if mod.bl_info['name'] == addon_name:  # type: ignore
            return os.path.dirname(mod.__file__)  # type: ignore
    return "Not Found"