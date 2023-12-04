# ====================== BEGIN GPL LICENSE BLOCK ============================
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.	 See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.	 If not, see <http://www.gnu.org/licenses/>.
#  All rights reserved.
#
# ======================= END GPL LICENSE BLOCK =============================


import bpy
from . import bfu_export_single_alembic_animation
from . import bfu_export_single_fbx_action
from . import bfu_export_single_camera
from . import bfu_export_single_fbx_nla_anim
from . import bfu_export_single_skeletal_mesh
from . import bfu_export_single_static_mesh
from . import bfu_export_single_static_mesh_collection
from .. import bfu_cached_asset_list
from .. import bps
from .. import bbpl
from .. import bfu_basics
from .. import bfu_utils
from .. import bfu_camera

if "bpy" in locals():
    import importlib
    if "bfu_export_single_alembic_animation" in locals():
        importlib.reload(bfu_export_single_alembic_animation)
    if "bfu_export_single_fbx_action" in locals():
        importlib.reload(bfu_export_single_fbx_action)
    if "bfu_export_single_camera" in locals():
        importlib.reload(bfu_export_single_camera)
    if "bfu_export_single_fbx_nla_anim" in locals():
        importlib.reload(bfu_export_single_fbx_nla_anim)
    if "bfu_export_single_skeletal_mesh" in locals():
        importlib.reload(bfu_export_single_skeletal_mesh)
    if "bfu_export_single_static_mesh" in locals():
        importlib.reload(bfu_export_single_static_mesh)
    if "bfu_export_single_static_mesh_collection" in locals():
        importlib.reload(bfu_export_single_static_mesh_collection)
    if "bfu_cached_asset_list" in locals():
        importlib.reload(bfu_cached_asset_list)
    if "bps" in locals():
        importlib.reload(bps)
    if "bbpl" in locals():
        importlib.reload(bbpl)
    if "bfu_basics" in locals():
        importlib.reload(bfu_basics)
    if "bfu_utils" in locals():
        importlib.reload(bfu_utils)


def IsValidActionForExport(scene, obj, animType):
    if animType == "Action":
        if scene.anin_export:
            if obj.bfu_export_procedure == 'auto-rig-pro':
                if bfu_basics.CheckPluginIsActivated('auto_rig_pro-master'):
                    return True
            else:
                return True
        else:
            return False
    elif animType == "Pose":
        if scene.anin_export:
            if obj.bfu_export_procedure == 'auto-rig-pro':
                if bfu_basics.CheckPluginIsActivated('auto_rig_pro-master'):
                    return True
            else:
                return True
        else:
            return False
    elif animType == "NLA":
        if scene.anin_export:
            if obj.bfu_export_procedure == 'auto-rig-pro':
                return False
            else:
                return True
        else:
            False
    else:
        print("Error in IsValidActionForExport() animType not found: ", animType)
    return False


def IsValidObjectForExport(scene, obj):
    objType = bfu_utils.GetAssetType(obj)

    if objType == "Camera":
        return scene.camera_export
    if objType == "StaticMesh":
        return scene.static_export
    if objType == "SkeletalMesh":
        if scene.skeletal_export:
            if obj.bfu_export_procedure == 'auto-rig-pro':
                if bfu_basics.CheckPluginIsActivated('auto_rig_pro-master'):
                    return True
            else:
                return True
        else:
            False
    if objType == "Alembic":
        return scene.alembic_export

    return False

def PrepareSceneForExport():
    for obj in bpy.data.objects:
        if obj.hide_select:
            obj.hide_select = False
        if obj.hide_viewport:
            obj.hide_viewport = False
        if obj.hide_get():
            obj.hide_set(False)

    for col in bpy.data.collections:
        if col.hide_select:
            col.hide_select = False
        if col.hide_viewport:
            col.hide_viewport = False

    for vlayer in bpy.context.scene.view_layers:
        layer_collections = bbpl.utils.get_layer_collections_recursive(vlayer.layer_collection)
        for layer_collection in layer_collections:
            if layer_collection.exclude:
                layer_collection.exclude = False
            if layer_collection.hide_viewport:
                layer_collection.hide_viewport = False

