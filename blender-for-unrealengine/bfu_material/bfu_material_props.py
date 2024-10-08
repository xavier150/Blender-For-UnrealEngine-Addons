# ====================== BEGIN GPL LICENSE BLOCK ============================
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.	 See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.	 If not, see <http://www.gnu.org/licenses/>.
#  All rights reserved.
#
# ======================= END GPL LICENSE BLOCK =============================


import bpy
from . import bfu_material_utils
from .. import bfu_basics
from .. import bfu_utils
from .. import bfu_ui
from .. import bbpl

def get_preset_values():
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

    
    # Used for set import_materials in FbxImportUI
    # https://docs.unrealengine.com/5.3/en-US/PythonAPI/class/FbxImportUI.html
    bpy.types.Object.bfu_import_materials = bpy.props.BoolProperty(
        name="Import Materials",
        description="Whether to import materials from the FBX file.",
        default=True  # Modifier selon le comportement par défaut souhaité
    )

    # Used for set import_textures in FbxImportUI
    # https://docs.unrealengine.com/5.3/en-US/PythonAPI/class/FbxImportUI.html
    bpy.types.Object.bfu_import_textures = bpy.props.BoolProperty(
        name="Import Textures",
        description="Whether to import textures from the FBX file.",
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
    
    del bpy.types.Scene.bfu_object_material_properties_expanded