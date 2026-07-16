# SPDX-FileCopyrightText: Xavier Loux (BleuRaven)
#
# SPDX-License-Identifier: GPL-3.0-or-later

# ----------------------------------------------
#  Blender For UnrealEngine
#  https://github.com/xavier150/Blender-For-UnrealEngine-Addons
# ----------------------------------------------

import bpy
from typing import List, Tuple
from .bfu_export_control_type import BFU_ExportTypeEnum


def get_blender_default() -> str:
    return BFU_ExportTypeEnum.default().value

def get_blender_enum_property_list() -> List[Tuple[str, str, str, str, int]]:
    return [
        (BFU_ExportTypeEnum.AUTO.value,
            "Auto",
            "Export if has a parent that is \"Export Recursive\".",
            "BOIDS",
            1),
        (BFU_ExportTypeEnum.EXPORT_RECURSIVE.value,
            "Export Recursive",
            "Export self object and all children.",
            "KEYINGSET",
            2),
        (BFU_ExportTypeEnum.EXPORT_SELF_ONLY.value,
            "Export Self Only",
            "Export self object only.",
            "KEYINGSET",
            4), # 4 to keep enum order with the previous version of the addon
        (BFU_ExportTypeEnum.DONT_EXPORT.value,
            "Not Exported",
            "Will never export.",
            "CANCEL",
            3)
        ]


classes = (
)

def set_object_export_type(obj: bpy.types.Object, export_type: BFU_ExportTypeEnum) -> None:
    """
    Set the object export type.
    """
    obj.bfu_export_type = export_type.value  # type: ignore

def get_object_export_type(obj: bpy.types.Object) -> BFU_ExportTypeEnum:
    return BFU_ExportTypeEnum(obj.bfu_export_type)  # type: ignore

def register():
    for cls in classes:
        bpy.utils.register_class(cls)  # type: ignore

    bpy.types.Object.bfu_export_type = bpy.props.EnumProperty(  # type: ignore
        name="Export type",
        description="Export procedure",
        override={'LIBRARY_OVERRIDABLE'},
        items=get_blender_enum_property_list(),
        default=get_blender_default(),
        )

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)  # type: ignore

    del bpy.types.Object.bfu_export_type # type: ignore