# SPDX-FileCopyrightText: Xavier Loux (BleuRaven)
#
# SPDX-License-Identifier: GPL-3.0-or-later

# ----------------------------------------------
#  Blender For UnrealEngine
#  https://github.com/xavier150/Blender-For-UnrealEngine-Addons
# ----------------------------------------------

from pathlib import Path
import bpy
from typing import List
from .. import bbpl
from ..bfu_assets_manager.bfu_asset_manager_type import AssetToExport
from .. import bfu_basics
from .. import bfu_export_logs
from .. import bfu_addon_prefs
from . import bfu_export_single_generic



def prepare_scene_for_export():    
    scene = bpy.context.scene
    if scene is None:
        raise RuntimeError("Scene is not available for export. Please ensure you are in a valid Blender context.")

    # Unhide all objects, but hide on viewport and make them selectable
    for obj in scene.objects:
        if obj.hide_select:
            obj.hide_select = False
        if obj.hide_viewport is False:
            obj.hide_viewport = True
        if obj.hide_get():
            obj.hide_set(False)

    # Hhide all collections on viewport and make them selectable
    for col in bpy.data.collections:
        if col.hide_select:
            col.hide_select = False
        if col.hide_viewport:
            col.hide_viewport = False

    # Unexclude all layer collections and hide them on viewport
    for vlayer in scene.view_layers:
        layer_collections = bbpl.utils.get_layer_collections_recursive(vlayer.layer_collection)
        for layer_collection in layer_collections:
            if layer_collection.exclude:
                layer_collection.exclude = False
            if layer_collection.hide_viewport:
                layer_collection.hide_viewport = False

def process_export(op: bpy.types.Operator, final_asset_list_to_export: List[AssetToExport]) -> List[bfu_export_logs.bfu_asset_export_logs_types.ExportedAssetLog]:
    prepare_all_export_time_log = bfu_export_logs.bfu_process_time_logs_utils.start_time_log("Prepare all export")

    scene = bpy.context.scene
    addon_prefs = bfu_addon_prefs.get_addon_preferences()

    # Save scene data before export
    bbpl.scene_utils.move_to_global_view()
    user_scene_save = bbpl.save_data.scene_save.UserSceneSave()
    user_scene_save.save_current_scene()
    
    # Set object mode before hide object or it will be not possible de switch to object mode.
    bbpl.utils.safe_mode_set('OBJECT', user_scene_save.user_select_class.user_active)
    prepare_scene_for_export()

    if addon_prefs.revert_export_path:
        bfu_basics.RemoveFolderTree(Path(bpy.path.abspath(scene.bfu_export_static_mesh_file_path)).resolve())  # type: ignore
        bfu_basics.RemoveFolderTree(Path(bpy.path.abspath(scene.bfu_export_skeletal_mesh_file_path)).resolve())  # type: ignore
        bfu_basics.RemoveFolderTree(Path(bpy.path.abspath(scene.bfu_export_skeletal_animation_file_path)).resolve())  # type: ignore
        bfu_basics.RemoveFolderTree(Path(bpy.path.abspath(scene.bfu_export_alembic_file_path)).resolve())  # type: ignore
        bfu_basics.RemoveFolderTree(Path(bpy.path.abspath(scene.bfu_export_groom_file_path)).resolve())  # type: ignore
        bfu_basics.RemoveFolderTree(Path(bpy.path.abspath(scene.bfu_export_camera_file_path)).resolve())  # type: ignore
        bfu_basics.RemoveFolderTree(Path(bpy.path.abspath(scene.bfu_export_spline_file_path)).resolve())  # type: ignore
        bfu_basics.RemoveFolderTree(Path(bpy.path.abspath(scene.bfu_export_other_file_path)).resolve())  # type: ignore


    prepare_all_export_time_log.end_time_log()
    exported_asset_log = export_all_from_asset_list(op, final_asset_list_to_export)

    post_export_time_log = bfu_export_logs.bfu_process_time_logs_utils.start_time_log("Clean after all export")

    # Reset scene data after export
    user_scene_save.reset_scene_at_save(print_removed_items = True)
    user_scene_save.reset_select(use_names = True)
    user_scene_save.reset_mode_at_save() # Apply the mode after resetting selection

    # Clean actions
    for action in bpy.data.actions:
        if action.name not in user_scene_save.action_names:
            bpy.data.actions.remove(action)

    bbpl.scene_utils.move_to_local_view()
    post_export_time_log.end_time_log()
    return exported_asset_log


def export_all_from_asset_list(op: bpy.types.Operator, asset_list: List[AssetToExport]) -> List[bfu_export_logs.bfu_asset_export_logs_types.ExportedAssetLog]:
    scene = bpy.context.scene
    if scene is None:
        raise RuntimeError("Scene is not available for export. Please ensure you are in a valid Blender context.")

    export_time_log = bfu_export_logs.bfu_process_time_logs_utils.start_time_log("TOTAL EXPORT")
    exported_asset_log: List[bfu_export_logs.bfu_asset_export_logs_types.ExportedAssetLog] = []

    for asset in asset_list:
        export_asset_time_log = bfu_export_logs.bfu_process_time_logs_utils.start_time_log(f"Export '{asset.name}' as {asset.asset_type.get_friendly_name()}.")
        # Save current start/end frame
        user_start_frame = scene.frame_start
        user_end_frame = scene.frame_end
        exported_asset_log.append(bfu_export_single_generic.process_generic_export_from_asset(op, asset))

        # Resets previous start/end frame
        scene.frame_start = user_start_frame
        scene.frame_end = user_end_frame
        export_asset_time_log.end_time_log()

    export_time_log.end_time_log()
    return exported_asset_log