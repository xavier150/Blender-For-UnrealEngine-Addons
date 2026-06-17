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

class BFU_GroomExportProcedure(str, Enum):
    STANDARD_ALEMBIC = "standard_alembic"

    @staticmethod
    def default() -> "BFU_GroomExportProcedure":
        return BFU_GroomExportProcedure.STANDARD_ALEMBIC

    @classmethod
    def _missing_(cls, value: object) -> "BFU_GroomExportProcedure":
        # Fallback for old scenes/transient states with empty or invalid value.
        return cls.default()

def get_groom_export_procedure_enum_property_list() -> List[Tuple[str, str, str, str, int]]:
    return [
        (BFU_GroomExportProcedure.STANDARD_ALEMBIC.value,
            "Blender Standard",
            "Standard ALEMBIC.",
            "OUTLINER_OB_FONT",
            1),
        ]

def get_default_groom_export_procedure() -> str:
    return BFU_GroomExportProcedure.default().value

def get_obj_export_file_type(obj: bpy.types.Object) -> BFU_FileTypeEnum:
    return get_export_file_type(get_object_export_procedure(obj))

def get_export_file_type(procedure: BFU_GroomExportProcedure) -> BFU_FileTypeEnum:
    return BFU_FileTypeEnum.ALEMBIC

def get_object_export_procedure(obj: bpy.types.Object) -> BFU_GroomExportProcedure:
    for procedure in BFU_GroomExportProcedure:
        if getattr(obj, "bfu_groom_export_procedure", None) == procedure.value:
            return procedure

    print(f"Warning: Object {obj.name} has unknown export procedure '{obj.bfu_groom_export_procedure}'. Falling back to default export procedure...")  # type: ignore
    return BFU_GroomExportProcedure.default()

def get_groom_procedure_preset(procedure: BFU_GroomExportProcedure) -> Dict[str, Union[str, bool]]:
    preset: Dict[str, Union[str, bool]] = {}
    return preset

def draw_object_export_procedure(layout: bpy.types.UILayout, obj: bpy.types.Object) -> bpy.types.UILayout:
    layout.prop(obj, 'bfu_groom_export_procedure')  # type: ignore
    return layout

def get_preset_values() -> List[str]:
    preset_values = [
        'obj.bfu_groom_export_procedure',
        ]
    return preset_values

classes = (
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)  # type: ignore
    
    bpy.types.Object.bfu_groom_export_procedure = bpy.props.EnumProperty(  # type: ignore
        name="Export Procedure",
        description=(
            "This will define how a groom animation should be exported."
            ),
        override={'LIBRARY_OVERRIDABLE'},
        items=get_groom_export_procedure_enum_property_list(),
        default=get_default_groom_export_procedure()
        )

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)  # type: ignore

    del bpy.types.Object.bfu_groom_export_procedure  # type: ignore