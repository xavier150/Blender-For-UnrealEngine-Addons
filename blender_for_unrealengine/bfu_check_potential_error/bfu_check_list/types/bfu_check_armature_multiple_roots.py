# SPDX-FileCopyrightText: Xavier Loux (BleuRaven)
#
# SPDX-License-Identifier: GPL-3.0-or-later

# ----------------------------------------------
#  Blender For UnrealEngine
#  https://github.com/xavier150/Blender-For-UnrealEngine-Addons
# ----------------------------------------------

import bpy
from typing import List
from ... import bfu_check_props
from ...bfu_check_types import bfu_checker
from .... import bbpl
from ....bfu_cached_assets.bfu_cached_assets_blender_class import AssetToExport
from .... import bfu_skeletal_mesh

class BFU_Checker_ArmatureMultipleRoots(bfu_checker):

    def __init__(self):
        super().__init__()
        self.check_name = "Armature Multiple Roots"


    # Check if the skeleton has multiple root bones
    def run_asset_check(self, asset: AssetToExport):
        if not asset.asset_type.is_skeletal():
            return

        for obj in self.get_armatures_to_check(asset):
            root_bones: List[bpy.types.Bone] = bfu_skeletal_mesh.bfu_skeletal_mesh_utils.get_armature_root_bones(obj)

            root_bones_str = ""
            for bone in root_bones:
                if bone.use_deform:
                    root_bones_str += bone.name + "(def), "
                else:
                    root_bones_str += bone.name + "(def child(s)), "

            if len(root_bones) > 1:
                my_po_error = self.add_potential_error()
                my_po_error.name = obj.name
                my_po_error.type = 2
                my_po_error.text = (
                    f'Object "{obj.name}" has multiple root bones. Unreal only supports a single root bone.'
                )
                my_po_error.text += '\n' + f' {len(root_bones)} root bone(s) found: {root_bones_str}'
                my_po_error.text += '\n' + 'A custom root bone will be added at export.'
                my_po_error.object = obj
                my_po_error.correct_ref = "Self"
                my_po_error.correct_label = "Create a new root bone at armature origin."
                my_po_error.docs_octicon = 'multiple-root-bones'

    def run_correction(self, my_po_error: bfu_check_props.BFU_OT_UnrealPotentialError) -> bool:
        # Create a new root bone at armature origin

        scene = bpy.context.scene
        if scene is None:
            return False

        obj = my_po_error.object
        if not isinstance(obj.data, bpy.types.Armature):
            return False
        
        save = bbpl.save_data.scene_save.UserSceneSave()
        save.save_current_scene()
        bbpl.utils.select_specific_object(obj)
        bpy.ops.object.mode_set(mode='EDIT')
        root_bones: List[bpy.types.Bone] = bfu_skeletal_mesh.bfu_skeletal_mesh_utils.get_armature_root_bones(obj)
        if len(root_bones) <= 1:
            bpy.ops.object.mode_set(mode='OBJECT')
            print("No correction needed, armature has 1 or less root bones.")
            return False
        
        # Create new root bone
        new_root_bone = obj.data.edit_bones.new("root")
        new_root_bone.head = (0, 0, 0)
        new_root_bone.tail = (0, 0, 0.2 * scene.unit_settings.scale_length)
        for bone in root_bones:
            if bone.name in obj.data.edit_bones:
                print("Reparenting bone:", bone.name)
                edit_bone = obj.data.edit_bones[bone.name]
                edit_bone.use_connect = False
                edit_bone.parent = new_root_bone

        save.reset_select()
        save.reset_mode_at_save()
        return True


        

        