def process_export(op):
    scene = bpy.context.scene
    addon_prefs = bfu_basics.GetAddonPrefs()
    export_filter = scene.bfu_export_selection_filter

    local_view_areas = bbpl.scene_utils.move_to_global_view()

    MyCurrentDataSave = bbpl.utils.UserSceneSave()
    MyCurrentDataSave.save_current_scene()
    
    if export_filter == "default":
        PrepareSceneForExport()
        final_asset_cache = bfu_cached_asset_list.GetfinalAssetCache()
        final_asset_list_to_export = final_asset_cache.GetFinalAssetList()

    elif export_filter == "only_object" or export_filter == "only_object_action":
        final_asset_cache = bfu_cached_asset_list.GetfinalAssetCache()
        final_asset_list_to_export = final_asset_cache.GetFinalAssetList() #Get finial assets visible only
        PrepareSceneForExport()


    bbpl.utils.safe_mode_set('OBJECT', MyCurrentDataSave.user_select_class.user_active)

    if addon_prefs.revertExportPath:
        bfu_basics.RemoveFolderTree(bpy.path.abspath(scene.bfu_export_static_file_path))
        bfu_basics.RemoveFolderTree(bpy.path.abspath(scene.bfu_export_skeletal_file_path))
        bfu_basics.RemoveFolderTree(bpy.path.abspath(scene.bfu_export_alembic_file_path))
        bfu_basics.RemoveFolderTree(bpy.path.abspath(scene.bfu_export_camera_file_path))
        bfu_basics.RemoveFolderTree(bpy.path.abspath(scene.bfu_export_other_file_path))

    obj_list = []  # Do a simple list of Objects to export
    action_list = []  # Do a simple list of Action to export
    col_list = []  # Do a simple list of Collection to export

    export_all_from_asset_list(op, final_asset_list_to_export)

    for Asset in final_asset_list_to_export:
        if Asset.asset_type == "Action" or Asset.asset_type == "Pose":
            if Asset.obj not in action_list:
                action_list.append(Asset.action.name)
            if Asset.obj not in obj_list:
                obj_list.append(Asset.obj)

        elif Asset.asset_type == "Collection StaticMesh":
            if Asset.obj not in col_list:
                col_list.append(Asset.obj)

        else:
            if Asset.obj not in obj_list:
                obj_list.append(Asset.obj)

    '''
    ExportAllAssetByList(
        op,
        targetobjects=obj_list,
        targetActionName=action_list,
        targetcollection=col_list,
    )
    '''

    MyCurrentDataSave.reset_select_by_name()
    MyCurrentDataSave.reset_scene_at_save(print_removed_items = True)

    # Clean actions
    for action in bpy.data.actions:
        if action.name not in MyCurrentDataSave.action_names:
            bpy.data.actions.remove(action)

    bbpl.scene_utils.move_to_local_view(local_view_areas)


def export_all_from_asset_list(op, asset_list: bfu_cached_asset_list.AssetToExport):
    export_collection_from_asset_list(op, asset_list)
    export_camera_from_asset_list(op, asset_list)
    export_static_mesh_from_asset_list(op, asset_list)
    export_skeletal_mesh_from_asset_list(op, asset_list)
    export_alembic_from_asset_list(op, asset_list)
    export_animation_from_asset_list(op, asset_list)
    export_nonlinear_animation_from_asset_list(op, asset_list)

def export_collection_from_asset_list(op, asset_list: bfu_cached_asset_list.AssetToExport):
    pass

