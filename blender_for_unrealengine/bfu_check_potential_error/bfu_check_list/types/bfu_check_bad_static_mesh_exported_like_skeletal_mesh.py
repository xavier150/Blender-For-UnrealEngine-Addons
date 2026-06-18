# SPDX-FileCopyrightText: Xavier Loux (BleuRaven)
#
# SPDX-License-Identifier: GPL-3.0-or-later

# ----------------------------------------------
#  Blender For UnrealEngine
#  https://github.com/xavier150/Blender-For-UnrealEngine-Addons
# ----------------------------------------------

from ...bfu_check_types import bfu_checker
from ....bfu_cached_assets.bfu_cached_assets_blender_class import AssetToExport, AssetType

class BFU_Checker_BadStaticMeshExportedLikeSkeletalMesh(bfu_checker):

    def __init__(self):
        super().__init__()
        self.check_name = "StaticMesh Exported Like SkeletalMesh"

    # Check if a mesh with an Armature modifier is incorrectly exported as Static Mesh
    def run_asset_check(self, asset: AssetToExport):
        if asset.asset_type != AssetType.STATIC_MESH:
            return
        
        for obj in self.get_objects_to_check(asset):
            for mod in obj.modifiers:
                if mod.type == "ARMATURE":  # type: ignore
                    my_po_error = self.add_potential_error()
                    my_po_error.name = obj.name
                    my_po_error.type = 1
                    my_po_error.text = (
                        f'In object "{obj.name}", the modifier "{mod.type}" '
                        f'named "{mod.name}" will not be applied when exported '
                        'with StaticMesh assets.\nNote: with armature, if you want to export '
                        'objects as skeletal mesh, you need to set only the armature as '
                        'export_recursive, not the child objects.'
                    )
                    my_po_error.object = obj
