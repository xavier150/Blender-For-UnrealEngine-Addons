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


class BFU_MaterialSearchLocationEnum(str, Enum):
    LOCAL = "Local"
    UNDER_PARENT = "UnderParent"
    UNDER_ROOT = "UnderRoot"
    ALL_ASSETS = "AllAssets"

    @staticmethod
    def default() -> "BFU_MaterialSearchLocationEnum":
        return BFU_MaterialSearchLocationEnum.LOCAL

    @classmethod
    def _missing_(cls, value: object) -> "BFU_MaterialSearchLocationEnum":
        # Fallback for old scenes/transient states with empty or invalid value.
        return cls.default()


def get_material_search_location_enum_list() -> List[Tuple[str, str, str, int]]:
    return [
        (BFU_MaterialSearchLocationEnum.LOCAL.value,
            "Local",
            "Search for matching material in local import folder only.",
            1),
        (BFU_MaterialSearchLocationEnum.UNDER_PARENT.value,
            "Under parent",
            "Search for matching material recursively from parent folder.",
            2),
        (BFU_MaterialSearchLocationEnum.UNDER_ROOT.value,
            "Under root",
            "Search for matching material recursively from root folder.",
            3),
        (BFU_MaterialSearchLocationEnum.ALL_ASSETS.value,
            "All assets",
            "Search for matching material in all assets folders.",
            4),
    ]


def get_default_material_search_location_enum() -> str:
    return BFU_MaterialSearchLocationEnum.default().value


def get_preset_values() -> List[str]:
    preset_values: List[str] = [
        'obj.bfu_export_materials',
        'obj.bfu_export_textures',
        'obj.bfu_import_materials',
        'obj.bfu_import_textures',
        'obj.bfu_flip_normal_map_green_channel',
        'obj.bfu_reorder_material_to_fbx_order',
        'obj.bfu_material_search_location'
        ]
    return preset_values


def get_object_export_materials(obj: bpy.types.Object) -> bool:
    return obj.bfu_export_materials   # type: ignore

def get_object_export_textures(obj: bpy.types.Object) -> bool:
    return obj.bfu_export_textures   # type: ignore

def get_object_import_materials(obj: bpy.types.Object) -> bool:
    return obj.bfu_import_materials   # type: ignore

def get_object_import_textures(obj: bpy.types.Object) -> bool:
    return obj.bfu_import_textures  # type: ignore

def get_object_flip_normal_map_green_channel(obj: bpy.types.Object) -> bool:
    return obj.bfu_flip_normal_map_green_channel  # type: ignore

def get_reorder_material_to_fbx_order(obj: bpy.types.Object) -> bool:
    return obj.bfu_reorder_material_to_fbx_order  # type: ignore

def get_object_material_search_location_enum(obj: bpy.types.Object) -> BFU_MaterialSearchLocationEnum:
    return BFU_MaterialSearchLocationEnum(obj.bfu_material_search_location)  # type: ignore


# -------------------------------------------------------------------
#   Register & Unregister
# -------------------------------------------------------------------

classes = (
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.Scene.bfu_object_material_properties_expanded = bbpl.blender_layout.layout_accordion.add_ui_accordion(name="Material")  # type: ignore
    
    # Export materials (Float color, roughness value, metallic value, etc.)
    bpy.types.Object.bfu_export_materials = bpy.props.BoolProperty(  # type: ignore
        name="Export Materials",
        description="Export materials with in the model file, you also need to enable the 'Export Textures' option to export textures.\n" \
        "Work better with glTF file format.",
        default=True
    )

    #export textures (Diffuse map, normal map, roughness map, metallic map, etc.)
    bpy.types.Object.bfu_export_textures = bpy.props.BoolProperty(  # type: ignore
        name="Export Textures",
        description="Export textures (Diffuse map, normal map, roughness map, metallic map, etc.) with the file.\n" \
        "Work better with glTF file format.\n" \
        "Note: I recommend to use this option only for the first export to save export time.\n" \
        "Note 2: For animation textures export is disabled by default, check the value 'bfu_export_animation_without_textures'.",
        default=False
    )

    bpy.types.Object.bfu_import_materials = bpy.props.BoolProperty(  # type: ignore
        name="Import Materials",
        description="Import materials from the model file when importing in Unreal Engine",
        default=False
    )

    bpy.types.Object.bfu_import_textures = bpy.props.BoolProperty(  # type: ignore
        name="Import Textures",
        description="Import textures from the model file when importing in Unreal Engine", 
        default=False
    )

    # Used for set flip_normal_map_green_channel in FbxTextureImportData
    # https://docs.unrealengine.com/5.3/en-US/PythonAPI/class/FbxTextureImportData.html
    bpy.types.Object.bfu_flip_normal_map_green_channel = bpy.props.BoolProperty(  # type: ignore
        name="Invert Normal Maps",
        description="This option will cause normal map Y (Green) values to be inverted.",
        default=False
    )

    # Used for set reorder_material_to_fbx_order in FbxMeshImportData
    # https://docs.unrealengine.com/5.3/en-US/PythonAPI/class/FbxMeshImportData.html
    bpy.types.Object.bfu_reorder_material_to_fbx_order = bpy.props.BoolProperty(  # type: ignore
        name="Reorder Materials to FBX Order",
        description="If checked, The material list will be reorder to the same order has the FBX file.",
        default=True
    )

    # Used for set material_search_location in FbxTextureImportData
    # https://docs.unrealengine.com/5.3/en-US/PythonAPI/class/FbxTextureImportData.html
    bpy.types.Object.bfu_material_search_location = bpy.props.EnumProperty(  # type: ignore
        name="Material Search Location",
        description=(
            "Specify where we should search" +
            " for matching materials when importing"
            ),
        override={'LIBRARY_OVERRIDABLE'},
        items=get_material_search_location_enum_list(),
        default=get_default_material_search_location_enum()
        )
    
def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)

    del bpy.types.Scene.bfu_object_material_properties_expanded  # type: ignore

    del bpy.types.Object.bfu_material_search_location  # type: ignore
    del bpy.types.Object.bfu_reorder_material_to_fbx_order  # type: ignore
    del bpy.types.Object.bfu_flip_normal_map_green_channel  # type: ignore
    del bpy.types.Object.bfu_import_textures  # type: ignore
    del bpy.types.Object.bfu_import_materials  # type: ignore
    del bpy.types.Object.bfu_export_textures  # type: ignore
    del bpy.types.Object.bfu_export_materials  # type: ignore
    
