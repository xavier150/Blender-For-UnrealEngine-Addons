# SPDX-FileCopyrightText: Xavier Loux (BleuRaven)
#
# SPDX-License-Identifier: GPL-3.0-or-later

# ----------------------------------------------
#  Blender For UnrealEngine
#  https://github.com/xavier150/Blender-For-UnrealEngine-Addons
# ----------------------------------------------

import bpy
from ...bfu_check_types import bfu_checker
from ....bfu_cached_assets.bfu_cached_assets_blender_class import AssetToExport

class BFU_Checker_ArmatureNoDeformBone(bfu_checker):

    def __init__(self):
        super().__init__()
        self.check_name = "Armature No Deform Bone"

    # Check that the skeleton has at least one deform bone
    def run_asset_check(self, asset: AssetToExport):
        if not asset.asset_type.is_skeletal():
            return

        for obj in self.get_armatures_to_check(asset):
            if obj.bfu_export_deform_only:  # type: ignore
                if not isinstance(obj.data, bpy.types.Armature):
                    continue
                has_deform_bone = any(bone.use_deform for bone in obj.data.bones)
                if not has_deform_bone:
                    my_po_error = self.add_potential_error()
                    my_po_error.name = obj.name
                    my_po_error.type = 2
                    my_po_error.text = (
                        f'Object "{obj.name}" does not have any deform bones. '
                        'Unreal will import it as a StaticMesh.'
                    )
                    my_po_error.object = obj
