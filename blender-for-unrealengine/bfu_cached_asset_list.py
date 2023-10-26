# ====================== BEGIN GPL LICENSE BLOCK ============================
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <http://www.gnu.org/licenses/>.
#  All rights reserved.
#
# ======================= END GPL LICENSE BLOCK =============================


import bpy
import fnmatch
from . import bbpl
from . import bfu_basics
from . import bfu_utils

class CachedAction():

    '''
    I can't use bpy.types.Scene or bpy.types.Object Property.
    "Writing to ID classes in this context is not allowed"
    So I use simple python var
    '''

    class ActionFromCache():
        # Info about actions from last cache.
        def __init__(self, action):
            self.total_action_fcurves_len = len(action.fcurves)

    def __init__(self):
        self.name = ""
        self.is_cached = False
        self.stored_actions = []
        self.total_actions = []
        self.total_rig_bone_len = 0

    def CheckCache(self, obj):
        # Check if the cache need update
        if self.name != obj.name:
            self.is_cached = False
        if len(bpy.data.actions) != len(self.total_actions):
            self.is_cached = False
        if len(obj.data.bones) != self.total_rig_bone_len:
            self.is_cached = False
        for action_name in self.stored_actions:
            if action_name not in bpy.data.actions:
                self.is_cached = False

        return self.is_cached

    def StoreActions(self, obj, actions):
        # Update new cache
        self.name = obj.name
        action_name_list = []
        for action in actions:
            action_name_list.append(action.name)
        self.stored_actions = action_name_list
        self.total_actions.clear()
        for action in bpy.data.actions:
            self.total_actions.append(self.ActionFromCache(action))
        self.total_rig_bone_len = len(obj.data.bones)
        self.is_cached = True
        # print("Stored action cache updated.")

    def GetStoredActions(self):
        actions = []
        for action_name in self.stored_actions:
            if action_name in bpy.data.actions:
                actions.append(bpy.data.actions[action_name])
        return actions

    def Clear(self):
        pass

MyCachedActions = CachedAction()


class BFU_CollectionExportAssetCache(bpy.types.PropertyGroup):

    def GetCollectionAssetList(self):

        scene = self.id_data
        collection_export_asset_list = []

        for col in scene.bfu_collection_asset_list:
            if col.use:
                if col.name in bpy.data.collections:
                    collection = bpy.data.collections[col.name]
                    collection_export_asset_list.append(collection)
        return collection_export_asset_list



class BFU_AnimationExportAssetCache(bpy.types.PropertyGroup):

    def UpdateActionCache(self):
        # Force update cache export auto action list
        return self.GetCachedExportAutoActionList(True)

    def GetCachedExportAutoActionList(self, force_update_cache=False):
        # This will cheak if the action contains
        # the same bones of the armature
        
        obj = self.id_data
        actions = []

        # Use the cache
        if force_update_cache:
            MyCachedActions.is_cached = False

        if MyCachedActions.CheckCache(obj):
            actions = MyCachedActions.GetStoredActions()

        else:
            MyCachedActions.Clear()

            objBoneNames = [bone.name for bone in obj.data.bones]
            for action in bpy.data.actions:
                if action.library is None:
                    if bfu_basics.GetIfActionIsAssociated(action, objBoneNames):
                        actions.append(action)
            # Update the cache
            MyCachedActions.StoreActions(obj, actions)
        return actions

    def GetAnimationAssetList(self):
        # Returns only the actions that will be exported with the Armature

        obj = self.id_data

        if obj.bfu_export_as_lod_mesh:
            return []

        TargetActionToExport = []  # Action list
        if obj.bfu_anim_action_export_enum == "dont_export":
            return []

        if obj.bfu_anim_action_export_enum == "export_current":
            if obj.animation_data is not None:
                if obj.animation_data.action is not None:
                    return [obj.animation_data.action]

        elif obj.bfu_anim_action_export_enum == "export_specific_list":
            for action in bpy.data.actions:
                for targetAction in obj.bfu_animation_asset_list:
                    if targetAction.use:
                        if targetAction.name == action.name:
                            TargetActionToExport.append(action)

        elif obj.bfu_anim_action_export_enum == "export_specific_prefix":
            for action in bpy.data.actions:
                if fnmatch.fnmatchcase(action.name, obj.bfu_prefix_name_to_export+"*"):
                    TargetActionToExport.append(action)

        elif obj.bfu_anim_action_export_enum == "export_auto":
            TargetActionToExport = self.GetCachedExportAutoActionList(obj)

        return TargetActionToExport


class AssetToExport:
    def __init__(self, obj, action, asset_type):
        self.name = obj.name
        self.obj = obj
        self.obj_list = []
        self.action = action
        self.asset_type = asset_type


