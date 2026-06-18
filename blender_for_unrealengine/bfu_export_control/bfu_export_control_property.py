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
            "Export with the parent if the parents is \"Export recursive\"",
            "BOIDS",
            1),
        (BFU_ExportTypeEnum.EXPORT_RECURSIVE.value,
            "Export recursive",
            "Export self object and all children",
            "KEYINGSET",
            2),
        (BFU_ExportTypeEnum.DONT_EXPORT.value,
            "Not exported",
            "Will never export",
            "CANCEL",
            3),
        ]


classes = (
)


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