import bpy
import os
import time
from . import bfu_utils


class BFU_OT_FileExport(bpy.types.PropertyGroup):
    name: bpy.props.StringProperty()
    path: bpy.props.StringProperty()
    type: bpy.props.StringProperty()  # FBX, AdditionalTrack

    def __init__(self, name):
        pass

    def GetRelativePath(self):
        return os.path.join(self.path, self.name)

    def GetAbsolutePath(self):
        return os.path.join(bpy.path.abspath(self.path), self.name)


class BFU_OT_UnrealExportedAsset(bpy.types.PropertyGroup):
    # [AssetName , AssetType , ExportPath, ExportTime]

    asset_name: bpy.props.StringProperty(default="None")
    skeleton_name: bpy.props.StringProperty(default="None")
    asset_type: bpy.props.StringProperty(default="None")  # return from GetAssetType()
    folder_name: bpy.props.StringProperty(default="")
    files: bpy.props.CollectionProperty(type=BFU_OT_FileExport)
    object: bpy.props.PointerProperty(type=bpy.types.Object)
    collection: bpy.props.PointerProperty(type=bpy.types.Collection)
    export_start_time: bpy.props.FloatProperty(default=0)
    export_end_time: bpy.props.FloatProperty(default=0)
    export_success: bpy.props.BoolProperty(default=False)

    def StartAssetExport(self, obj=None, action=None, collection=None):

        if obj and action:
            self.asset_name = bfu_utils.GetActionExportFileName(obj, action, "")

        self.export_start_time = time.perf_counter()

    def EndAssetExport(self, success):
        self.export_end_time = time.perf_counter()
        self.export_success = success

    def GetExportTime(self):
        return self.export_end_time - self.export_start_time

    def GetFileByType(self, type: str):
        for file in self.files:
            if file.type == type:
                return file
        print("File type not found in this assets:", type)

    def GetFilename(self, fileType=".fbx"):
        if self.asset_type == "Collection StaticMesh":
            return bfu_utils.GetCollectionExportFileName(self.collection.name, fileType)
        else:
            return bfu_utils.GetObjExportFileName(self.object, fileType)


classes = (
)


def register():
    """
    Register.
    """
    from bpy.utils import register_class

    for cls in classes:
        register_class(cls)

    bpy.utils.register_class(BFU_OT_FileExport)
    bpy.utils.register_class(BFU_OT_UnrealExportedAsset)
    bpy.types.Scene.UnrealExportedAssetsList = bpy.props.CollectionProperty(
        type=BFU_OT_UnrealExportedAsset)


def unregister():
    """
    unregister.
    """
    from bpy.utils import unregister_class

    for cls in reversed(classes):
        unregister_class(cls)

    bpy.utils.unregister_class(BFU_OT_FileExport)
    bpy.utils.unregister_class(BFU_OT_UnrealExportedAsset)
