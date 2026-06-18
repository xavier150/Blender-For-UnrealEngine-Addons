# SPDX-FileCopyrightText: Xavier Loux (BleuRaven)
#
# SPDX-License-Identifier: GPL-3.0-or-later

# ----------------------------------------------
#  Blender For UnrealEngine
#  https://github.com/xavier150/Blender-For-UnrealEngine-Addons
# ----------------------------------------------

import bpy
from ... import bfu_check_props
from ...bfu_check_types import bfu_checker
from .... import bfu_utils
from ....bfu_assets_manager.bfu_asset_manager_type import AssetToExport

class BFU_Checker_ArmatureChildWithBoneParent(bfu_checker):

    def __init__(self):
        super().__init__()
        self.check_name = "Armature Child With Bone Parent"

    # Check if a mesh child is parented to a bone, which will cause import issues
    def run_asset_check(self, asset: AssetToExport):
        if not asset.asset_type.is_skeletal():
            return
        for obj in self.get_armatures_to_check(asset):
            childs = bfu_utils.get_export_desired_childs(obj)
            for child in childs:
                if child.type == "MESH" and child.parent_type == 'BONE':  # type: ignore
                    my_po_error = self.add_potential_error()
                    my_po_error.name = child.name
                    my_po_error.type = 2
                    my_po_error.text = (
                        f'Object "{child.name}" uses Parent Bone to parent. '
                        '\nIf you use Parent Bone to parent your mesh to your armature, the import will fail.'
                    )
                    my_po_error.object = child
                    my_po_error.correct_ref = "Self"
                    my_po_error.correct_label = "Use Armature Modifier."
                    my_po_error.docs_octicon = 'armature-child-with-bone-parent'

    def run_correction(self, my_po_error: bfu_check_props.BFU_OT_UnrealPotentialError) -> bool:
        # Use Armature Modifier instead of Parent Bone
        obj = my_po_error.object
        if not isinstance(obj.data, bpy.types.Mesh):
            return False

        # Get the armature
        armature = obj.parent
        bone_name = obj.parent_bone

        # Clear parent and keep transform
        current_matrix = obj.matrix_world.copy()
        obj.parent_bone = ""
        obj.parent_type = 'ARMATURE'
        obj.parent = armature
        obj.matrix_world = current_matrix
       
        # Clear all existing vertex groups and create a new one
        obj.vertex_groups.clear()
        vg = obj.vertex_groups.new(name=bone_name)
        vg.add(range(len(obj.data.vertices)), 1.0, 'ADD')

        # Create Armature Modifier
        armature_modifier = obj.modifiers.new(name="Armature", type='ARMATURE')
        if isinstance(armature_modifier, bfu_utils.bpy.types.ArmatureModifier):
            armature_modifier.object = armature
            armature_modifier.vertex_group = bone_name
            return True
        
        return False
