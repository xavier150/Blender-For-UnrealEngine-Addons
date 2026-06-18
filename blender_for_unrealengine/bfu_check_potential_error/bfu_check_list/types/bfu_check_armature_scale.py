# SPDX-FileCopyrightText: Xavier Loux (BleuRaven)
#
# SPDX-License-Identifier: GPL-3.0-or-later

# ----------------------------------------------
#  Blender For UnrealEngine
#  https://github.com/xavier150/Blender-For-UnrealEngine-Addons
# ----------------------------------------------

from ...bfu_check_types import bfu_checker
from ....bfu_cached_assets.bfu_cached_assets_blender_class import AssetToExport

class BFU_Checker_ArmatureScale(bfu_checker):

    def __init__(self):
        super().__init__()
        self.check_name = "Armature Scale"

    # Check if the armature uses the same value on all scale axes
    def run_asset_check(self, asset: AssetToExport):
        if not asset.asset_type.is_skeletal():
            return

        obj_to_check = self.get_armatures_to_check(asset)
        for obj in obj_to_check:
            if obj.scale.z != obj.scale.y or obj.scale.z != obj.scale.x:
                my_po_error = self.add_potential_error()
                my_po_error.name = obj.name
                my_po_error.type = 2
                my_po_error.text = (
                    f'In object "{obj.name}", the scale values are not consistent across all axes.'
                )
                my_po_error.text += (
                    f'\nScale x: {obj.scale.x}, y: {obj.scale.y}, z: {obj.scale.z}'
                )
                my_po_error.object = obj
