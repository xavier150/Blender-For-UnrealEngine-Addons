# SPDX-FileCopyrightText: Xavier Loux (BleuRaven)
#
# SPDX-License-Identifier: GPL-3.0-or-later

# ----------------------------------------------
#  Blender For UnrealEngine
#  https://github.com/xavier150/Blender-For-UnrealEngine-Addons
# ----------------------------------------------

import os
import bpy
import datetime
import json
from typing import Dict, Any
from pathlib import Path
from .. import bbpl
from .. import bfu_utils


def add_generated_json_header(json_data: Dict[str, Any], text: str):

    json_data['comment'] = {
        '1/3': bpy.app.translations.pgettext("This file was generated with the addons Blender for UnrealEngine : https://github.com/xavier150/Blender-For-UnrealEngine-Addons", "interface.write_text_additional_track_start"),
        '2/3': text,
        '3/3': bpy.app.translations.pgettext("The script must be used in Unreal Engine Editor with Python plugins : https://docs.unrealengine.com/en-US/Engine/Editor/ScriptingAndAutomation/Python", "interface.write_text_additional_track_end"),
    }

def add_generated_json_footer(json_data: Dict[str, Any]):
    # Empty for the momment.
    pass

def add_generated_json_meta_data(json_data: Dict[str, Any]):

    current_datetime = datetime.datetime.now()
    current_datetime_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    timestamp = int(current_datetime.timestamp())

    blender_file_path = bpy.data.filepath

    import_module_path: Path = Path("unknown")
    if bpy.app.version >= (4, 2, 0):
        version_str = 'Version '+ str(bbpl.blender_extension.extension_utils.get_package_version())
        addon_path = bbpl.blender_extension.extension_utils.get_package_path()
        if addon_path:
            import_module_path = Path(addon_path) / "bfu_import_module"
    else:
        version_str = 'Version '+ bbpl.blender_addon.addon_utils.get_addon_version_str("Unreal Engine Assets Exporter")
        addon_path = bbpl.blender_addon.addon_utils.get_addon_path("Unreal Engine Assets Exporter")
        if addon_path:
            import_module_path = Path(addon_path) / "bfu_import_module"
    
    


    json_data['info'] = {
        'date_time_str': current_datetime_str,
        "timestamp": timestamp,
        "blender_file": blender_file_path,
        'addon_version': version_str,
        'addon_path': addon_path,
        'import_module_path': str(import_module_path),
    }

def is_read_only(filepath: Path) -> bool:
    return filepath.exists() and not os.access(filepath, os.W_OK)

def export_single_text_file(text: str, fullpath: Path):

    if not bfu_utils.check_and_make_export_path(fullpath):
        print(f"Cannot write to '{fullpath}': Path is invalid.")
        return

    if is_read_only(fullpath):
        print(f"Cannot write to '{fullpath}': File is read-only.")
        return

    print(f"Writing text file to: {fullpath}")
    with open(fullpath, "w") as file:
        file.write(text)
        

def export_single_json_file(json_data: Dict[str, Any], fullpath: Path) -> bool:

    if not bfu_utils.check_and_make_export_path(fullpath):
        print(f"Cannot write to '{fullpath}': Path is invalid.")
        return False

    if is_read_only(fullpath):
        print(f"Cannot write to '{fullpath}': File is read-only.")
        return False

    with open(fullpath, 'w') as json_file:
        json.dump(json_data, json_file, ensure_ascii=False, sort_keys=False, indent=4)
    return True
    return True
