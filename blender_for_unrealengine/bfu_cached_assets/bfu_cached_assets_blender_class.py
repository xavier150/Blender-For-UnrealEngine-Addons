# SPDX-FileCopyrightText: Xavier Loux (BleuRaven)
#
# SPDX-License-Identifier: GPL-3.0-or-later

# ----------------------------------------------
#  Blender For UnrealEngine
#  https://github.com/xavier150/Blender-For-UnrealEngine-Addons
# ----------------------------------------------


import bpy
from typing import List, Optional
from ..bfu_assets_manager.bfu_asset_manager_type import AssetToExport, AssetToSearch, AssetDataSearchMode, AssetType
from .. import bfu_assets_manager
from .. import bfu_export_control
from .. import bfu_debug_settings
from .. import bfu_collection_as_staticmesh
from .. import bfu_export_filter
from ..bfu_export_filter.bfu_export_filter_props import BFU_ExportSelectionFilterEnum



class BFU_FinalExportAssetCache(bpy.types.PropertyGroup):

    def get_final_asset_list(self, asset_to_search: AssetToSearch = AssetToSearch.ALL_ASSETS, search_mode: AssetDataSearchMode = AssetDataSearchMode.ASSET_NUMBER, force_cache_update: bool = False) -> List[AssetToExport]:
        # Returns all assets that will be exported
        # WARNING: the assets not to be ordered. First asset are exported first.

        events = bfu_debug_settings.root_events
        events.add_sub_event("Get Final Asset List")
        events.add_sub_event("Prepare")

        def get_have_parent_to_export(obj: bpy.types.Object) -> Optional[bpy.types.Object]:
            if obj.parent is not None:
                if bfu_export_control.bfu_export_control_utils.is_export_recursive(obj.parent):
                    return obj.parent
                else:
                    return get_have_parent_to_export(obj.parent)
            else:
                return None

        scene = bpy.context.scene
        if not scene:
            return []
        export_filter: BFU_ExportSelectionFilterEnum = bfu_export_filter.bfu_export_filter_props.scene_export_selection_filter(scene)

        target_asset_to_export: List[AssetToExport] = []

        events.stop_last_and_start_new_event("Search Assets")
        if asset_to_search.value == AssetToSearch.ALL_ASSETS.value:

            
            # Search for objects
            obj_list: List[bpy.types.Object] = []
            if export_filter.value == BFU_ExportSelectionFilterEnum.DEFAULT.value:
                events.add_sub_event("Search recursive objects 01")
                obj_list = bfu_export_control.bfu_export_control_utils.get_all_export_recursive_objects(scene)
                events.stop_last_event()

            elif export_filter.value in [BFU_ExportSelectionFilterEnum.ONLY_OBJECT.value, BFU_ExportSelectionFilterEnum.ONLY_OBJECT_AND_ACTIVE.value]:
                events.add_sub_event("Search recursive objects 02")
                recursive_list = bfu_export_control.bfu_export_control_utils.get_all_export_recursive_objects(scene)

                events.stop_last_and_start_new_event("filter recursive objects")
                for obj in bpy.context.selected_objects:
                    if obj in recursive_list:
                        if obj not in obj_list:
                            obj_list.append(obj)
                    parent_target = get_have_parent_to_export(obj)
                    if parent_target is not None:
                        if parent_target not in obj_list:
                            obj_list.append(parent_target)
                events.stop_last_event()

            events.add_sub_event("Create object assets class")
            # Search for objects assets
            for obj in obj_list:
                asset_class_list = bfu_assets_manager.bfu_asset_manager_utils.get_custom_type_supported_asset_class("Object", obj)
                for asset_class in asset_class_list:
                    target_asset_to_export.extend(asset_class.get_asset_export_data(obj, None, search_mode=search_mode))
            events.stop_last_event()


        events.stop_last_and_start_new_event("Search Collections")
        if asset_to_search.value in [AssetToSearch.ALL_ASSETS.value, AssetToSearch.COLLECTION_ONLY.value]:
        
            if export_filter.value == BFU_ExportSelectionFilterEnum.DEFAULT.value:
                collection_list: List[bpy.types.Collection] = []
                events.add_sub_event("-> S1")
            
                # Search for collections
                collection_list = bfu_collection_as_staticmesh.bfu_static_col_utils.optimized_collection_search(scene)
    
                events.stop_last_and_start_new_event("Create collection assets class")
                # Search for collections assets
                for collection in collection_list:
                    asset_class_list = bfu_assets_manager.bfu_asset_manager_utils.get_custom_type_supported_asset_class("Scene", collection)
                    if asset_class_list:
                        for asset_class in asset_class_list:
                            target_asset_to_export.extend(asset_class.get_asset_export_data(collection, None, search_mode=search_mode))

                events.stop_last_event()


        events.stop_last_and_start_new_event("Search Armatures")
        if asset_to_search.value in [AssetToSearch.ALL_ASSETS.value, AssetToSearch.ANIMATION_ONLY.value]:
            events.add_sub_event("-> S1")
            
            # Search for armatures and their actions
            armature_list: List[bpy.types.Object] = []
            if export_filter.value == BFU_ExportSelectionFilterEnum.DEFAULT.value:
                armature_list = bfu_export_control.bfu_export_control_utils.get_all_export_recursive_armatures(scene)
            elif export_filter.value in [BFU_ExportSelectionFilterEnum.ONLY_OBJECT.value, BFU_ExportSelectionFilterEnum.ONLY_OBJECT_AND_ACTIVE.value]:
                armature_recursive_list = bfu_export_control.bfu_export_control_utils.get_all_export_recursive_armatures(scene)

                for obj in bpy.context.selected_objects:
                    if obj in armature_recursive_list:
                        if obj not in armature_list:
                            armature_list.append(obj)
                    armature_parent_target = get_have_parent_to_export(obj)
                    if armature_parent_target is not None:
                        if armature_parent_target not in armature_list:
                            armature_list.append(armature_parent_target)

            events.stop_last_and_start_new_event("-> S2")

            # Search for armature animation assets
            for armature in armature_list:
                asset_class_list = bfu_assets_manager.bfu_asset_manager_utils.get_custom_type_supported_asset_class("ArmatureAnimation", armature)
                for asset_class in asset_class_list:
                    target_asset_to_export.extend(asset_class.get_asset_export_data(armature, None, search_mode=search_mode))
            
            # Get batch action assets export data from asset classes
            for asset in bfu_assets_manager.bfu_asset_manager_registred_assets.get_registred_asset_class_by_type("ArmatureActions"):
                target_asset_to_export.extend(asset.get_batch_asset_export_data(search_mode=search_mode, force_cache_update=force_cache_update))


        events.stop_last_and_start_new_event("Search Other Assets")

        # Reorder the asset list
        asset_type_order = [
            AssetType.COLLECTION_AS_STATIC_MESH,
            AssetType.CAMERA,
            AssetType.SPLINE,
            AssetType.STATIC_MESH,
            AssetType.SKELETAL_MESH,
            AssetType.ANIM_ALEMBIC,
            AssetType.GROOM_SIMULATION,
            AssetType.ANIM_POSE,
            AssetType.ANIM_ACTION,
            AssetType.ANIM_NLA,
        ]

        type_priority = {asset_type: index for index, asset_type in enumerate(asset_type_order)}

        def sort_key(asset: AssetToExport):
            return type_priority.get(asset.asset_type, len(asset_type_order))
        
        target_asset_to_export.sort(key=sort_key)
        events.stop_last_event()
        events.stop_last_event()
        return target_asset_to_export


def get_final_asset_cache() -> BFU_FinalExportAssetCache: # type: ignore
    scene = bpy.context.scene
    if scene:
        return scene.final_asset_cache # type: ignore

# -------------------------------------------------------------------
#   Register & Unregister
# -------------------------------------------------------------------

classes = (
    BFU_FinalExportAssetCache,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    
    bpy.types.Scene.final_asset_cache = bpy.props.PointerProperty( # type: ignore
        type=BFU_FinalExportAssetCache,
        options={'LIBRARY_EDITABLE'},
        override={'LIBRARY_OVERRIDABLE'},
        )



def unregister():

    del bpy.types.Scene.final_asset_cache # type: ignore

    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)

    