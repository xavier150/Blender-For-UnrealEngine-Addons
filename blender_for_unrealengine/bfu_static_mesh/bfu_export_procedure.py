# SPDX-FileCopyrightText: Xavier Loux (BleuRaven)
#
# SPDX-License-Identifier: GPL-3.0-or-later

# ----------------------------------------------
#  Blender For UnrealEngine
#  https://github.com/xavier150/Blender-For-UnrealEngine-Addons
# ----------------------------------------------

import bpy
from typing import List, Tuple, Dict, Union
from enum import Enum
from ..bfu_simple_file_type_enum import BFU_FileTypeEnum

class BFU_StaticExportProcedure(Enum):
    CUSTOM_FBX_EXPORT = "custom_fbx_export"
    STANDARD_FBX = "standard_fbx"
    STANDARD_GLTF = "standard_gltf"

    @staticmethod
    def default() -> "BFU_StaticExportProcedure":
        # For the momment FBX is the default export procedure.
        # But in the future I will change on glTF when fully stable and supported by Unreal Engine.
        # glTF is more modern and open than FBX.
        return BFU_StaticExportProcedure.STANDARD_FBX

def get_blender_default() -> str:
    return BFU_StaticExportProcedure.STANDARD_FBX.value

def get_blender_enum_property_list() -> List[Tuple[str, str, str, str, int]]:
    return [
        (BFU_StaticExportProcedure.CUSTOM_FBX_EXPORT.value,
            "UE Standard (FBX)",
            "Modified fbx I/O for Unreal Engine. (Warning: will be deprecated in the future, use \"(GLTF)\" instead.)",
            "OUTLINER_OB_GROUP_INSTANCE",
            1),
        (BFU_StaticExportProcedure.STANDARD_FBX.value,
            "Blender Standard (FBX)",
            "Standard fbx I/O.",
            "OUTLINER_OB_GROUP_INSTANCE",
            2),
        (BFU_StaticExportProcedure.STANDARD_GLTF.value,
            "Blender Standard (glTF 2.0)",
            "Standard glTF 2.0.",
            "OUTLINER_OB_GROUP_INSTANCE",
            3),
        ]

def get_object_export_procedure(obj: bpy.types.Object) -> BFU_StaticExportProcedure:
    for procedure in BFU_StaticExportProcedure:
        if obj.bfu_static_export_procedure == procedure.value:  # type: ignore
            return procedure

    print(f"Warning: Object {obj.name} has unknown export procedure '{obj.bfu_static_export_procedure}'. Falling back to default export procedure...")  # type: ignore
    return BFU_StaticExportProcedure.default()

def get_obj_export_file_type(obj: bpy.types.Object) -> BFU_FileTypeEnum:
    return get_export_file_type(get_object_export_procedure(obj))

def get_export_file_type(procedure: BFU_StaticExportProcedure) -> BFU_FileTypeEnum: # Object.bfu_static_export_procedure
    if procedure == BFU_StaticExportProcedure.CUSTOM_FBX_EXPORT:
        return BFU_FileTypeEnum.FBX
    elif procedure == BFU_StaticExportProcedure.STANDARD_FBX:
        return BFU_FileTypeEnum.FBX
    elif procedure == BFU_StaticExportProcedure.STANDARD_GLTF:
        return BFU_FileTypeEnum.GLTF

def get_obj_static_fbx_procedure_preset(obj: bpy.types.Object) -> Dict[str, Union[bool, str]]:
    return get_static_fbx_procedure_preset(get_object_export_procedure(obj))

def get_static_fbx_procedure_preset(procedure: BFU_StaticExportProcedure) -> Dict[str, Union[bool, str]]: # Object.bfu_static_export_procedure
    preset: Dict[str, Union[bool, str]] = {}
    if procedure == BFU_StaticExportProcedure.CUSTOM_FBX_EXPORT:
        preset["use_space_transform"]=True
        preset["axis_forward"]='-Z'
        preset["axis_up"]='Y'
        return preset

    else:
        preset["use_space_transform"]=True
        preset["axis_forward"]='-Z'
        preset["axis_up"]='Y'

    return preset

def get_obj_can_edit_scale(obj: bpy.types.Object)-> bool:
    return get_can_edit_scale(get_object_export_procedure(obj))

def get_can_edit_scale(procedure: BFU_StaticExportProcedure)-> bool: # Object.bfu_static_export_procedure
    if procedure == BFU_StaticExportProcedure.STANDARD_GLTF:
        # bpy.ops.export_scene.gltf() don't have global_scale
        return False

    return True

def draw_object_export_procedure(layout: bpy.types.UILayout, obj: bpy.types.Object) -> bpy.types.UILayout:
    layout.prop(obj, 'bfu_static_export_procedure')  # type: ignore
    return layout

def get_preset_values() -> List[str]:
    preset_values = [
        'obj.bfu_static_export_procedure',
        ]
    return preset_values

classes = (
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)  # type: ignore

    bpy.types.Object.bfu_static_export_procedure = bpy.props.EnumProperty( # type: ignore
        name="Export Procedure",
        description=(
            "This will define how a static mesh should be exported."
            ),
        override={'LIBRARY_OVERRIDABLE'},
        items=get_blender_enum_property_list(),
        default=get_blender_default()
        )

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)  # type: ignore

    del bpy.types.Object.bfu_static_export_procedure # type: ignore