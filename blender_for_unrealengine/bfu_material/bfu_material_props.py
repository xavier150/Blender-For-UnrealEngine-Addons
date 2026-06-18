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
        'obj.bfu_material_search_location'
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

    
    # Export materials (Float color, roughness value, metallic value, etc.)
    bpy.types.Object.bfu_export_materials = bpy.props.BoolProperty(
        name="Export Materials",
        description="Export materials with in the model file, you also need to enable the 'Export Textures' option to export textures.\n" \
        "Work better with glTF file format.",
        default=True
    )

    #export textures (Diffuse map, normal map, roughness map, metallic map, etc.)
    bpy.types.Object.bfu_export_textures = bpy.props.BoolProperty(
        name="Export Textures",
        description="Export textures (Diffuse map, normal map, roughness map, metallic map, etc.) with the file.\n" \
        "Work better with glTF file format.\n" \
        "Note: I recommend to use this option only for the first export to save export time.\n" \
        "Note 2: For animation textures export is disabled by default, check the value 'bfu_export_animation_without_textures'.",
        default=False
    )

    bpy.types.Object.bfu_import_materials = bpy.props.BoolProperty(
        name="Import Materials",
        description="Import materials from the model file when importing in Unreal Engine",
        default=False
    )

    bpy.types.Object.bfu_import_textures = bpy.props.BoolProperty(
        name="Import Textures",
        description="Import textures from the model file when importing in Unreal Engine", 
        default=False
    )

    # Used for set flip_normal_map_green_channel in FbxTextureImportData
    # https://docs.unrealengine.com/5.3/en-US/PythonAPI/class/FbxTextureImportData.html
    bpy.types.Object.bfu_flip_normal_map_green_channel = bpy.props.BoolProperty(
        name="Invert Normal Maps",
        description="This option will cause normal map Y (Green) values to be inverted.",
        default=False
    )

    # Used for set reorder_material_to_fbx_order in FbxMeshImportData
    # https://docs.unrealengine.com/5.3/en-US/PythonAPI/class/FbxMeshImportData.html
    bpy.types.Object.bfu_reorder_material_to_fbx_order = bpy.props.BoolProperty(
        name="Reorder Materials to FBX Order",
        description="If checked, The material list will be reorder to the same order has the FBX file.",
        default=True
    )

    # Used for set material_search_location in FbxTextureImportData
    # https://docs.unrealengine.com/5.3/en-US/PythonAPI/class/FbxTextureImportData.html
    bpy.types.Object.bfu_material_search_location = bpy.props.EnumProperty(
        name="Material Search Location",
        description=(
            "Specify where we should search" +
            " for matching materials when importing"
            ),
        override={'LIBRARY_OVERRIDABLE'},
        # Item list:
        # https://docs.unrealengine.com/en-US/PythonAPI/class/MaterialSearchLocation.html?highlight=materialsearchlocation
        # http://api.unrealengine.com/INT/API/Editor/UnrealEd/Factories/EMaterialSearchLocation/index.html
        items=[
            ("Local",
                "Local",
                "Search for matching material in local import folder only.",
                1),
            ("UnderParent",
                "Under parent",
                "Search for matching material recursively from parent folder.",
                2),
            ("UnderRoot",
                "Under root",
                "Search for matching material recursively from root folder.",
                3),
            ("AllAssets",
                "All assets",
                "Search for matching material in all assets folders.",
                4)
            ]
        )
    
    bpy.types.Scene.bfu_object_material_properties_expanded = bbpl.blender_layout.layout_accordion.add_ui_accordion(name="Material")


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)

    del bpy.types.Object.bfu_material_search_location
    del bpy.types.Object.bfu_reorder_material_to_fbx_order
    del bpy.types.Object.bfu_flip_normal_map_green_channel
    del bpy.types.Object.bfu_import_textures
    del bpy.types.Object.bfu_import_materials
    del bpy.types.Object.bfu_export_textures
    del bpy.types.Object.bfu_export_materials
    
    del bpy.types.Scene.bfu_object_material_properties_expanded