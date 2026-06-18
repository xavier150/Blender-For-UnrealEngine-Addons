# SPDX-FileCopyrightText: Xavier Loux (BleuRaven)
#
# SPDX-License-Identifier: GPL-3.0-or-later

# ----------------------------------------------
#  Blender For UnrealEngine
#  https://github.com/xavier150/Blender-For-UnrealEngine-Addons
# ----------------------------------------------

import bpy
from .... import bfu_utils
from ....bfu_simple_file_type_enum import BFU_FileTypeEnum
from .... import bfu_addon_prefs
from ....bfu_cached_assets.bfu_cached_assets_blender_class import AssetToExport
from ...bfu_check_types import bfu_checker


class BFU_Checker_UnitScale(bfu_checker):
    
    def __init__(self):
        super().__init__()
        self.check_name = "Unit Scale"

    def run_asset_check(self, asset: AssetToExport):
        addon_prefs = bfu_addon_prefs.get_addon_preferences()        
        main_object = asset.get_primary_asset_package()

        scene = bpy.context.scene
        if scene is None:
            return

        if main_object:
            file_type = asset.original_asset_class.get_package_file_type(main_object)

            if file_type in [BFU_FileTypeEnum.FBX, BFU_FileTypeEnum.ALEMBIC]:

                # Check if the unit scale is equal to 0.01 for FBX and Alembic export.
                if addon_prefs.notifyUnitScalePotentialError:
                    if not bfu_utils.get_scene_unit_scale_is_close(0.01):
                        str_unit_scale = str(bfu_utils.get_scene_unit_scale())
                        my_po_error = self.add_potential_error()
                        my_po_error.name = scene.name
                        my_po_error.type = 1
                        my_po_error.text = (f"Asset '{asset.name}'(FBX) in scene '{scene.name}' has a Unit Scale equal to {str_unit_scale}.")
                        my_po_error.text += ('\nFor Unreal, with FBX and Alembic export a unit scale equal to 0.01 is recommended.')
                        my_po_error.text += ('\n(You can disable this potential error in the addon preferences.)')
                        my_po_error.object = main_object
                        my_po_error.correct_ref = "SetUnitScaleForFBX"
                        my_po_error.correct_label = 'Set Unreal Unit 0.01'
            
            elif file_type in [BFU_FileTypeEnum.GLTF]:
                
                # Check if the unit scale is equal to 1.0 for GLTF export.
                if addon_prefs.notifyUnitScalePotentialError:
                    if not bfu_utils.get_scene_unit_scale_is_close(1.0):
                        str_unit_scale = str(bfu_utils.get_scene_unit_scale())
                        my_po_error = self.add_potential_error()
                        my_po_error.name = scene.name
                        my_po_error.type = 1
                        my_po_error.text = (f"Asset '{asset.name}'(GLTF) in scene '{scene.name}' has a Unit Scale equal to {str_unit_scale}.")
                        my_po_error.text += ('\nFor Unreal, with GLTF export a unit scale equal to 1.0 is recommended.')
                        my_po_error.text += ('\n(You can disable this potential error in the addon preferences.)')
                        my_po_error.object = main_object
                        my_po_error.correct_ref = "SetUnitScaleForGLTF"
                        my_po_error.correct_label = 'Set Unreal Unit 1.0'