# SPDX-FileCopyrightText: Xavier Loux (BleuRaven)
#
# SPDX-License-Identifier: GPL-3.0-or-later

# ----------------------------------------------
#  Blender For UnrealEngine
#  https://github.com/xavier150/Blender-For-UnrealEngine-Addons
# ----------------------------------------------

from ...bfu_check_types import bfu_checker
from ....bfu_cached_assets.bfu_cached_assets_blender_class import AssetToExport

class BFU_Checker_ArmatureConstData(bfu_checker):

    def __init__(self):
        super().__init__()
        self.check_name = "Armature Constraint Data"

    # Check the parameters of ARMATURE constraints
    def run_asset_check(self, asset: AssetToExport):
        pass
        # @TODO.

