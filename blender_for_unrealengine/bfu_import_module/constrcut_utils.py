# SPDX-FileCopyrightText: Xavier Loux (BleuRaven)
#
# SPDX-License-Identifier: GPL-3.0-or-later

# ----------------------------------------------
#  Blender For UnrealEngine
#  https://github.com/xavier150/Blender-For-UnrealEngine-Addons
# ----------------------------------------------

from typing import Tuple
import unreal

def get_unreal_version() -> Tuple[int, int, int]:
    """Returns the Unreal Engine version as a tuple of (major, minor, patch)."""
    version_info = unreal.SystemLibrary.get_engine_version().split('-')[0]
    major, minor, patch = map(int, version_info.split('.'))
    return (major, minor, patch)

