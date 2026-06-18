# SPDX-FileCopyrightText: Xavier Loux (BleuRaven)
#
# SPDX-License-Identifier: GPL-3.0-or-later

# ----------------------------------------------
#  Blender For UnrealEngine
#  https://github.com/xavier150/Blender-For-UnrealEngine-Addons
# ----------------------------------------------


from ...bfu_check_types import bfu_checker
from ....bfu_cached_assets.bfu_cached_assets_blender_class import AssetToExport
from .... import bfu_collision

class BFU_Checker_UVMaps(bfu_checker):

    def __init__(self):
        super().__init__()
        self.check_name = "UV Maps"

    # Check that the objects have at least one valid UV map
    def run_asset_check(self, asset: AssetToExport):
        for obj in self.get_meshes_to_check(asset):
            if obj.data:
                if not bfu_collision.bfu_collision_utils.is_a_collision(obj):
                    if len(obj.data.uv_layers) < 1:  # type: ignore
                        my_po_error = self.add_potential_error()
                        my_po_error.name = obj.name
                        my_po_error.type = 1
                        my_po_error.text = f'Object "{obj.name}" does not have any UV Layer.'
                        my_po_error.object = obj
                        my_po_error.correct_ref = "CreateUV"
                        my_po_error.correct_label = 'Create Smart UV Project'
