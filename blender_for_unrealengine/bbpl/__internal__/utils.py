# SPDX-FileCopyrightText: Xavier Loux (BleuRaven)
#
# SPDX-License-Identifier: GPL-3.0-or-later

# ----------------------------------------------
#  BBPL -> BleuRaven Blender Python Library
#  https://github.com/xavier150/BBPL
# ----------------------------------------------

from typing import List
from ... import __package__ as base_package # type: ignore

def get_package_name() -> str:
    # Before 4.2 __package__ will look like that: 
    # my_blender_addon.bbpl.__internal__

    # After 4.2 __package__ will look like that: 
    # bl_ext.user_default.my_blender_addon.bbpl.__internal__

    if not isinstance(base_package, str):
        return "unknown_package"

    package_name = base_package.split(".")[-1]
    return package_name

def get_reduced_package_name():
    package_name = get_package_name()

    # blender-for-unrealengine -> bdfunr
    # unrealengine_assets_exporter -> unrassexp

    separators = ["-", "_", "."]
    for sep in separators:
        package_name = package_name.replace(sep, " ")
    parts = package_name.split()

    special_reductions = {
        "blender": "bd",
        "for": "f",
        "to": "t",
        "assets": "ass",
        "asset": "as",
    }

    reduced_parts: List[str] = []
    for part in parts:
        reduced_part = special_reductions.get(part, part[:3])
        reduced_parts.append(reduced_part)

    reduced_name = ''.join(reduced_parts).lower()[:12] # Max length is 12
    return reduced_name

def get_operator_class_name(name: str) -> str:
    reduced_package_name = get_reduced_package_name()
    return f"BBPL_OT_{reduced_package_name}_{name}"

def get_data_operator_idname(name: str) -> str:
    reduced_package_name = get_reduced_package_name()
    return f"data.bbpl_{reduced_package_name}_{name}"

def get_object_operator_idname(name: str) -> str:
    reduced_package_name = get_reduced_package_name()
    return f"object.bbpl_{reduced_package_name}_{name}"

def get_scene_operator_idname(name: str) -> str:
    reduced_package_name = get_reduced_package_name()
    return f"scene.bbpl_{reduced_package_name}_{name}"

def get_layout_ui_class_name(name: str) -> str:
    reduced_package_name = get_reduced_package_name()
    return f"BBPL_UI_{reduced_package_name}_{name}"