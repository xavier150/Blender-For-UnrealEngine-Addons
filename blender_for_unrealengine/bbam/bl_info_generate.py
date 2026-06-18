# SPDX-FileCopyrightText: Xavier Loux (BleuRaven)
#
# SPDX-License-Identifier: GPL-3.0-or-later

# ----------------------------------------------
#  BBAM -> BleuRaven Blender Addon Manager
#  https://github.com/xavier150/BBAM
# ----------------------------------------------

import os
from typing import Dict, Any, List
from . import utils
from .bbam_addon_config.bbam_addon_config_type import BBAM_AddonConfig, BBAM_AddonBuild



def generate_new_bl_info(
    addon_config: BBAM_AddonConfig,
    build_config: BBAM_AddonBuild,
):
    """
    Generates a new `bl_info` dictionary for the addon based on the configuration data.
    """
    addon_manifest = addon_config.addon_manifest

    # Populate `bl_info` with addon details
    data: Dict[str, Any] = {
        'name': addon_manifest.addon_name,
        'author': addon_manifest.maintainer,
        'version': tuple(addon_manifest.addon_version),
        'blender': tuple(build_config.blender_version_min),
        'location': 'View3D > UI > Unreal Engine',
        'description': addon_manifest.tagline,
        'warning': '',
        "wiki_url": addon_manifest.website_url,
        'tracker_url': addon_manifest.report_issue_url,
        'support': addon_manifest.support,
        'category': addon_manifest.category
    }

    return data

def format_bl_info_lines(data: Dict[str, Any]) -> List[str]:
    # Format the new `bl_info` dictionary with line breaks and indentation
    new_bl_info_lines = ["bl_info = {"]
    items = list(data.items())
    for i, (key, value) in enumerate(items):
        if i < len(items) - 1:
            new_bl_info_lines.append(f"    '{key}': {repr(value)},")
        else:
            new_bl_info_lines.append(f"    '{key}': {repr(value)}")
    new_bl_info_lines.append("}\n")  # Close `bl_info` and add an extra line break for readability
    return new_bl_info_lines

def update_file_bl_info(
    addon_path: str,
    data: Dict[str, Any],
    show_debug: bool = False
):
    """
    Updates the `bl_info` dictionary in the addon's __init__.py file with new data.

    Parameters:
        addon_path (str): Path to the addon's root folder.
        data (dict): New `bl_info` dictionary to update in the file.
        show_debug (bool): If True, displays debug information about the update process.
    """
    addon_init_file_path = os.path.join(addon_path, "__init__.py")

    result = replace_file_bl_info(addon_init_file_path, data)
    if result is False:
        result = add_new_bl_info(addon_init_file_path, data)

    if result is False:
        utils.print_red(f"Failed to replace or add bl_info! File: {addon_init_file_path}")
    
    if search_file_bl_info(addon_init_file_path):
        if show_debug:
            print(f"Addon bl_info successfully updated at: {addon_init_file_path}")
            return
    else:
        utils.print_red(f"Failed to found bl_info after update!: {addon_init_file_path}")



def search_file_bl_info(
    file_path: str
):
    import re
    
    with open(file_path, "r") as file:
        content = file.read()

    # Search for bl_info definition with any indentation using regex
    pattern = r'^\s*bl_info\s*='
    if re.search(pattern, content, re.MULTILINE):
        return True
    return False

def replace_file_bl_info(
    file_path: str, 
    data: Dict[str, Any]
) -> bool:
    import re
    
    with open(file_path, "r") as file:
        lines = file.readlines()

    # Find bl_info definition with any indentation
    start_bl_info = None
    end_bl_info = None
    bl_info_indentation = ""
    
    for i, line in enumerate(lines):
        # Match 'bl_info =' with any amount of whitespace before it
        match = re.match(r'^(\s*)bl_info\s*=', line)
        if match:
            start_bl_info = i
            bl_info_indentation = match.group(1)  # Capture the indentation
            
            # Find the end of the bl_info dictionary
            brace_count = 0
            in_bl_info = False
            for j in range(i, len(lines)):
                line_content = lines[j]
                for char in line_content:
                    if char == '{':
                        brace_count += 1
                        in_bl_info = True
                    elif char == '}' and in_bl_info:
                        brace_count -= 1
                        if brace_count == 0:
                            end_bl_info = j + 1
                            break
                if end_bl_info is not None:
                    break
            break

    if start_bl_info is not None and end_bl_info is not None:
        # Remove the existing `bl_info` block
        del lines[start_bl_info:end_bl_info]
        
        # Format new bl_info with the same indentation
        new_bl_info_lines: List[str] = []
        bl_info_data = format_bl_info_lines(data)
        
        for bl_info_line in bl_info_data:
            if bl_info_line.strip():  # If line is not empty
                new_bl_info_lines.append(bl_info_indentation + bl_info_line + "\n")
            else:
                new_bl_info_lines.append("\n")
        
        # Insert the new `bl_info` block at the same position
        for i, line in enumerate(new_bl_info_lines):
            lines.insert(start_bl_info + i, line)

        # Write the updated content back to the file
        with open(file_path, "w") as file:
            file.writelines(lines)
        return True
    return False

def add_new_bl_info(
    file_path: str,
    data: Dict[str, Any]
) -> bool:
    
    with open(file_path, "r") as file:
        lines = file.readlines()

    # Find the first executable line (import, try, function call, etc.)
    # Skip comments, empty lines, and docstrings
    insert_index = 0
    i = 0
    
    while i < len(lines):
        stripped_line = lines[i].strip()
        
        # Skip empty lines and single-line comments
        if not stripped_line or stripped_line.startswith('#'):
            i += 1
            continue
        
        # Handle docstrings at the beginning (triple quotes)
        if stripped_line.startswith('"""') or stripped_line.startswith("'''"):
            quote_type = '"""' if stripped_line.startswith('"""') else "'''"
            
            # Check if it's a single line docstring
            if stripped_line.count(quote_type) >= 2 and len(stripped_line) > len(quote_type):
                # Single line docstring, skip it
                i += 1
                continue
            else:
                # Multi-line docstring, find the end
                i += 1  # Move to next line
                while i < len(lines):
                    if quote_type in lines[i]:
                        i += 1  # Skip the closing line
                        break
                    i += 1
                continue
        
        # This is the first executable line
        insert_index = i
        break

    # Format bl_info without indentation (at root level)
    new_bl_info_lines: List[str] = []
    bl_info_data = format_bl_info_lines(data)
    
    for bl_info_line in bl_info_data:
        new_bl_info_lines.append(bl_info_line + "\n")
    
    # Add an extra empty line after bl_info for readability
    new_bl_info_lines.append("\n")
    
    # Insert `bl_info` lines at the determined position
    for i, line in enumerate(new_bl_info_lines):
        lines.insert(insert_index + i, line)

    # Write the updated content back to the file
    with open(file_path, "w") as file:
        file.writelines(lines)
    return True