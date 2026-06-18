# SPDX-FileCopyrightText: Xavier Loux (BleuRaven)
#
# SPDX-License-Identifier: GPL-3.0-or-later

# ----------------------------------------------
#  Blender For UnrealEngine
#  https://github.com/xavier150/Blender-For-UnrealEngine-Addons
# ----------------------------------------------

import bpy
from ...bfu_check_types import bfu_checker
from ... import bfu_check_utils
from ....bfu_cached_assets.bfu_cached_assets_blender_class import AssetToExport


class BFU_Checker_VertexGroupWeight(bfu_checker):

    def __init__(self):
        super().__init__()
        self.check_name = "Vertex Group Weight"

    # Prepare the list of objects to check
    
    def contains_armature_modifier(self, obj: bpy.types.Object) -> bool:
        for mod in obj.modifiers:
            if mod.type == "ARMATURE":  # type: ignore
                return True
        return False

    # Check that all vertices have a weight
    def run_asset_check(self, asset: AssetToExport):
        if not asset.asset_type.is_skeletal():
            return

        main_obj = asset.get_primary_asset_package()
        if main_obj:
            for mesh in self.get_meshes_to_check(asset):
                if mesh.type == "MESH":# type: ignore
                    if self.contains_armature_modifier(mesh):
                        # Get vertices with zero weight
                        vertices_with_zero_weight = bfu_check_utils.get_vertices_with_zero_weight(main_obj, mesh)
                        if vertices_with_zero_weight:
                            my_po_error = self.add_potential_error()
                            my_po_error.name = mesh.name
                            my_po_error.type = 1
                            my_po_error.text = (
                                f'Object "{mesh.name}" contains {len(vertices_with_zero_weight)} '
                                'vertices with zero cumulative valid weight.'
                            )
                            my_po_error.text += (
                                '\nNote: Vertex groups must have a bone with the same name to be valid.'
                            )
                            my_po_error.object = mesh
                            my_po_error.select_vertex_button = True
                            my_po_error.select_option = "VertexWithZeroWeight"
