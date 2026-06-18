# SPDX-FileCopyrightText: Xavier Loux (BleuRaven)
#
# SPDX-License-Identifier: GPL-3.0-or-later

# ----------------------------------------------
#  Blender For UnrealEngine
#  https://github.com/xavier150/Blender-For-UnrealEngine-Addons
# ----------------------------------------------


from typing import List
import bpy
from .. import bbpl

def get_preset_values() -> List[str]:
    preset_values: List[str] = [
        ]
    return preset_values




def get_scene_collection_properties_expanded(scene: bpy.types.Scene) -> bool:
    return scene.bfu_collection_properties_expanded.is_expanded()  # type: ignore

def get_collection_export_folder_name(col: bpy.types.Collection) -> str:
    return col.bfu_export_folder_name  # type: ignore

# -------------------------------------------------------------------
#   Register & Unregister
# -------------------------------------------------------------------

classes = (
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.Scene.bfu_collection_properties_expanded = bbpl.blender_layout.layout_accordion.add_ui_accordion(name="Collection Properties") # type: ignore
    
    bpy.types.Collection.bfu_export_folder_name = bpy.props.StringProperty( # type: ignore
        name="Sub folder name",
        description=(
            'The name of sub folder.' +
            ' You can now use ../ for up one directory.'
            ),
        override={'LIBRARY_OVERRIDABLE'},
        maxlen=64,
        default="",
        subtype='FILE_NAME'
        )


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)

    del bpy.types.Collection.bfu_export_folder_name # type: ignore
    del bpy.types.Scene.bfu_collection_properties_expanded # type: ignore