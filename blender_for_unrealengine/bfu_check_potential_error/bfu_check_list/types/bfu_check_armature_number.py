# SPDX-FileCopyrightText: Xavier Loux (BleuRaven)
#
# SPDX-License-Identifier: GPL-3.0-or-later

# ----------------------------------------------
#  Blender For UnrealEngine
#  https://github.com/xavier150/Blender-For-UnrealEngine-Addons
# ----------------------------------------------

from ...bfu_check_types import bfu_checker
from ....bfu_cached_assets.bfu_cached_assets_blender_class import AssetToExport

class BFU_Checker_ArmatureNumber(bfu_checker):

    def __init__(self):
        super().__init__()
        self.check_name = "Armature Number"


    # Check if the number of ARMATURE modifiers or constraints is exactly 1
    def run_asset_check(self, asset: AssetToExport):
        if not asset.asset_type.is_skeletal():
            return

        for mesh in self.get_meshes_to_check(asset):
            # Count the number of ARMATURE modifiers and constraints
            armature_modifiers = sum(1 for mod in mesh.modifiers if mod.type == "ARMATURE")  # type: ignore
            armature_constraints = sum(1 for const in mesh.constraints if const.type == "ARMATURE")  # type: ignore

            # Check if the total number of ARMATURE modifiers and constraints is greater than 1
            if armature_modifiers + armature_constraints > 1:
                my_po_error = self.add_potential_error()
                my_po_error.name = mesh.name
                my_po_error.type = 2
                my_po_error.text = (
                    f'In object "{mesh.name}", {armature_modifiers} Armature modifier(s) and '
                    f'{armature_constraints} Armature constraint(s) were found. '
                    'Please use only one Armature modifier or one Armature constraint.'
                )
                my_po_error.object = mesh

            # Check if no ARMATURE modifiers or constraints are found
            if armature_modifiers + armature_constraints == 0:
                my_po_error = self.add_potential_error()
                my_po_error.name = mesh.name
                my_po_error.type = 2
                my_po_error.text = (
                    f'In object "{mesh.name}", no Armature modifiers or constraints were found. '
                    'Please use one Armature modifier or one Armature constraint.'
                )
                my_po_error.object = mesh
