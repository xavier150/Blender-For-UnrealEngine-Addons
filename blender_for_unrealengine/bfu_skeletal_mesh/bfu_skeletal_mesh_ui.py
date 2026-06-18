# SPDX-FileCopyrightText: Xavier Loux (BleuRaven)
#
# SPDX-License-Identifier: GPL-3.0-or-later

# ----------------------------------------------
#  Blender For UnrealEngine
#  https://github.com/xavier150/Blender-For-UnrealEngine-Addons
# ----------------------------------------------


import bpy
from .. import bfu_ui
from .. import bbpl
from .. import bfu_export_control
from .. import bfu_skeletal_mesh
from .. import bfu_alembic_animation
from .. import bfu_lod
from ..bfu_skeletal_mesh.bfu_export_procedure import BFU_SkeletonExportProcedure
from . import bfu_skeletal_mesh_utils


def draw_general_ui_object(layout: bpy.types.UILayout, obj: bpy.types.Object):    
    if not isinstance(obj.data, bpy.types.Armature):
        return
    
    scene = bpy.context.scene 
    
    if bfu_ui.bfu_ui_utils.DisplayPropertyFilter("OBJECT", "GENERAL"):
        accordion = bbpl.blender_layout.layout_accordion.get_accordion(scene, "bfu_object_properties_expanded")
        if accordion:
            if accordion.is_expanded():
                if bfu_export_control.bfu_export_control_utils.is_export_recursive(obj):
                    if not bfu_alembic_animation.bfu_alembic_animation_props.get_object_export_as_alembic_animation(obj):
                        skeletal_mesh_ui = layout.column()
                        # Show asset type
                        skeletal_mesh_ui.prop(obj, "bfu_export_skeletal_mesh_as_static_mesh")

def draw_ui_object(layout: bpy.types.UILayout, context: bpy.types.Context, obj: bpy.types.Object):

    is_skeletal_mesh = bfu_skeletal_mesh_utils.is_skeletal_mesh(obj)
    if not isinstance(obj.data, bpy.types.Armature):
        return
    if is_skeletal_mesh is False:
        return
    if bfu_export_control.bfu_export_control_utils.is_not_export_recursive(obj):
        return
    if bfu_lod.bfu_lod_props.get_object_export_as_lod_mesh(obj):
        return
    
    scene = bpy.context.scene 

    if bfu_ui.bfu_ui_utils.DisplayPropertyFilter("OBJECT", "GENERAL"):
        accordion = bbpl.blender_layout.layout_accordion.get_accordion(scene, "bfu_skeleton_properties_expanded")
        if accordion:
            _, panel = accordion.draw(layout)
            if panel:

                # SkeletalMesh prop
                AssetType2 = panel.column()

                AssetType2.prop(obj, 'bfu_create_sub_folder_with_skeletal_mesh_name')
                AssetType2.prop(obj, 'bfu_export_deform_only')
                ue_standard_skeleton = panel.column()

                if bfu_skeletal_mesh.bfu_export_procedure.get_object_export_procedure(obj).value == BFU_SkeletonExportProcedure.CUSTOM_FBX_EXPORT.value:
                    ue_standard_skeleton_props = ue_standard_skeleton.column()
                    ue_standard_skeleton_props.prop(obj, "bfu_mirror_symmetry_right_side_bones")
                    mirror_symmetry_right_side_bones = ue_standard_skeleton_props.row()
                    mirror_symmetry_right_side_bones.enabled = bfu_skeletal_mesh.bfu_skeletal_mesh_props.get_object_mirror_symmetry_right_side_bones(obj)
                    mirror_symmetry_right_side_bones.prop(obj, "bfu_use_ue_mannequin_bone_alignment")

def draw_ui_scene(layout: bpy.types.UILayout):
    pass