def export_camera_from_asset_list(op, asset_list: bfu_cached_asset_list.AssetToExport):
    scene = bpy.context.scene
    addon_prefs = bfu_basics.GetAddonPrefs()
    print("Start Export camera(s)")

    camera_list = []

    use_camera_evaluate = (scene.text_AdditionalData and addon_prefs.useGeneratedScripts)
    if use_camera_evaluate:
        multi_camera_tracks = bfu_camera.bfu_camera_data.MultiCameraDataAtFrame()
        multi_camera_tracks.set_start_end_frames(scene.frame_start, scene.frame_end+1)
    
    # Preparre asset to export
    for asset in asset_list:
        asset: bfu_cached_asset_list.AssetToExport
        if asset.asset_type == "Camera":
            obj = asset.obj
            if obj.bfu_export_type == "export_recursive":
                if bfu_utils.GetAssetType(obj) == "Camera" and IsValidObjectForExport(scene, obj):                    
                    camera_list.append(obj)
                    multi_camera_tracks.add_camera_to_evaluate(obj)

    if use_camera_evaluate:
        multi_camera_tracks.evaluate_all_cameras()

    #Start export
    for obj in camera_list:
        # Save current start/end frame
        UserStartFrame = scene.frame_start
        UserEndFrame = scene.frame_end

        if use_camera_evaluate:
            camera_tracks = multi_camera_tracks.get_evaluate_camera_data(obj)
        else:
            camera_tracks = None
        bfu_export_single_camera.ProcessCameraExport(op, obj, camera_tracks)

        # Resets previous start/end frame
        scene.frame_start = UserStartFrame
        scene.frame_end = UserEndFrame
        #UpdateExportProgress()

def export_static_mesh_from_asset_list(op, asset_list: [bfu_cached_asset_list.AssetToExport]):
    scene = bpy.context.scene

    print("Start Export StaticMesh(s)")
    for asset in asset_list:
        asset: bfu_cached_asset_list.AssetToExport
        if asset.asset_type == "StaticMesh":
            obj = asset.obj
            if obj.bfu_export_type == "export_recursive":
                if bfu_utils.GetAssetType(obj) == "StaticMesh" and IsValidObjectForExport(scene, obj):

                    # Save current start/end frame
                    UserStartFrame = scene.frame_start
                    UserEndFrame = scene.frame_end
                    bfu_export_single_static_mesh.ProcessStaticMeshExport(op, obj)

                    # Resets previous start/end frame
                    scene.frame_start = UserStartFrame
                    scene.frame_end = UserEndFrame
                    #UpdateExportProgress()

def export_skeletal_mesh_from_asset_list(op, asset_list: bfu_cached_asset_list.AssetToExport):
    scene = bpy.context.scene

    print("Start Export SkeletalMesh(s)")
    for asset in asset_list:
        asset: bfu_cached_asset_list.AssetToExport
        if asset.asset_type == "SkeletalMesh":
            armature = asset.obj
            mesh_parts = asset.obj_list
            desired_name = asset.name
            if armature.bfu_export_type == "export_recursive":
                if bfu_utils.GetAssetType(armature) == "SkeletalMesh" and IsValidObjectForExport(scene, armature):
                    # Save current start/end frame
                    UserStartFrame = scene.frame_start
                    UserEndFrame = scene.frame_end
                    bfu_export_single_skeletal_mesh.ProcessSkeletalMeshExport(op, armature, mesh_parts, desired_name)

                    # Resets previous start/end frame
                    scene.frame_start = UserStartFrame
                    scene.frame_end = UserEndFrame
                    #UpdateExportProgress()

def export_alembic_from_asset_list(op, asset_list: bfu_cached_asset_list.AssetToExport):
    scene = bpy.context.scene

    print("Start Export Alembic(s)")
    for asset in asset_list:
        asset: bfu_cached_asset_list.AssetToExport
        if asset.asset_type == "Alembic":
            obj = asset.obj
            if obj.bfu_export_type == "export_recursive":        
                if bfu_utils.GetAssetType(obj) == "Alembic" and IsValidObjectForExport(scene, obj):
                    # Save current start/end frame
                    UserStartFrame = scene.frame_start
                    UserEndFrame = scene.frame_end
                    bfu_export_single_alembic_animation.ProcessAlembicExport(obj)

                    # Resets previous start/end frame
                    scene.frame_start = UserStartFrame
                    scene.frame_end = UserEndFrame
                    #UpdateExportProgress()

