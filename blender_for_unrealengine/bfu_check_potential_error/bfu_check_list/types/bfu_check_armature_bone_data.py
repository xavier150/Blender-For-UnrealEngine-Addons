# SPDX-FileCopyrightText: Xavier Loux (BleuRaven)
#
# SPDX-License-Identifier: GPL-3.0-or-later

# ----------------------------------------------
#  Blender For UnrealEngine
#  https://github.com/xavier150/Blender-For-UnrealEngine-Addons
# ----------------------------------------------

import bpy
from ...bfu_check_types import bfu_checker
from ....bfu_assets_manager.bfu_asset_manager_type import AssetToExport

class BFU_Checker_ArmatureBoneData(bfu_checker):

    def __init__(self):
        super().__init__()
        self.check_name = "Armature Bone Data"



    # Check the parameters of the ARMATURE bones
    def run_asset_check(self, asset: AssetToExport):
        if not asset.asset_type.is_skeletal():
            return

        for obj in self.get_armatures_to_check(asset):
            if not isinstance(obj.data, bpy.types.Armature):
                continue
            for bone in obj.data.bones:
                if (not obj.bfu_export_deform_only or (bone.use_deform and obj.bfu_export_deform_only)):  # type: ignore

                    if bone.bbone_segments > 1:
                        my_po_error = self.add_potential_error()
                        my_po_error.name = obj.name
                        my_po_error.type = 1
                        my_po_error.text = (
                            f'In asset "{obj.name}", the bone named "{bone.name}" '
                            'has the Bendy Bones / Segments parameter set to more than 1. '
                            'This parameter must be set to 1.'
                        )
                        my_po_error.text += (
                            '\nBendy bones are not supported by Unreal Engine, '
                            'so it is better to disable it if you want the same '
                            'animation preview in Unreal and Blender.'
                        )
                        my_po_error.object = obj
                        my_po_error.item_name = bone.name
                        my_po_error.select_pose_bone_button = True
                        my_po_error.correct_ref = "BoneSegments"
                        my_po_error.correct_label = 'Set Bone Segments to 1'
                        my_po_error.docs_octicon = 'bendy-bone'
