# SPDX-FileCopyrightText: Xavier Loux (BleuRaven)
#
# SPDX-License-Identifier: GPL-3.0-or-later

# ----------------------------------------------
#  Blender For UnrealEngine
#  https://github.com/xavier150/Blender-For-UnrealEngine-Addons
# ----------------------------------------------


from ...bfu_check_types import bfu_checker
from ....bfu_cached_assets.bfu_cached_assets_blender_class import AssetToExport

class BFU_Checker_ObjType(bfu_checker):

    def __init__(self):
        super().__init__()
        self.check_name = "Object Type"

        self.non_recommended_types = {"SURFACE", "META", "FONT"}

    def run_asset_check(self, asset: AssetToExport):
        for package in asset.asset_packages:
            for obj in package.objects:
                obj_type = obj.type  # type: ignore
                if obj_type in self.non_recommended_types:
                    my_po_error = self.add_potential_error()
                    my_po_error.name = obj.name
                    my_po_error.type = 1
                    my_po_error.text = (
                        f'Object "{obj.name}" is a {obj_type}. The object of the type '
                        'SURFACE, META, and FONT is not recommended.'
                    )
                    my_po_error.object = obj
                    my_po_error.correct_ref = "ConvertToMesh"
                    my_po_error.correct_label = 'Convert to mesh'
