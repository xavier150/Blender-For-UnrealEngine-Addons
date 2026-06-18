# SPDX-FileCopyrightText: Xavier Loux (BleuRaven)
#
# SPDX-License-Identifier: GPL-3.0-or-later

# ----------------------------------------------
#  Blender For UnrealEngine
#  https://github.com/xavier150/Blender-For-UnrealEngine-Addons
# ----------------------------------------------

import bpy
from pathlib import Path
from .. import bfu_basics
from .. import bfu_export_nomenclature

def get_import_location()-> Path:
    """Get the path to import assets into Unreal Engine."""
    
    scene = bpy.context.scene
    if scene is None:
        raise ValueError("No active scene found.")

    unreal_import_module = bfu_export_nomenclature.bfu_export_nomenclature_props.get_unreal_import_module(scene)
    unreal_import_location = bfu_export_nomenclature.bfu_export_nomenclature_props.get_unreal_import_location(scene)
#

    unreal_import_module = bfu_basics.valid_folder_name(unreal_import_module)
    unreal_import_location = bfu_basics.valid_folder_name(unreal_import_location)
    return Path(unreal_import_module) / unreal_import_location



