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

class BFU_Checker_ShapeKeys(bfu_checker):

    def __init__(self):
        super().__init__()
        self.check_name = "Shape Keys"

        # Destructive modifiers that can break shape keys at export
        self.destructive_modifiers = {
            "BOOLEAN",       # ...
            "BUILD",         # ...
            "DECIMATE",      # ...
            "EDGE_SPLIT",    # ...
            "MASK",          # ...
            "MIRROR",        # ...
            "REMESH",        # ...
            "SCREW",         # ...
            "SKIN",          # ...
            "SOLIDIFY",      # ...
            "SUBSURF",       # ...
            "TRIANGULATE",   # ...
            "WELD",          # ...
            "WIREFRAME",     # ...
        }


    # Check shape keys validity and safety for Unreal export
    def run_asset_check(self, asset: AssetToExport):
        for obj in self.get_meshes_to_check(asset):
            if obj.data is not None:
                shape_keys = obj.data.shape_keys  # type: ignore
                if shape_keys is not None and len(shape_keys.key_blocks) > 0:  # type: ignore
                    # Check that no modifiers is destructive for the key shapes
                    for modif in obj.modifiers:
                        mod_type = modif.type  # type: ignore
                        if mod_type in self.destructive_modifiers:
                            my_po_error = self.add_potential_error()
                            my_po_error.name = obj.name
                            my_po_error.type = 2
                            my_po_error.object = obj
                            my_po_error.item_name = modif.name
                            my_po_error.text = (
                                f'In object "{obj.name}", the modifier "{mod_type}" '
                                f'named "{modif.name}" can destroy shape keys. '
                                'Please use only the Armature modifier with shape keys.'
                            )
                            my_po_error.correct_ref = "RemoveModifier"
                            my_po_error.correct_label = 'Remove modifier'

                    # Check shape key ranges for Unreal Engine compatibility
                    unreal_engine_shape_key_max = 5
                    unreal_engine_shape_key_min = -5
                    for key in shape_keys.key_blocks:  # type: ignore
                        if isinstance(key, bpy.types.ShapeKey):
                            # Min check
                            if key.slider_min < unreal_engine_shape_key_min:
                                my_po_error = self.add_potential_error()
                                my_po_error.name = obj.name
                                my_po_error.type = 1
                                my_po_error.object = obj
                                my_po_error.item_name = key.name
                                my_po_error.text = (
                                    f'In object "{obj.name}", the shape key "{key.name}" '
                                    f'is out of bounds for Unreal. The minimum range must not be less than {unreal_engine_shape_key_min}.'
                                )
                                my_po_error.correct_ref = "SetKeyRangeMin"
                                my_po_error.correct_label = f'Set min range to {unreal_engine_shape_key_min}'

                            # Max check
                            if key.slider_max > unreal_engine_shape_key_max:
                                my_po_error = self.add_potential_error()
                                my_po_error.name = obj.name
                                my_po_error.type = 1
                                my_po_error.object = obj
                                my_po_error.item_name = key.name
                                my_po_error.text = (
                                    f'In object "{obj.name}", the shape key "{key.name}" '
                                    f'is out of bounds for Unreal. The maximum range must not exceed {unreal_engine_shape_key_max}.'
                                )
                                my_po_error.correct_ref = "SetKeyRangeMax"
                                my_po_error.correct_label = f'Set max range to {unreal_engine_shape_key_max}'