def export_animation_from_asset_list(op, asset_list: bfu_cached_asset_list.AssetToExport):
    scene = bpy.context.scene

    for asset in asset_list:
        asset: bfu_cached_asset_list.AssetToExport
        if asset.asset_type == "Action" or asset.asset_type == "Pose":
            obj = asset.obj
            if obj.bfu_export_type == "export_recursive":    
                if bfu_utils.GetAssetType(obj) == "SkeletalMesh" and obj.visible_get():
                    # Action animation
                    print("Start Export Action(s)")
                    action_curve_scale = None
                    animation_asset_cache = bfu_cached_asset_list.GetAnimationAssetCache(obj)
                    animation_to_export = animation_asset_cache.GetAnimationAssetList()
                    for action in animation_to_export:
                        if action.name == asset.action.name:
                            animType = bfu_utils.GetActionType(action)

                            # Action and Pose
                            if IsValidActionForExport(scene, obj, animType):
                                if animType == "Action" or animType == "Pose":
                                    # Save current start/end frame
                                    UserStartFrame = scene.frame_start
                                    UserEndFrame = scene.frame_end
                                    action_curve_scale = bfu_export_single_fbx_action.ProcessActionExport(op, obj, action, action_curve_scale)

                                    # Resets previous start/end frame
                                    scene.frame_start = UserStartFrame
                                    scene.frame_end = UserEndFrame
                                    #UpdateExportProgress()
                    if action_curve_scale:
                        action_curve_scale.ResetScaleAfterExport()

def export_nonlinear_animation_from_asset_list(op, asset_list: bfu_cached_asset_list.AssetToExport):
    scene = bpy.context.scene

    for asset in asset_list:
        asset: bfu_cached_asset_list.AssetToExport
        if asset.asset_type == "NlAnim":
            obj = asset.obj
            if obj.bfu_export_type == "export_recursive":    
                if bfu_utils.GetAssetType(obj) == "SkeletalMesh" and obj.visible_get():
                    # NLA animation
                    print("Start Export NLA(s)")
                    if IsValidActionForExport(scene, obj, "NLA"):
                        if obj.bfu_anim_nla_use:
                            # Save current start/end frame
                            UserStartFrame = scene.frame_start
                            UserEndFrame = scene.frame_end
                            bfu_export_single_fbx_nla_anim.ProcessNLAAnimExport(op, obj)

                            # Resets previous start/end frame
                            scene.frame_start = UserStartFrame
                            scene.frame_end = UserEndFrame


def ExportAllAssetByList(op, targetobjects, targetActionName, targetcollection):
    # Export all objects that need to be exported from a list

    print(len(targetobjects), len(targetcollection))
    if len(targetobjects) < 1 and len(targetcollection) < 1:
        return

    scene = bpy.context.scene
    counter = bps.utils.CounterTimer()

    final_asset_cache = bfu_cached_asset_list.GetfinalAssetCache()
    final_asset_list_to_export = final_asset_cache.GetFinalAssetList()
    NumberAssetToExport = len(final_asset_list_to_export)

    def UpdateExportProgress(time=None):
        exported_assets = len(scene.UnrealExportedAssetsList)
        remain_assets = exported_assets/NumberAssetToExport

        wm = bpy.context.window_manager

        if remain_assets == NumberAssetToExport:
            wm.progress_begin(0, remain_assets)

        wm.progress_update(exported_assets)

        if remain_assets == 0:
            wm.progress_end()

        bfu_utils.UpdateProgress("Export assets", remain_assets, time)

    UpdateExportProgress()

    # Export collections
    print("Start Export collection(s)")
    if scene.static_collection_export:
        collection_asset_cache = bfu_cached_asset_list.GetCollectionAssetCache()
        collection_export_asset_list = collection_asset_cache.GetCollectionAssetList()
        for col in collection_export_asset_list:
            if col.name in targetcollection:
                # Save current start/end frame
                UserStartFrame = scene.frame_start
                UserEndFrame = scene.frame_end
                bfu_export_single_static_mesh_collection.ProcessCollectionExport(op, col)

                # Resets previous start/end frame
                scene.frame_start = UserStartFrame
                scene.frame_end = UserEndFrame
                UpdateExportProgress()

    # Export assets
    for obj in targetobjects:
        if obj.bfu_export_type == "export_recursive":
            pass









    UpdateExportProgress(counter.get_time())