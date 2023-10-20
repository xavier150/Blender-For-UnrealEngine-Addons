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
from .. import bps
from .. import bbpl
from .. import bfu_basics
from .. import bfu_utils

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


def ExportAllAssetByList(op, targetobjects, targetActionName, targetcollection):
    # Export all objects that need to be exported from a list

    if len(targetobjects) < 1 and len(targetcollection) < 1:
        return

    scene = bpy.context.scene
    counter = bps.utils.CounterTimer()

    NumberAssetToExport = len(bfu_utils.GetFinalAssetToExport())

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
        for col in bfu_utils.GetCollectionToExport(scene):
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

            # Camera
            print("Start Export camera(s)")
            if bfu_utils.GetAssetType(obj) == "Camera" and IsValidObjectForExport(scene, obj):
                # Save current start/end frame
                UserStartFrame = scene.frame_start
                UserEndFrame = scene.frame_end
                bfu_export_single_camera.ProcessCameraExport(op, obj)

                # Resets previous start/end frame
                scene.frame_start = UserStartFrame
                scene.frame_end = UserEndFrame
                UpdateExportProgress()

            # StaticMesh
            print("Start Export StaticMesh(s)")
            if bfu_utils.GetAssetType(obj) == "StaticMesh" and IsValidObjectForExport(scene, obj):

                # Save current start/end frame
                UserStartFrame = scene.frame_start
                UserEndFrame = scene.frame_end
                bfu_export_single_static_mesh.ProcessStaticMeshExport(op, obj)

                # Resets previous start/end frame
                scene.frame_start = UserStartFrame
                scene.frame_end = UserEndFrame
                UpdateExportProgress()

            # SkeletalMesh
            print("Start Export SkeletalMesh(s)")
            if bfu_utils.GetAssetType(obj) == "SkeletalMesh" and IsValidObjectForExport(scene, obj):
                # Save current start/end frame
                UserStartFrame = scene.frame_start
                UserEndFrame = scene.frame_end
                bfu_export_single_skeletal_mesh.ProcessSkeletalMeshExport(op, obj)

                # Resets previous start/end frame
                scene.frame_start = UserStartFrame
                scene.frame_end = UserEndFrame
                UpdateExportProgress()

            # Alembic
            print("Start Export Alembic(s)")
            if bfu_utils.GetAssetType(obj) == "Alembic" and IsValidObjectForExport(scene, obj):
                # Save current start/end frame
                UserStartFrame = scene.frame_start
                UserEndFrame = scene.frame_end
                bfu_export_single_alembic_animation.ProcessAlembicExport(obj)

                # Resets previous start/end frame
                scene.frame_start = UserStartFrame
                scene.frame_end = UserEndFrame
                UpdateExportProgress()

            # Action animation
            if bfu_utils.GetAssetType(obj) == "SkeletalMesh" and obj.visible_get():
                print("Start Export Action(s)")
                action_curve_scale = None
                for action in bfu_utils.GetActionToExport(obj):
                    if action.name in targetActionName:
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
                                UpdateExportProgress()
                if action_curve_scale:
                    action_curve_scale.ResetScaleAfterExport()

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

    UpdateExportProgress(counter.get_time())

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

def ExportForUnrealEngine(op):
    scene = bpy.context.scene
    addon_prefs = bfu_basics.GetAddonPrefs()
    export_filter = scene.bfu_export_selection_filter

    local_view_areas = bbpl.scene_utils.move_to_global_view()

    MyCurrentDataSave = bbpl.utils.UserSceneSave()
    MyCurrentDataSave.save_current_scene()
    
    if export_filter == "default":
        PrepareSceneForExport()
        AssetToExport = bfu_utils.GetFinalAssetToExport()

    elif export_filter == "only_object" or export_filter == "only_object_action":
        AssetToExport = bfu_utils.GetFinalAssetToExport() #Get finial assets visible only
        PrepareSceneForExport()


    bbpl.utils.safe_mode_set('OBJECT', MyCurrentDataSave.user_select_class.user_active)

    if addon_prefs.revertExportPath:
        bfu_basics.RemoveFolderTree(bpy.path.abspath(scene.export_static_file_path))
        bfu_basics.RemoveFolderTree(bpy.path.abspath(scene.export_skeletal_file_path))
        bfu_basics.RemoveFolderTree(bpy.path.abspath(scene.export_alembic_file_path))
        bfu_basics.RemoveFolderTree(bpy.path.abspath(scene.export_camera_file_path))
        bfu_basics.RemoveFolderTree(bpy.path.abspath(scene.export_other_file_path))

    obj_list = []  # Do a simple list of Objects to export
    action_list = []  # Do a simple list of Action to export
    col_list = []  # Do a simple list of Collection to export


    for Asset in AssetToExport:
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

    ExportAllAssetByList(
        op,
        targetobjects=obj_list,
        targetActionName=action_list,
        targetcollection=col_list,
    )

    MyCurrentDataSave.reset_select_by_name()
    MyCurrentDataSave.reset_scene_at_save(print_removed_items = True)

    # Clean actions
    for action in bpy.data.actions:
        if action.name not in MyCurrentDataSave.action_names:
            bpy.data.actions.remove(action)

    bbpl.scene_utils.move_to_local_view(local_view_areas)
