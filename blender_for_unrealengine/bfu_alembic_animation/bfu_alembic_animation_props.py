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
    preset_values = [
        'obj.bfu_export_as_alembic_animation',
        'obj.bfu_create_sub_folder_with_alembic_name'
        ]
    return preset_values

def get_scene_object_properties_expanded(scene: bpy.types.Scene) -> bool:
    return scene.bfu_alembic_properties_expanded.is_expanded()  # type: ignore

def get_object_export_as_alembic_animation(obj: bpy.types.Object) -> bool:
    return obj.bfu_export_as_alembic_animation  # type: ignore

def get_object_create_sub_folder_with_alembic_name(obj: bpy.types.Object) -> bool:
    return obj.bfu_create_sub_folder_with_alembic_name  # type: ignore

# -------------------------------------------------------------------
#   Register & Unregister
# -------------------------------------------------------------------

classes = (
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.Scene.bfu_alembic_properties_expanded = bbpl.blender_layout.layout_accordion.add_ui_accordion(name="Alembic")  # type: ignore[attr-defined]

    bpy.types.Object.bfu_export_as_alembic_animation = bpy.props.BoolProperty(  # type: ignore[attr-defined]
        name="Export as Alembic animation",
        description=("If true this mesh will be exported as a Alembic animation"),
        override={'LIBRARY_OVERRIDABLE'},
        default=False
        )
    
    bpy.types.Object.bfu_create_sub_folder_with_alembic_name = bpy.props.BoolProperty(  # type: ignore[attr-defined]
        name="Create Alembic Sub Folder",
        description="Create a subfolder with the Alembic object name to avoid asset conflicts during the export. (Recommended)",
        override={'LIBRARY_OVERRIDABLE'},
        default=True
        )



def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
    
    del bpy.types.Object.bfu_create_sub_folder_with_alembic_name  # type: ignore[attr-defined]
    del bpy.types.Object.bfu_export_as_alembic_animation  # type: ignore[attr-defined]
    del bpy.types.Scene.bfu_alembic_properties_expanded  # type: ignore[attr-defined]