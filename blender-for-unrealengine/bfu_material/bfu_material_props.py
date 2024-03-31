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

    # SkeletalMeshImportData:
    # https://api.unrealengine.com/INT/API/Editor/UnrealEd/Factories/UFbxSkeletalMeshImportData/index.html

    # UFbxTextureImportData:
    # https://api.unrealengine.com/INT/API/Editor/UnrealEd/Factories/UFbxTextureImportData/index.html

    bpy.types.Object.bfu_material_search_location = bpy.props.EnumProperty(
        name="Material search location",
        description=(
            "Specify where we should search" +
            " for matching materials when importing"
            ),
        override={'LIBRARY_OVERRIDABLE'},
        # Vania python:
        # https://docs.unrealengine.com/en-US/PythonAPI/class/MaterialSearchLocation.html?highlight=materialsearchlocation
        # C++ API:
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


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)

    del bpy.types.Object.bfu_material_search_location