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
from .... import bfu_nanite
from ....bfu_nanite.bfu_nanite_props import BFU_BuildNaniteMode

maxium_uv_maps_without_nanite = 8 # Unreal Engine supports a maximum of 8 UV channels for non-Nanite meshes.
maxium_uv_maps_with_nanite = 4 # Unreal Engine supports a maximum of 4 UV channels for Nanite meshes.

# Notes:
# https://dev.epicgames.com/documentation/en-us/unreal-engine/using-uv-channels-with-static-meshes-in-unreal-engine
# https://forums.unrealengine.com/t/getting-only-4-uvs-channels-when-exporting-mesh/1763857

class BFU_Checker_UVMapsNumber(bfu_checker):
    
    def __init__(self):
        super().__init__()
        self.check_name = "UV Maps Number"

    # Check that the objects have a valid number of UV maps depending on whether they are set to be imported as Nanite or not.
    def run_asset_check(self, asset: AssetToExport):
        for obj in self.get_meshes_to_check(asset):
            if obj.data:
                if not bfu_collision.bfu_collision_utils.is_a_collision(obj):
                    num_uv_maps = len(obj.data.uv_layers)  # type: ignore
                    build_nanite_mode: BFU_BuildNaniteMode = bfu_nanite.bfu_nanite_props.get_object_build_nanite_mode(obj)
                    if build_nanite_mode.value in [BFU_BuildNaniteMode.BUILD_NANITE_TRUE.value, BFU_BuildNaniteMode.AUTO.value]:
                        # Notify auto because in most of case projects are setup to import meshes as Nanite by default.
                        if num_uv_maps > maxium_uv_maps_with_nanite:
                            my_po_error = self.add_potential_error()
                            my_po_error.name = obj.name
                            my_po_error.type = 1
                            my_po_error.text = f'Object "{obj.name}" has {num_uv_maps} UV maps but only {maxium_uv_maps_with_nanite} are supported for Nanite meshes in Unreal Engine. \n (8 UV maps are supported for non-Nanite meshes.)' 
                            my_po_error.object = obj
                    else:
                        if num_uv_maps > maxium_uv_maps_without_nanite:
                            my_po_error = self.add_potential_error()
                            my_po_error.name = obj.name
                            my_po_error.type = 1
                            my_po_error.text = f'Object "{obj.name}" has {num_uv_maps} UV maps but only {maxium_uv_maps_without_nanite} are supported for non-Nanite meshes in Unreal Engine. (4 UV maps are supported for Nanite meshes.)'
                            my_po_error.object = obj