# SPDX-FileCopyrightText: Xavier Loux (BleuRaven)
#
# SPDX-License-Identifier: GPL-3.0-or-later

# ----------------------------------------------
#  BBAM -> BleuRaven Blender Addon Manager
#  https://github.com/xavier150/BBAM
# ----------------------------------------------

import os

from typing import Dict, Any, List
from . import config
from .bbam_addon_config.bbam_addon_config_type import BBAM_AddonConfig, BBAM_AddonBuild


def generate_new_manifest(
    addon_config: BBAM_AddonConfig,
    build_config: BBAM_AddonBuild,
) -> Dict[str, Any]:
    """
    Generates a new manifest dictionary for the addon based on the configuration data.
    """

    data: Dict[str, Any] = {}
    addon_manifest = addon_config.addon_manifest

    # Populate generic information
    data["schema_version"] = config.manifest_schema_version
    data["version"] = addon_manifest.get_version_as_string()
    data["id"] = addon_manifest.addon_id
    data["name"] = addon_manifest.addon_name
    data["tagline"] = addon_manifest.tagline
    data["maintainer"] = addon_manifest.maintainer
    data["website"] = addon_manifest.website_url
    data["type"] = addon_manifest.type.get_as_string()
    data["tags"] = addon_manifest.tags
    data["blender_version_min"] = build_config.get_min_blender_version_as_string()
    data["license"] = addon_manifest.license
    data["copyright"] = addon_manifest.copyright

    if len(addon_manifest.permissions) > 0:
        data["permissions"] = addon_manifest.permissions
    return data

def dump_list(value_list: List[str]) -> str:
    """
    Formats a list to display each item on a new line in the TOML output.

    Parameters:
        v (list): The list to format for multi-line display.

    Returns:
        str: A formatted multi-line string representation of the list.
    """
    output = "[\n"
    for item in value_list:
        output += f"  \"{str(item)}\",\n"  # Indent each item and escape as a string
    output += "]"
    return output

def dict_to_toml(data: Dict[str, Any]) -> str:
    """
    Convert a dictionary to a TOML-formatted string.

    Parameters:
        data (dict): The dictionary to format.

    Returns:
        str: A TOML-formatted string representation of the dictionary.
    """
    toml_string = ""
    for key, value in data.items():
        if isinstance(value, dict):
            toml_string += f"[{key}]\n" + dict_to_toml(value)  # type: ignore # Recursive call for nested dictionaries
        elif isinstance(value, list):
            toml_string += f"{key} = {dump_list(value)}\n"  # type: ignore
        elif isinstance(value, str):
            toml_string += f"{key} = \"{value}\"\n"  # Add quotes for strings
        else:
            toml_string += f"{key} = {value}\n"
    return toml_string

def save_addon_manifest(
    addon_path: str,
    data: Dict[str, Any],
    show_debug: bool = False
):
    """
    Saves the addon manifest as a TOML file manually.

    Parameters:
        addon_path (str): Path to the addon's root folder.
        data (dict): Manifest data to save as a TOML file.
        show_debug (bool): If True, displays debug information about the save process.
    """
    addon_manifest_path = os.path.join(addon_path, config.blender_manifest)

    # Generate TOML content manually
    toml_content = dict_to_toml(data)

    # Save to file
    with open(addon_manifest_path, "w") as file:
        file.write(toml_content)

    if show_debug:
        print(f"Addon manifest saved successfully at: {addon_manifest_path}")