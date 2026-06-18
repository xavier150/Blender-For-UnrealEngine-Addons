# SPDX-FileCopyrightText: Xavier Loux (BleuRaven)
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

class BFU_AlembicExportProcedure(str, Enum):
    STANDARD_ALEMBIC = "standard_alembic"

    @staticmethod
    def default() -> "BFU_AlembicExportProcedure":
        return BFU_AlembicExportProcedure.STANDARD_ALEMBIC

    @classmethod
    def _missing_(cls, value: object) -> "BFU_AlembicExportProcedure":
        # Fallback for old scenes/transient states with empty or invalid value.
        return cls.default()

def get_alembic_export_procedure_enum_property_list() -> List[Tuple[str, str, str, str, int]]:
    return [
        (BFU_AlembicExportProcedure.STANDARD_ALEMBIC.value,
            "Blender Standard",
            "Standard ALEMBIC.",
            "OUTLINER_OB_FONT",
            1),
        ]

def get_default_alembic_export_procedure() -> str:
    return BFU_AlembicExportProcedure.default().value

def get_obj_export_file_type(obj: bpy.types.Object) -> BFU_FileTypeEnum:
    return get_export_file_type(get_object_export_procedure(obj))

def get_export_file_type(procedure: BFU_AlembicExportProcedure) -> BFU_FileTypeEnum:
    return BFU_FileTypeEnum.ALEMBIC

def get_object_export_procedure(obj: bpy.types.Object) -> BFU_AlembicExportProcedure:
    for procedure in BFU_AlembicExportProcedure:
        if getattr(obj, "bfu_alembic_export_procedure", None) == procedure.value:
            return procedure

    print(f"Warning: Object {obj.name} has unknown export procedure '{obj.bfu_alembic_export_procedure}'. Falling back to default export procedure...")  # type: ignore
    return BFU_AlembicExportProcedure.default()

def get_alembic_procedure_preset(procedure: BFU_AlembicExportProcedure) -> Dict[str, Union[str, bool]]:
    preset: Dict[str, Union[str, bool]] = {}
    return preset

def draw_object_export_procedure(layout: bpy.types.UILayout, obj: bpy.types.Object) -> bpy.types.UILayout:
    layout.prop(obj, 'bfu_alembic_export_procedure')  # type: ignore
    return layout

def get_preset_values() -> List[str]:
    preset_values = [
        'obj.bfu_alembic_export_procedure',
        ]
    return preset_values

classes = (
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)  # type: ignore
    
    bpy.types.Object.bfu_alembic_export_procedure = bpy.props.EnumProperty(  # type: ignore
        name="Export Procedure",
        description=(
            "This will define how an Alembic animation should be exported."
            ),
        override={'LIBRARY_OVERRIDABLE'},
        items=get_alembic_export_procedure_enum_property_list(),
        default=get_default_alembic_export_procedure()
        )

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)  # type: ignore

    del bpy.types.Object.bfu_alembic_export_procedure  # type: ignore