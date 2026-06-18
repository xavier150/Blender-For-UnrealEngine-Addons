# SPDX-FileCopyrightText: Xavier Loux (BleuRaven)
#
# SPDX-License-Identifier: GPL-3.0-or-later

# ----------------------------------------------
#  Blender For UnrealEngine
#  https://github.com/xavier150/Blender-For-UnrealEngine-Addons
# ----------------------------------------------


from typing import List, Tuple
import bpy
from enum import Enum
from .. import bbpl

''' Example of usage:
class BFU_AlembicExportProcedure(str, Enum):
    STANDARD_ALEMBIC = "standard_alembic"

    @staticmethod
    def default() -> "BFU_AlembicExportProcedure":
        return BFU_AlembicExportProcedure.STANDARD_ALEMBIC

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

'''

class BFU_VertexColorImportOptionEnum(str, Enum):
    IGNORE = "IGNORE"
    OVERRIDE = "OVERRIDE"
    REPLACE = "REPLACE"

    @staticmethod
    def default() -> "BFU_VertexColorImportOptionEnum":
        return BFU_VertexColorImportOptionEnum.REPLACE

    @classmethod
    def _missing_(cls, value: object) -> "BFU_VertexColorImportOptionEnum":
        # Fallback for old scenes/transient states with empty or invalid value.
        return cls.default()
    
def get_vertex_color_import_option_enum_property_list() -> List[Tuple[str, str, str, str, int]]:
    return [
        (BFU_VertexColorImportOptionEnum.IGNORE.value,
            "Ignore",
            "Ignore vertex colors, and keep the existing mesh vertex colors.",
            "OUTLINER_OB_FONT",
            1),
        (BFU_VertexColorImportOptionEnum.OVERRIDE.value,
            "Override",
            "Override all vertex colors with the specified color.",
            "OUTLINER_OB_FONT",
            2),
        (BFU_VertexColorImportOptionEnum.REPLACE.value,
            "Replace",
            "Import the static mesh using the target vertex colors.",
            "OUTLINER_OB_FONT",
            0),
        ]

def get_default_vertex_color_import_option() -> str:
    return BFU_VertexColorImportOptionEnum.default().value

class BFU_VertexColorToUseEnum(str, Enum):
    FIRST_INDEX = "FirstIndex"
    LAST_INDEX = "LastIndex"
    ACTIVE_INDEX = "ActiveIndex"
    CUSTOM_INDEX = "CustomIndex"

    @staticmethod
    def default() -> "BFU_VertexColorToUseEnum":
        return BFU_VertexColorToUseEnum.ACTIVE_INDEX

    @classmethod
    def _missing_(cls, value: object) -> "BFU_VertexColorToUseEnum":
        # Fallback for old scenes/transient states with empty or invalid value.
        return cls.default()
    
def get_vertex_color_to_use_enum_property_list() -> List[Tuple[str, str, str, str, int]]:
    return [
        (BFU_VertexColorToUseEnum.FIRST_INDEX.value,
            "First Index",
            "Use the the first index in Object Data -> Vertex Color.",
            "OUTLINER_OB_FONT",
            0),
        (BFU_VertexColorToUseEnum.LAST_INDEX.value,
            "Last Index",
            "Use the the last index in Object Data -> Vertex Color.",
            "OUTLINER_OB_FONT",
            1),
        (BFU_VertexColorToUseEnum.ACTIVE_INDEX.value,
            "Active Render",
            "Use the the active index in Object Data -> Vertex Color.",
            "OUTLINER_OB_FONT",
            2),
        (BFU_VertexColorToUseEnum.CUSTOM_INDEX.value,
            "CustomIndex",
            "Use a specific Vertex Color in Object Data -> Vertex Color.",
            "OUTLINER_OB_FONT",
            3),
        ]

def get_default_vertex_color_to_use() -> str:
    return BFU_VertexColorToUseEnum.default().value

def get_preset_values() -> List[str]:
    preset_values = [
            'obj.bfu_vertex_color_import_option',
            'obj.bfu_vertex_color_override_color',
            'obj.bfu_vertex_color_to_use',
            'obj.bfu_vertex_color_index_to_use'
        ]
    return preset_values

def get_scene_object_vertex_color_properties_expanded(scene: bpy.types.Scene) -> bool:
    return scene.bfu_object_vertex_color_properties_expanded.is_expanded()  # type: ignore

def get_object_vertex_color_import_option(obj: bpy.types.Object) -> BFU_VertexColorImportOptionEnum:
    for option in BFU_VertexColorImportOptionEnum:
        if obj.bfu_vertex_color_import_option == option.value:  # type: ignore
            return option
        
    print(f"Warning: Object {obj.name} has unknown export procedure '{obj.bfu_vertex_color_import_option}'. Falling back to default export procedure...")  # type: ignore
    return BFU_VertexColorImportOptionEnum.default()