class BFU_FinalExportAssetCache(bpy.types.PropertyGroup):

    def GetFinalAssetList(self) -> AssetToExport:
        # Returns all assets that will be exported

        def getHaveParentToExport(obj):
            if obj.parent is not None:
                if obj.parent.bfu_export_type == 'export_recursive':
                    return obj.parent
                else:
                    return getHaveParentToExport(obj.parent)
            else:
                return None

        scene = bpy.context.scene
        export_filter = scene.bfu_export_selection_filter

        TargetAssetToExport = []  # Obj, Action, type

        objList = []
        collectionList = []

        if export_filter == "default":
            objList = bfu_utils.GetAllobjectsByExportType("export_recursive")
            collection_asset_cache = GetCollectionAssetCache()
            collection_export_asset_list = collection_asset_cache.GetCollectionAssetList()
            for col_asset in collection_export_asset_list:
                collectionList.append(col_asset.name)

        elif export_filter == "only_object" or export_filter == "only_object_action":
            recuList = bfu_utils.GetAllobjectsByExportType("export_recursive")

            for obj in bpy.context.selected_objects:
                if obj in recuList:
                    if obj not in objList:
                        objList.append(obj)
                parentTarget = getHaveParentToExport(obj)
                if parentTarget is not None:
                    if parentTarget not in objList:
                        objList.append(parentTarget)

        for collection in collectionList:
            # Collection
            if scene.static_collection_export:
                TargetAssetToExport.append(AssetToExport(
                    collection,
                    None,
                    "Collection StaticMesh"))

        for obj in objList:
            if bfu_utils.GetAssetType(obj) == "Alembic":
                # Alembic
                if scene.alembic_export:
                    TargetAssetToExport.append(AssetToExport(
                        obj,
                        None,
                        "Alembic"))

            if bfu_utils.GetAssetType(obj) == "SkeletalMesh":

                # Skeletal Mesh
                if scene.skeletal_export:
                    if obj.bfu_modular_skeletal_mesh_mode == "all_in_one":
                        asset = AssetToExport(obj, None, "SkeletalMesh")
                        asset.name = obj.name
                        asset.obj_list = bfu_utils.GetExportDesiredChilds(obj)
                        TargetAssetToExport.append(asset)
                    elif obj.bfu_modular_skeletal_mesh_mode == "every_meshs":
                        for mesh in bfu_basics.GetChilds(obj):
                            asset = AssetToExport(obj, None, "SkeletalMesh")
                            asset.name = obj.name + obj.bfu_modular_skeletal_mesh_every_meshs_separate + mesh.name
                            asset.obj_list = [mesh]
                            TargetAssetToExport.append(asset)
                    elif obj.bfu_modular_skeletal_mesh_mode == "specified_parts":
                        for part in obj.bfu_modular_skeletal_specified_parts_meshs_template.get_template_collection():
                            asset = AssetToExport(obj, None, "SkeletalMesh")
                            asset.name = part.name
                            for mesh in part.target_meshs.get_template_collection():
                                asset.obj_list.append(mesh.mesh)
                            TargetAssetToExport.append(asset)

                # NLA
                if scene.anin_export:
                    if obj.bfu_anim_nla_use:
                        TargetAssetToExport.append(AssetToExport(
                            obj,
                            obj.animation_data,
                            "NlAnim"))
                animation_asset_cache = GetAnimationAssetCache(obj)
                animation_to_export = animation_asset_cache.GetAnimationAssetList()
                for action in animation_to_export:
                    if scene.bfu_export_selection_filter == "only_object_action":
                        if obj.animation_data:
                            if obj.animation_data.action == action:
                                TargetAssetToExport.append(AssetToExport(obj, action, "Action"))
                    else:
                        # Action
                        if scene.anin_export:
                            if bfu_utils.GetActionType(action) == "Action":
                                TargetAssetToExport.append(AssetToExport(obj, action, "Action"))

                        # Pose
                        if scene.anin_export:
                            if bfu_utils.GetActionType(action) == "Pose":
                                TargetAssetToExport.append(AssetToExport(obj, action, "Pose"))
            # Camera
            if bfu_utils.GetAssetType(obj) == "Camera" and scene.camera_export:
                TargetAssetToExport.append(AssetToExport(
                    obj,
                    None,
                    "Camera"))

            # StaticMesh
            if bfu_utils.GetAssetType(obj) == "StaticMesh" and scene.static_export:
                TargetAssetToExport.append(AssetToExport(
                    obj,
                    None,
                    "StaticMesh"))

        return TargetAssetToExport

def GetCollectionAssetCache() -> BFU_CollectionExportAssetCache:
    scene = bpy.context.scene
    return scene.collection_asset_cache

def GetAnimationAssetCache(obj) -> BFU_AnimationExportAssetCache:
    return obj.animation_asset_cache

def GetfinalAssetCache() -> BFU_FinalExportAssetCache:
    scene = bpy.context.scene
    return scene.final_asset_cache

# -------------------------------------------------------------------
#   Register & Unregister
# -------------------------------------------------------------------

classes = (

    BFU_CollectionExportAssetCache,
    BFU_AnimationExportAssetCache,
    BFU_FinalExportAssetCache,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)



    bpy.types.Scene.collection_asset_cache = bpy.props.PointerProperty(
        type=BFU_CollectionExportAssetCache,
        options={'LIBRARY_EDITABLE'},
        override={'LIBRARY_OVERRIDABLE'},
        )

    bpy.types.Object.animation_asset_cache = bpy.props.PointerProperty(
        type=BFU_AnimationExportAssetCache,
        options={'LIBRARY_EDITABLE'},
        override={'LIBRARY_OVERRIDABLE'},
        )
    
    bpy.types.Scene.final_asset_cache = bpy.props.PointerProperty(
        type=BFU_FinalExportAssetCache,
        options={'LIBRARY_EDITABLE'},
        override={'LIBRARY_OVERRIDABLE'},
        )



def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)