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

if "bpy" in locals():
    import importlib
    if "bfu_write_text" in locals():
        importlib.reload(bfu_write_text)
    if "bfu_basics" in locals():
        importlib.reload(bfu_basics)
    if "bfu_utils" in locals():
        importlib.reload(bfu_utils)
    if "bfu_export_single_alembic_animation" in locals():
        importlib.reload(bfu_export_single_alembic_animation)
    if "bfu_export_single_fbx_action" in locals():
        importlib.reload(bfu_export_single_fbx_action)
    if "bfu_export_single_fbx_camera" in locals():
        importlib.reload(bfu_export_single_fbx_camera)
    if "bfu_export_single_fbx_nla_anim" in locals():
        importlib.reload(bfu_export_single_fbx_nla_anim)
    if "bfu_export_single_skeletal_mesh" in locals():
        importlib.reload(bfu_export_single_skeletal_mesh)
    if "bfu_export_single_static_mesh" in locals():
        importlib.reload(bfu_export_single_static_mesh)
    if "bfu_export_single_static_mesh_collection" in locals():
        importlib.reload(bfu_export_single_static_mesh_collection)

import bpy
import time
import math


from . import bfu_write_text
from . import bfu_basics
from .bfu_basics import *
from . import bfu_utils
from .bfu_utils import *
from . import bfu_export_single_alembic_animation
from .bfu_export_single_alembic_animation import *

from . import bfu_export_single_fbx_action
from .bfu_export_single_fbx_action import *

from . import bfu_export_single_fbx_camera
from .bfu_export_single_fbx_camera import *

from . import bfu_export_single_fbx_nla_anim
from .bfu_export_single_fbx_nla_anim import *

from . import bfu_export_single_skeletal_mesh
from .bfu_export_single_skeletal_mesh import *

from . import bfu_export_single_static_mesh
from .bfu_export_single_static_mesh import *

from . import bfu_export_single_static_mesh_collection
from .bfu_export_single_static_mesh_collection import *


