import bpy

from bpy.props import (
        StringProperty,
        BoolProperty,
        )

from .. import bfu_utils

class BFU_PT_BlenderForUnrealDebug(bpy.types.Panel):
    # Debug panel for get dev info and test

    bl_idname = "BFU_PT_BlenderForUnrealDebug"
    bl_label = "Debug"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Unreal Engine"

    bpy.types.Object.bfu_use_socket_custom_Name = BoolProperty(
        name="Socket custom name",
        description='Use a custom name in Unreal Engine for this socket?',
        default=False
        )

    bpy.types.Object.bfu_socket_custom_Name = StringProperty(
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
            layout.label(text="GetObjExportDir(local):" + bfu_utils.GetObjExportDir(obj, False))
            layout.label(text="GetObjExportDir:" + bfu_utils.GetObjExportDir(obj, True))
            layout.label(text="GetObjExportName:" + bfu_utils.GetObjExportName(obj))
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
