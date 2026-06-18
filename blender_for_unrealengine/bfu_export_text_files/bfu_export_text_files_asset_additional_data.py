# SPDX-FileCopyrightText: Xavier Loux (BleuRaven)
#
# SPDX-License-Identifier: GPL-3.0-or-later

# ----------------------------------------------
#  Blender For UnrealEngine
#  https://github.com/xavier150/Blender-For-UnrealEngine-Addons
# ----------------------------------------------

from typing import Dict, Any
from . import bfu_export_text_files_utils
import bpy

def write_additional_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Writes the additional data for a preset to a JSON file.
    :param data: The data to write.
    :return: The additional data as a dictionary.
    """
    asset_additional_data: Dict[str, Any] = {}

    bfu_export_text_files_utils.add_generated_json_header(asset_additional_data, bpy.app.translations.pgettext("It used for import into Unreal Engine all the assets of type StaticMesh, SkeletalMesh, Animation, Pose, Camera, [...]", "interface.write_text_additional_track_all"))
    bfu_export_text_files_utils.add_generated_json_meta_data(asset_additional_data)

    # Defaultsettings
    asset_additional_data['DefaultSettings'] = {}
    
    # Add the preset data
    asset_additional_data.update(data)

    bfu_export_text_files_utils.add_generated_json_footer(asset_additional_data)
    return asset_additional_data