def ExportAllAssetByList(
    originalScene,
    targetobjects,
    targetActionName,
    targetcollection
):
    # Export all objects that need to be exported from a list

    if len(targetobjects) < 1 and len(targetcollection) < 1:
        return

    scene = bpy.context.scene
    addon_prefs = bpy.context.preferences.addons[__package__].preferences

    s = CounterStart()

    NumberAssetToExport = len(GetFinalAssetToExport())

    def UpdateProgress(time=None):
        update_progress(
            "Export assets",
            len(originalScene.UnrealExportedAssetsList)/NumberAssetToExport,
            time
        )
    UpdateProgress()

    if scene.static_collection_export:
        for col in GetCollectionToExport(originalScene):
            if col in targetcollection:
                # StaticMesh collection
                ExportSingleStaticMeshCollection(
                    originalScene,
                    GetCollectionExportDir(),
                    GetCollectionExportFileName(col),
                    col
                )
                UpdateProgress()

    for obj in targetobjects:

        if obj.ExportEnum == "export_recursive":

            # Camera
            if GetAssetType(obj) == "Camera" and scene.camera_export:
                # Save current start/end frame
                UserStartFrame = scene.frame_start
                UserEndFrame = scene.frame_end
                ExportSingleFbxCamera(
                        originalScene,
                        GetObjExportDir(obj),
                        GetObjExportFileName(obj),
                        obj
                    )
                if obj.ExportAsLod is False:
                    if (scene.text_AdditionalData and
                            addon_prefs.useGeneratedScripts):
                        ExportSingleAdditionalTrackCamera(
                            GetObjExportDir(obj),
                            GetObjExportFileName(obj, "_AdditionalTrack.ini"),
                            obj
                            )
                # Resets previous start/end frame
                scene.frame_start = UserStartFrame
                scene.frame_end = UserEndFrame
                UpdateProgress()

            # StaticMesh
            if GetAssetType(obj) == "StaticMesh" and scene.static_export:
                ExportSingleStaticMesh(
                    originalScene,
                    GetObjExportDir(obj),
                    GetObjExportFileName(obj),
                    obj
                    )
                if obj.ExportAsLod is False:
                    if (scene.text_AdditionalData and
                            addon_prefs.useGeneratedScripts):
                        ExportSingleAdditionalParameterMesh(
                            GetObjExportDir(obj),
                            GetObjExportFileName(
                                obj,
                                "_AdditionalParameter.ini"
                                ),
                            obj
                            )
                UpdateProgress()

            # SkeletalMesh
            if GetAssetType(obj) == "SkeletalMesh" and scene.skeletal_export:
                ExportSingleSkeletalMesh(
                    originalScene,
                    GetObjExportDir(obj),
                    GetObjExportFileName(obj),
                    obj
                    )

                if (scene.text_AdditionalData and
                        addon_prefs.useGeneratedScripts):

                    ExportSingleAdditionalParameterMesh(
                        GetObjExportDir(obj),
                        GetObjExportFileName(obj, "_AdditionalParameter.ini"),
                        obj
                        )
                UpdateProgress()

            # Alembic
            if GetAssetType(obj) == "Alembic" and scene.alembic_export:
                ExportSingleAlembicAnimation(
                    originalScene,
                    GetObjExportDir(obj),
                    GetObjExportFileName(obj, ".abc"),
                    obj
                    )
                UpdateProgress()

            # Action animation
            if GetAssetType(obj) == "SkeletalMesh" and obj.visible_get():
                animExportDir = os.path.join(
                    GetObjExportDir(obj),
                    scene.anim_subfolder_name
                    )
                for action in GetActionToExport(obj):
                    if action.name in targetActionName:
                        animType = GetActionType(action)

                        # Action
                        if animType == "Action" and scene.anin_export:
                            # Save current start/end frame
                            UserStartFrame = scene.frame_start
                            UserEndFrame = scene.frame_end
                            ExportSingleFbxAction(
                                originalScene,
                                animExportDir,
                                GetActionExportFileName(obj, action),
                                obj,
                                action,
                                "Action"
                                )
                            # Resets previous start/end frame
                            scene.frame_start = UserStartFrame
                            scene.frame_end = UserEndFrame
                            UpdateProgress()

                        # pose
                        if animType == "Pose" and scene.anin_export:
                            # Save current start/end frame
                            UserStartFrame = scene.frame_start
                            UserEndFrame = scene.frame_end
                            ExportSingleFbxAction(
                                originalScene,
                                animExportDir,
                                GetActionExportFileName(obj, action),
                                obj,
                                action,
                                "Pose"
                                )
                            # Resets previous start/end frame
                            scene.frame_start = UserStartFrame
                            scene.frame_end = UserEndFrame
                            UpdateProgress()

                # NLA animation
                if bpy.context.scene.anin_export:
                    if obj.ExportNLA:
                        scene.frame_end += 1
                        ExportSingleFbxNLAAnim(
                            originalScene,
                            animExportDir,
                            GetNLAExportFileName(obj),
                            obj
                            )
                        scene.frame_end -= 1

    UpdateProgress(CounterEnd(s))