def get_object_vertex_color_override_color(obj: bpy.types.Object) -> Tuple[float, float, float]:
    return obj.bfu_vertex_color_override_color  # type: ignore

def get_object_vertex_color_to_use(obj: bpy.types.Object) -> BFU_VertexColorToUseEnum:
    for option in BFU_VertexColorToUseEnum:
        if obj.bfu_vertex_color_to_use == option.value:  # type: ignore
            return option
        
    print(f"Warning: Object {obj.name} has unknown vertex color to use '{obj.bfu_vertex_color_to_use}'. Falling back to default...")  # type: ignore
    return BFU_VertexColorToUseEnum.default()

def get_object_vertex_color_index_to_use(obj: bpy.types.Object) -> int:
    return obj.bfu_vertex_color_index_to_use  # type: ignore

def get_object_vertex_color_type(obj: bpy.types.Object) -> str:
    return obj.bfu_vertex_color_type  # type: ignore

# -------------------------------------------------------------------
#   Register & Unregister
# -------------------------------------------------------------------

classes = (

)


# colors_type was added in 3.4 default is SRGB

def register():
    for cls in classes:
        bpy.utils.register_class(cls)


    bpy.types.Scene.bfu_object_vertex_color_properties_expanded = bbpl.blender_layout.layout_accordion.add_ui_accordion(name="Vertex color")  # type: ignore[attr-defined]

    bpy.types.Object.bfu_vertex_color_import_option = bpy.props.EnumProperty(  # type: ignore[attr-defined]
        name="Vertex Color Import Option",
        description="Specify how vertex colors should be imported",
        override={'LIBRARY_OVERRIDABLE'},
        # Vania python
        # https://docs.unrealengine.com/en-US/PythonAPI/class/VertexColorImportOption.html
        # C++ API
        # https://docs.unrealengine.com/en-US/API/Editor/UnrealEd/Factories/EVertexColorImportOption__Type/index.html
        items=[
            ("IGNORE", "Ignore",
                "Ignore vertex colors, and keep the existing mesh vertex colors.", 1),
            ("OVERRIDE", "Override",
                "Override all vertex colors with the specified color.", 2),
            ("REPLACE", "Replace",
                "Import the static mesh using the target vertex colors.", 0)
            ],
        default="REPLACE"
        )

    bpy.types.Object.bfu_vertex_color_override_color = bpy.props.FloatVectorProperty(  # type: ignore[attr-defined]
            name="Vertex Override Color",
            subtype='COLOR',
            description="Specify override color in the case that bfu_vertex_color_import_option is set to Override",
            override={'LIBRARY_OVERRIDABLE'},
            default=(1.0, 1.0, 1.0),
            min=0.0,
            max=1.0
            # Vania python
            # https://docs.unrealengine.com/en-US/PythonAPI/class/FbxSkeletalMeshImportData.html
        )

    bpy.types.Object.bfu_vertex_color_to_use = bpy.props.EnumProperty(  # type: ignore[attr-defined]
        name="Vertex Color to use",
        description="Specify which vertex colors should be imported",
        override={'LIBRARY_OVERRIDABLE'},
        items=get_vertex_color_to_use_enum_property_list(),
        default=get_default_vertex_color_to_use()
        )

    bpy.types.Object.bfu_vertex_color_index_to_use = bpy.props.IntProperty(  # type: ignore[attr-defined]
        name="Vertex color index",
        description="Vertex Color index to use.",
        override={'LIBRARY_OVERRIDABLE'},
        default=0
    )

    bpy.types.Object.bfu_vertex_color_type = bpy.props.EnumProperty(  # type: ignore[attr-defined]
        name="Vertex Color to use",
        description="Target color space",
        override={'LIBRARY_OVERRIDABLE'},
        items=[
            ("SRGB", "sRGB", "Export colors in sRGB color space.", 0),
            ("LINEAR", "Linear", "Export colors in linear color space.", 1)
            ],
        default="SRGB"
        )


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)

    del bpy.types.Object.bfu_vertex_color_type  # type: ignore[attr-defined]
    del bpy.types.Object.bfu_vertex_color_index_to_use  # type: ignore[attr-defined]
    del bpy.types.Object.bfu_vertex_color_to_use  # type: ignore[attr-defined]
    del bpy.types.Object.bfu_vertex_color_override_color  # type: ignore[attr-defined]
    del bpy.types.Object.bfu_vertex_color_import_option  # type: ignore[attr-defined]
    del bpy.types.Scene.bfu_object_vertex_color_properties_expanded  # type: ignore[attr-defined]