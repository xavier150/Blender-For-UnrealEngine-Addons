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
from . import bfu_skeletal_mesh_utils
from .. import bfu_basics
from .. import bfu_utils
from .. import bfu_ui
from .. import bbpl


def draw_general_ui_object(layout: bpy.types.UILayout, obj: bpy.types.Object):
    if obj is None:
        return
    
    if obj.type != "ARMATURE":
        return
    
    scene = bpy.context.scene 
    addon_prefs = bfu_basics.GetAddonPrefs()
    
    if bfu_ui.bfu_ui_utils.DisplayPropertyFilter("OBJECT", "GENERAL"):
        if scene.bfu_object_properties_expanded.is_expend():
            if obj.bfu_export_type == "export_recursive":
                if not obj.bfu_export_as_alembic:
                    AssetType2 = layout.column()
                    # Show asset type
                    AssetType2.prop(obj, "bfu_export_skeletal_mesh_as_static_mesh")

def draw_ui_object(layout: bpy.types.UILayout, obj: bpy.types.Object):
    if obj is None:
        return
    
    if obj.type != "ARMATURE":
        return
    
    scene = bpy.context.scene 
    addon_prefs = bfu_basics.GetAddonPrefs()

    if bfu_ui.bfu_ui_utils.DisplayPropertyFilter("OBJECT", "GENERAL"):
        if scene.bfu_object_properties_expanded.is_expend():

            if bfu_utils.GetAssetType(obj) == "SkeletalMesh":
                scene.bfu_skeleton_properties_expanded.draw(layout)
                if scene.bfu_skeleton_properties_expanded.is_expend():
                    if addon_prefs.useGeneratedScripts and obj is not None:
                        if obj.bfu_export_type == "export_recursive":

                            # SkeletalMesh prop
                            if not obj.bfu_export_as_lod_mesh:
                                AssetType2 = layout.column()
                                AssetType2.prop(obj, 'bfu_create_sub_folder_with_skeletal_mesh_name')
                                AssetType2.prop(obj, 'bfu_export_deform_only')
                                ue_standard_skeleton = layout.column()
                                ue_standard_skeleton.label(text="(ue-standard)")
                                ue_standard_skeleton_props = ue_standard_skeleton.column()
                                ue_standard_skeleton_props.enabled = obj.bfu_skeleton_export_procedure == "ue-standard"
                                ue_standard_skeleton_props.prop(obj, "bfu_export_animation_without_mesh")
                                ue_standard_skeleton_props.prop(obj, "bfu_mirror_symmetry_right_side_bones")
                                mirror_symmetry_right_side_bones = ue_standard_skeleton_props.row()
                                mirror_symmetry_right_side_bones.enabled = obj.bfu_mirror_symmetry_right_side_bones
                                mirror_symmetry_right_side_bones.prop(obj, "bfu_use_ue_mannequin_bone_alignment")

                scene.bfu_modular_skeletal_mesh_properties_expanded.draw(layout)
                if scene.bfu_modular_skeletal_mesh_properties_expanded.is_expend():
                    if obj.bfu_export_type == "export_recursive":

                        # SkeletalMesh prop
                        if not obj.bfu_export_as_lod_mesh:
                            modular_skeletal_mesh = layout.column()
                            modular_skeletal_mesh.prop(obj, "bfu_modular_skeletal_mesh_mode")
                            if obj.bfu_modular_skeletal_mesh_mode == "every_meshs":
                                modular_skeletal_mesh.prop(obj, "bfu_modular_skeletal_mesh_every_meshs_separate")
                            if obj.bfu_modular_skeletal_mesh_mode == "specified_parts":
                                obj.bfu_modular_skeletal_specified_parts_meshs_template.draw(modular_skeletal_mesh)

def draw_ui_scene(layout: bpy.types.UILayout):
    pass