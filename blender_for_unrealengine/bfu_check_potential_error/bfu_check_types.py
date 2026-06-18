# SPDX-FileCopyrightText: Xavier Loux (BleuRaven)
#
# SPDX-License-Identifier: GPL-3.0-or-later

# ----------------------------------------------
#  Blender For UnrealEngine
#  https://github.com/xavier150/Blender-For-UnrealEngine-Addons
# ----------------------------------------------


import bpy
from . import bfu_check_props
from typing import List
from abc import ABC
from ..bfu_cached_assets.bfu_cached_assets_blender_class import AssetToExport

class bfu_checker(ABC):

    def __init__(self):
        self.check_name: str = "My Checker"
    
    # Helpers

    def add_potential_error(self) -> bfu_check_props.BFU_OT_UnrealPotentialError:
        scene = bpy.context.scene  # type: ignore
        return scene.bfu_export_potential_errors.add()  # type: ignore

    # Prepare list of skeletal objects to check
    def get_armatures_to_check(self, asset: AssetToExport) -> List[bpy.types.Object]:
        obj_to_check: List[bpy.types.Object] = []

        for package in asset.asset_packages:
            for obj in package.objects:
                if obj.type == 'ARMATURE':  # type: ignore
                    obj_to_check.append(obj)

        return obj_to_check

    def get_meshes_to_check(self, asset: AssetToExport) -> List[bpy.types.Object]:
        obj_to_check: List[bpy.types.Object] = []

        for package in asset.asset_packages:
            for obj in package.objects:
                if obj.type == 'MESH':  # type: ignore
                    obj_to_check.append(obj)

        return obj_to_check
    
    # Prepare list of objects to check
    def get_objects_to_check(self, asset: AssetToExport) -> List[bpy.types.Object]:
        obj_to_check: List[bpy.types.Object] = []

        for package in asset.asset_packages:
            for obj in package.objects:
                obj_to_check.append(obj)

        return obj_to_check

    # Prepare list of collections to check
    def get_collections_to_check(self, asset: AssetToExport) -> List[bpy.types.Collection]:
        collection_to_check: List[bpy.types.Collection] = []

        for package in asset.asset_packages:
            for col in package.collection:
                collection_to_check.append(col)

        return collection_to_check

    # Prepare list of actions to check
    def get_actions_to_check(self, asset: AssetToExport) -> List[bpy.types.Action]:
        action_to_check: List[bpy.types.Action] = []

        for package in asset.asset_packages:
            if package.action:
                action_to_check.append(package.action)

        return action_to_check

    # Check Methods

    def run_scene_check(self, scene: bpy.types.Scene):
        pass

    def run_asset_check(self, asset: AssetToExport):
        pass

    def run_correction(self, my_po_error: bfu_check_props.BFU_OT_UnrealPotentialError) -> bool:
        return False


# -------------------------------------------------------------------
#   Register & Unregister
# -------------------------------------------------------------------

classes = (
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)  # type: ignore


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)  # type: ignore