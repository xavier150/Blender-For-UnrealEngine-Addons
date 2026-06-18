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
        'obj.bfu_modular_skeletal_mesh_mode',
        'obj.bfu_modular_skeletal_mesh_every_meshs_separate',
        'obj.bfu_modular_skeletal_specified_parts_meshs_template'
        ]
    return preset_values

# -------------------------------------------------------------------
#   Register & Unregister
# -------------------------------------------------------------------

classes = (
)



def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.Scene.bfu_modular_skeletal_mesh_properties_expanded = bbpl.blender_layout.layout_accordion.add_ui_accordion(name="Modular Skeletal Mesh")

    bpy.types.Object.bfu_modular_skeletal_mesh_mode = bpy.props.EnumProperty(
        name="Modular Skeletal Mesh Mode",
        description='Modular skeletal mesh mode',
        override={'LIBRARY_OVERRIDABLE'},
        items=[
            ("all_in_one",
                "All In One",
                "Export a single skeletal mesh for the armature and all child meshes.",
                1),
            ("every_meshs",
                "Every Meshs",
                "Export a skeletal mesh per every mesh that child of the armature.",
                2),
            ("specified_parts",
                "Specified Parts",
                "Export a skeletal mesh for every specified parts. A specified part can contain multiple objects or collections.",
                3)
            ]
        )
    
    bpy.types.Object.bfu_modular_skeletal_mesh_every_meshs_separate = bpy.props.StringProperty(
        name="Separate string",
        description="String between armature name and mesh name",
        override={'LIBRARY_OVERRIDABLE'},
        default="_"
        )


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)

    del bpy.types.Scene.bfu_modular_skeletal_mesh_properties_expanded
    del bpy.types.Object.bfu_modular_skeletal_mesh_every_meshs_separate
    del bpy.types.Object.bfu_modular_skeletal_mesh_mode