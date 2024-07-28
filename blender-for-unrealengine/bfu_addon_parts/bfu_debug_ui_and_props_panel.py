import bpy

from .. import bfu_utils
from .. import bfu_assets_manager

class BFU_PT_BlenderForUnrealDebug(bpy.types.Panel):
    # Debug panel for get dev info and test

    bl_idname = "BFU_PT_BlenderForUnrealDebug"
    bl_label = "Debug"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Unreal Engine"

    bpy.types.Object.bfu_use_socket_custom_Name = bpy.props.BoolProperty(
        name="Socket custom name",
        description='Use a custom name in Unreal Engine for this socket?',
        default=False
        )

    bpy.types.Object.bfu_socket_custom_Name = bpy.props.StringProperty(
        name="",
        description='',
        default="MySocket"
        )

    def draw(self, context):
        
        layout = self.layout
        obj = context.object
        layout.label(text="This panel is only for Debug", icon='INFO')
        
        if obj:
            layout.label(text="Full path name as Static Mesh:")
            asset_class = bfu_assets_manager.bfu_asset_manager_utils.get_asset_class(obj)
            if asset_class:
                obj_export_name = asset_class.get_obj_export_name(obj)
                obj_export_dir = asset_class.get_obj_export_directory_path(obj)
                obj_export_abs_dir = asset_class.get_obj_export_directory_path(obj, True)

            else:
                obj_export_name = "XXX"
                obj_export_dir = "XXX"
                obj_export_abs_dir = "XXX"

            layout.label(text="Obj Export Name:" + obj_export_name)
            layout.label(text="Obj Export Dir" + obj_export_dir)
            layout.label(text="Obj Export Abs Dir:" + obj_export_abs_dir)


            if obj.type == "CAMERA":
                layout.label(text="CameraPositionForUnreal (Loc):" + str(bfu_utils.EvaluateCameraPositionForUnreal(obj)[0]))
                layout.label(text="CameraPositionForUnreal (Rot):" + str(bfu_utils.EvaluateCameraPositionForUnreal(obj)[1]))
                layout.label(text="CameraPositionForUnreal (Scale):" + str(bfu_utils.EvaluateCameraPositionForUnreal(obj)[2]))

# -------------------------------------------------------------------
#   Register & Unregister
# -------------------------------------------------------------------

classes = (
    # BFU_PT_BlenderForUnrealDebug, # Unhide for dev
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
