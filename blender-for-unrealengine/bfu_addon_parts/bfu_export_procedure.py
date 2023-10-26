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

from bpy.props import (
        StringProperty,
        BoolProperty,
        EnumProperty,
        IntProperty,
        FloatProperty,
        FloatVectorProperty,
        PointerProperty,
        CollectionProperty,
        )

def get_export_procedure_enum_property_list():
    items=[
        ("ue-standard",
            "UE Standard",
            "Modified fbx I/O for Unreal Engine",
            "ARMATURE_DATA",
            1),
        ("blender-standard",
            "Blender Standard",
            "Standard fbx I/O.",
            "ARMATURE_DATA",
            2),
        ("auto-rig-pro",
            "AutoRigPro",
            "Export using AutoRigPro.",
            "ARMATURE_DATA",
            3),
        ]
    return items

def get_export_procedure_enum_property_default():
    return "blender-standard"

def get_procedure_preset(procedure: str): # Object.bfu_export_procedure
    preset = {}
    if procedure == "ue-standard":
        preset["axis_forward"]='-Z'
        preset["axis_up"]='Y'
        preset["primary_bone_axis"]='X' 
        preset["secondary_bone_axis"]='-Z'

    if procedure == "blender-standard":
        preset["axis_forward"]='-Z'
        preset["axis_up"]='Y'
        preset["primary_bone_axis"]='Y'
        preset["secondary_bone_axis"]='X'

    if procedure == "auto-rig-pro":
        preset["axis_forward"]='-Z'
        preset["axis_up"]='Y'
        preset["primary_bone_axis"]='Y'
        preset["secondary_bone_axis"]='X'

    return preset

def get_procedure_preset_as_text(procedure: str): # Object.bfu_export_procedure
    preset = get_procedure_preset(procedure)  # Obtenez le dictionnaire de preset
    
    # Initialisez une chaîne de caractères vide pour stocker les valeurs
    preset_text = ""

    # Utilisez une boucle pour itérer sur les éléments du dictionnaire
    for key, value in preset.items():
        # Concaténez la clé et la valeur dans la chaîne de caractères
        preset_text += f"{key}: {value}\n"

    return preset_text

classes = (
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.Object.bfu_export_procedure = EnumProperty(
        name="Export procedure",
        description=(
            "This will define how the object should" +
            " be exported in case you are using specific Rig."
            ),
        override={'LIBRARY_OVERRIDABLE'},
        items=get_export_procedure_enum_property_list(),
        default=get_export_procedure_enum_property_default()
        )


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)