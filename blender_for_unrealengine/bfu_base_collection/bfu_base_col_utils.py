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
from . import bfu_base_col_props


def get_col_import_location(col: bpy.types.Collection) -> Path:
    """Get the path to import a collection into Unreal Engine."""

    export_folder_name = bfu_base_col_props.get_collection_export_folder_name(col)
    return bfu_export_nomenclature.bfu_export_nomenclature_utils.get_import_location() / bfu_basics.valid_folder_name(export_folder_name)

def get_col_export_folder(col: bpy.types.Collection) -> str:
    """Get the export folder name for a collection."""
    
    export_folder_name = bfu_base_col_props.get_collection_export_folder_name(col)
    return bfu_basics.valid_folder_name(export_folder_name)