def PrepareAndSaveDataForExport():

    scene = bpy.context.scene
    addon_prefs = bpy.context.preferences.addons[__package__].preferences

    MoveToGlobalView()

    mode_set = bpy.ops.object.mode_set

    # ----------------------------------------Save data
    # This can take time

    actionNames = []
    for action in bpy.data.actions:
        actionNames.append(action.name)

    collectionNames = []
    for collection in bpy.data.collections:
        collectionNames.append(collection.name)

    UserObjHide = []
    for object in bpy.data.objects:
        UserObjHide.append((
                object.name,
                object.hide_select,
                object.hide_viewport
                )
            )
        if object.hide_select:
            object.hide_select = False
        if object.hide_viewport:
            object.hide_viewport = False

    UserColHide = []
    for col in bpy.data.collections:
        UserColHide.append((col.name, col.hide_select, col.hide_viewport))
        if col.hide_select:
            col.hide_select = False
        if col.hide_viewport:
            col.hide_viewport = False

    UserVLayerHide = []
    for vlayer in bpy.context.scene.view_layers:
        for childCol in vlayer.layer_collection.children:
            UserVLayerHide.append((
                    vlayer.name,
                    childCol.name,
                    childCol.exclude,
                    childCol.hide_viewport
                    )
                )
            if childCol.exclude:
                childCol.exclude = False
            if childCol.hide_viewport:
                childCol.hide_viewport = False

    copyScene = bpy.context.scene.copy()
    copyScene.name = "ue4-export_Temp"
    bpy.context.window.scene = copyScene  # Switch the scene but can take time

    UserActive = bpy.context.active_object  # Save current active object
    if mode_set.poll():
        UserMode = UserActive.mode  # Save current mode
    else:
        UserMode = None

    if UserActive and UserActive.mode != 'OBJECT' and mode_set.poll():
        mode_set(mode='OBJECT')

    if addon_prefs.revertExportPath:
        RemoveFolderTree(bpy.path.abspath(scene.export_static_file_path))
        RemoveFolderTree(bpy.path.abspath(scene.export_skeletal_file_path))
        RemoveFolderTree(bpy.path.abspath(scene.export_alembic_file_path))
        RemoveFolderTree(bpy.path.abspath(scene.export_camera_file_path))
        RemoveFolderTree(bpy.path.abspath(scene.export_other_file_path))

    assetList = []  # Do a simple lit of objects to export
    for Asset in GetFinalAssetToExport():
        if Asset.obj in GetAllobjectsByExportType("export_recursive"):
            if Asset.obj not in assetList:
                assetList.append(Asset.obj)

    ExportAllAssetByList(
        originalScene=scene,
        targetobjects=assetList,
        targetActionName=actionNames,
        targetcollection=collectionNames,
    )

    bpy.context.window.scene = scene
    bpy.data.scenes.remove(copyScene)

    # UserActive = bpy.context.active_object #Save current active object
    if UserMode:
        bpy.ops.object.mode_set(mode=UserMode)

    # Clean actions
    for action in bpy.data.actions:
        if action.name not in actionNames:
            bpy.data.actions.remove(action)

    # Reset hide and select (bpy.data.objects)
    for object in UserObjHide:
        if object[0] in bpy.data.objects:
            if bpy.data.objects[object[0]].hide_select != object[1]:
                bpy.data.objects[object[0]].hide_select = object[1]
            if bpy.data.objects[object[0]].hide_select != object[2]:
                bpy.data.objects[object[0]].hide_viewport = object[2]
            pass
        else:
            print("/!\\ "+object[0]+" not found in bpy.data.objects")

    # Reset hide and select (collections)
    for col in UserColHide:
        if col[0] in bpy.data.collections:
            if bpy.data.collections[col[0]].hide_select != col[1]:
                bpy.data.collections[col[0]].hide_select = col[1]
            if bpy.data.collections[col[0]].hide_select != col[2]:
                bpy.data.collections[col[0]].hide_viewport = col[2]
            pass
        else:
            print("/!\\ "+col[0]+" not found in bpy.data.collections")

    # Reset hide in and viewport (collections)
    for childCol in UserVLayerHide:
        view_layer = scene.view_layers[childCol[0]]
        layer_col_children = view_layer.layer_collection.children[childCol[1]]

        if layer_col_children.exclude != childCol[2]:
            layer_col_children.exclude = childCol[2]
        if layer_col_children.hide_viewport != childCol[3]:
            layer_col_children.hide_viewport = childCol[3]


def ExportForUnrealEngine():
    PrepareAndSaveDataForExport()
