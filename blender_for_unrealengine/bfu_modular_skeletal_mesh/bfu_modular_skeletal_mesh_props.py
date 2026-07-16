# SPDX-FileCopyrightText: Xavier Loux (BleuRaven)
#
# SPDX-License-Identifier: GPL-3.0-or-later

# ----------------------------------------------
#  Blender For UnrealEngine
#  https://github.com/xavier150/Blender-For-UnrealEngine-Addons
# ----------------------------------------------


from enum import Enum
from typing import List, Tuple
import bpy
from .. import bbpl


class BFU_ModularSkeletalMeshModeEnum(str, Enum):
    ALL_IN_ONE = "all_in_one"
    EVERY_MESHS = "every_meshs"
    SPECIFIED_PARTS = "specified_parts"

    def is_all_in_one(self) -> bool:
        return self.value == BFU_ModularSkeletalMeshModeEnum.ALL_IN_ONE.value
    
    def is_every_meshs(self) -> bool:
        return self.value == BFU_ModularSkeletalMeshModeEnum.EVERY_MESHS.value
    
    def is_specified_parts(self) -> bool:
        return self.value == BFU_ModularSkeletalMeshModeEnum.SPECIFIED_PARTS.value

    @staticmethod
    def default() -> "BFU_ModularSkeletalMeshModeEnum":
        return BFU_ModularSkeletalMeshModeEnum.ALL_IN_ONE

    @classmethod
    def _missing_(cls, value: object) -> "BFU_ModularSkeletalMeshModeEnum":
        # Fallback for old scenes/transient states with empty or invalid value.
        return cls.default()


def get_modular_skeletal_mesh_mode_enum_list() -> List[Tuple[str, str, str, int]]:
    return [
        (BFU_ModularSkeletalMeshModeEnum.ALL_IN_ONE.value,
            "All In One",
            "Export a single skeletal mesh for the armature and all child meshes.",
            1),
        (BFU_ModularSkeletalMeshModeEnum.EVERY_MESHS.value,
            "Every Meshs",
            "Export a skeletal mesh per every mesh that child of the armature.",
            2),
        (BFU_ModularSkeletalMeshModeEnum.SPECIFIED_PARTS.value,
            "Specified Parts",
            "Export a skeletal mesh for every specified parts. A specified part can contain multiple objects or collections.",
            3),
    ]


def get_default_modular_skeletal_mesh_mode_enum() -> str:
    return BFU_ModularSkeletalMeshModeEnum.default().value


def get_preset_values() -> List[str]:
    preset_values = [
        'obj.bfu_modular_skeletal_mesh_mode',
        'obj.bfu_modular_skeletal_mesh_every_meshs_separate',
        'obj.bfu_modular_skeletal_specified_parts_meshs_template'
        ]
    return preset_values

def get_object_lod_properties_expanded(obj: bpy.types.Object) -> bool:
    return obj.bfu_lod_properties_expanded # type: ignore

def get_object_modular_skeletal_mesh_every_meshs_separate(obj: bpy.types.Object) -> str:
    return obj.bfu_modular_skeletal_mesh_every_meshs_separate # type: ignore

def get_object_modular_skeletal_mesh_mode_enum(obj: bpy.types.Object) -> BFU_ModularSkeletalMeshModeEnum:
    return BFU_ModularSkeletalMeshModeEnum(obj.bfu_modular_skeletal_mesh_mode)  # type: ignore

# -------------------------------------------------------------------
#   Register & Unregister
# -------------------------------------------------------------------

classes = (
)



def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.Scene.bfu_modular_skeletal_mesh_properties_expanded = bbpl.blender_layout.layout_accordion.add_ui_accordion(name="Modular Skeletal Mesh") # type: ignore

    bpy.types.Object.bfu_modular_skeletal_mesh_mode = bpy.props.EnumProperty( # type: ignore
        name="Modular Skeletal Mesh Mode",
        description='Modular skeletal mesh mode',
        override={'LIBRARY_OVERRIDABLE'},
        items=get_modular_skeletal_mesh_mode_enum_list(),
        default=get_default_modular_skeletal_mesh_mode_enum()
        )
    
    bpy.types.Object.bfu_modular_skeletal_mesh_every_meshs_separate = bpy.props.StringProperty( # type: ignore
        name="Separate string",
        description="String between armature name and mesh name",
        override={'LIBRARY_OVERRIDABLE'},
        default="_"
        )


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)

    del bpy.types.Scene.bfu_modular_skeletal_mesh_properties_expanded # type: ignore
    del bpy.types.Object.bfu_modular_skeletal_mesh_every_meshs_separate # type: ignore
    del bpy.types.Object.bfu_modular_skeletal_mesh_mode # type: ignore