# SPDX-FileCopyrightText: 2018-2025 Xavier Loux (BleuRaven)
#
# SPDX-License-Identifier: GPL-3.0-or-later

# ----------------------------------------------
#  Blender For UnrealEngine
#  https://github.com/xavier150/Blender-For-UnrealEngine-Addons
# ----------------------------------------------

import bpy
from enum import Enum
from typing import List, Tuple, Dict, Union 
from ..bfu_simple_file_type_enum import BFU_FileTypeEnum

class BFU_SplineExportProcedure(str, Enum):
    ADITIONAL_DATA_ONLY = "additional_data_only"
    STANDARD_FBX = "standard_fbx"
    STANDARD_GLTF = "standard_gltf"

    @staticmethod
    def default() -> "BFU_SplineExportProcedure":
        return BFU_SplineExportProcedure.ADITIONAL_DATA_ONLY

    @classmethod
    def _missing_(cls, value: object) -> "BFU_SplineExportProcedure":
        # Fallback for old scenes/transient states with empty or invalid value.
        return cls.default()

def get_spline_export_procedure_enum_property_list() -> List[Tuple[str, str, str, str, int]]:
    return [
        (BFU_SplineExportProcedure.ADITIONAL_DATA_ONLY.value,
            "Additional Data Only",
            "Export only additional data for spline.",
            "OUTLINER_OB_GROUP_INSTANCE",
            0),
        (BFU_SplineExportProcedure.STANDARD_FBX.value,
            "Blender Standard (FBX)",
            "Standard fbx I/O.",
            "OUTLINER_OB_GROUP_INSTANCE",
            1),
        (BFU_SplineExportProcedure.STANDARD_GLTF.value,
            "Blender Standard (glTF 2.0)",
            "Standard glTF 2.0.",
            "OUTLINER_OB_GROUP_INSTANCE",
            2),
        ]

def get_default_spline_export_procedure() -> str:
    return BFU_SplineExportProcedure.default().value

def get_obj_export_file_type(obj: bpy.types.Object) -> BFU_FileTypeEnum:
    return get_export_file_type(get_object_export_procedure(obj))

def get_export_file_type(procedure: BFU_SplineExportProcedure) -> BFU_FileTypeEnum:
    if procedure == BFU_SplineExportProcedure.STANDARD_FBX:
        return BFU_FileTypeEnum.FBX
    elif procedure == BFU_SplineExportProcedure.STANDARD_GLTF:
        return BFU_FileTypeEnum.GLTF
    else:
        return BFU_FileTypeEnum.UNKNOWN

def get_object_export_additional_data_only(obj: bpy.types.Object) -> bool:
    return get_object_export_procedure(obj).value == BFU_SplineExportProcedure.ADITIONAL_DATA_ONLY.value

def get_object_export_procedure(obj: bpy.types.Object) -> BFU_SplineExportProcedure:
    for procedure in BFU_SplineExportProcedure:
        if getattr(obj, "bfu_spline_export_procedure", None) == procedure.value:
            return procedure

    print(f"Warning: Object {obj.name} has unknown export procedure '{obj.bfu_spline_export_procedure}'. Falling back to default export procedure...")  # type: ignore
    return BFU_SplineExportProcedure.default()

def get_spline_procedure_preset(procedure: BFU_SplineExportProcedure) -> Dict[str, Union[str, bool]]:
    preset: Dict[str, Union[str, bool]] = {}
    return preset

def draw_object_export_procedure(layout: bpy.types.UILayout, obj: bpy.types.Object) -> bpy.types.UILayout:
    layout.prop(obj, 'bfu_spline_export_procedure')  # type: ignore
    return layout

def get_preset_values() -> List[str]:
    preset_values = [
        'obj.bfu_spline_export_procedure',
        ]
    return preset_values

classes = (
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)  # type: ignore

    bpy.types.Object.bfu_spline_export_procedure = bpy.props.EnumProperty(  # type: ignore
        name="Export Procedure",
        description=(
            "This will define how a spline should be exported."
            ),
        override={'LIBRARY_OVERRIDABLE'},
        items=get_spline_export_procedure_enum_property_list(),
        default=get_default_spline_export_procedure()
        )

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)  # type: ignore

    del bpy.types.Object.bfu_spline_export_procedure  # type: ignore