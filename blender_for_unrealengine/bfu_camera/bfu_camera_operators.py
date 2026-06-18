# SPDX-FileCopyrightText: Xavier Loux (BleuRaven)
#
# SPDX-License-Identifier: GPL-3.0-or-later

# ----------------------------------------------
#  Blender For UnrealEngine
#  https://github.com/xavier150/Blender-For-UnrealEngine-Addons
# ----------------------------------------------
import bpy
from .. import bbpl
from . import bfu_camera_write_paste_commands

# Object buttons
class BFU_OT_CopyActiveCameraOperator(bpy.types.Operator):
    bl_label = "Copy active camera for Unreal"
    bl_idname = "object.bfu_copy_active_camera_data"
    bl_description = "Copy active camera data. (Use CTRL+V in Unreal viewport)"

    def execute(self, context: bpy.types.Context):  # type: ignore
        obj = context.object
        result = bfu_camera_write_paste_commands.get_import_camera_script_command([obj])  # type: ignore
        if result[0]:
            bbpl.basics.set_windows_clipboard(result[1])
            self.report({'INFO'}, result[2])
        else:
            self.report({'WARNING'}, result[2])
        return {'FINISHED'}

# Scene buttons
class BFU_OT_CopySelectedCamerasOperator(bpy.types.Operator):
    bl_label = "Copy selected camera(s) for Unreal"
    bl_idname = "object.copy_selected_cameras_data"
    bl_description = "Copy selected camera(s) data. (Use CTRL+V in Unreal viewport)"

    def execute(self, context: bpy.types.Context):  # type: ignore
        objs: list[bpy.types.Object] = context.selected_objects # type: ignore
        result = bfu_camera_write_paste_commands.get_import_camera_script_command(objs)
        if result[0]:
            bbpl.basics.set_windows_clipboard(result[1])
            self.report({'INFO'}, result[2])
        else:
            self.report({'WARNING'}, result[2])
        return {'FINISHED'}
    
# -------------------------------------------------------------------
#   Register & Unregister
# -------------------------------------------------------------------

classes = (
    BFU_OT_CopyActiveCameraOperator,
    BFU_OT_CopySelectedCamerasOperator
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    



def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)


