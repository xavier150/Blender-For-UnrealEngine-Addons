# SPDX-FileCopyrightText: Xavier Loux (BleuRaven)
#
# SPDX-License-Identifier: GPL-3.0-or-later

# ----------------------------------------------
#  Blender For UnrealEngine
#  https://github.com/xavier150/Blender-For-UnrealEngine-Addons
# ----------------------------------------------

from ...bfu_check_types import bfu_checker
from ....bfu_cached_assets.bfu_cached_assets_blender_class import AssetToExport

class BFU_Checker_ArmatureModData(bfu_checker):

    def __init__(self):
        super().__init__()
        self.check_name = "Armature Modifier Data"

    
    # Check the parameters of ARMATURE modifiers
    def run_asset_check(self, asset: AssetToExport):
        if not asset.asset_type.is_skeletal():
            return

        for obj in self.get_objects_to_check(asset):
            for mod in obj.modifiers:
                if mod.type == "ARMATURE":  # type: ignore
                    if mod.use_deform_preserve_volume:  # type: ignore
                        my_po_error = self.add_potential_error()
                        my_po_error.name = obj.name
                        my_po_error.type = 2
                        my_po_error.text = (
                            f'In object "{obj.name}", the ARMATURE modifier '
                            f'named "{mod.name}" has the Preserve Volume parameter set to True. '
                            'This parameter must be set to False.'
                        )
                        my_po_error.object = obj
                        my_po_error.item_name = mod.name
                        my_po_error.correct_ref = "PreserveVolume"
                        my_po_error.correct_label = 'Set Preserve Volume to False'
