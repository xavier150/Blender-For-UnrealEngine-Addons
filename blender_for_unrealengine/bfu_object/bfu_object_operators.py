# SPDX-FileCopyrightText: 2018-2025 Xavier Loux (BleuRaven)
#
# SPDX-License-Identifier: GPL-3.0-or-later

# ----------------------------------------------
#  Blender For UnrealEngine
#  https://github.com/xavier150/Blender-For-UnrealEngine-Addons
# ----------------------------------------------

import bpy
from .. import bbpl
from . import bfu_object_write_paste_commands


            #object_ui.operator("object.copy_active_object_location_for_unreal", icon="COPYDOWN")
            #object_ui.operator("object.copy_active_object_rotation_for_unreal", icon="COPYDOWN")
            #object_ui.operator("object.copy_active_object_scale_for_unreal", icon="COPYDOWN")


# Scene buttons
class BFU_OT_CopyActiveObjectLocationForUnreal(bpy.types.Operator):
    bl_idname = "object.copy_active_object_location_for_unreal"
    bl_label = "Copy Active Object Location for Unreal"
    bl_description = "Copy the location of the active object to the clipboard in a format suitable for Unreal Engine"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context: bpy.types.Context):  # type: ignore
        active_object = context.active_object
        if active_object:
            result = bfu_object_write_paste_commands.get_object_location_for_unreal_script_command(active_object)
            if result[0]:
                bbpl.basics.set_windows_clipboard(result[1])
                self.report({'INFO'}, result[2])
            else:
                self.report({'WARNING'}, result[2])
            return {'FINISHED'}
        else:
            self.report({'WARNING'}, "No active object found")
            return {'CANCELLED'}
        
class BFU_OT_CopyActiveObjectRotationForUnreal(bpy.types.Operator):
    bl_idname = "object.copy_active_object_rotation_for_unreal"
    bl_label = "Copy Active Object Rotation for Unreal"
    bl_description = "Copy the rotation of the active object to the clipboard in a format suitable for Unreal Engine"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context: bpy.types.Context):  # type: ignore
        active_object = context.active_object
        if active_object:
            result = bfu_object_write_paste_commands.get_object_rotation_for_unreal_script_command(active_object)
            if result[0]:
                bbpl.basics.set_windows_clipboard(result[1])
                self.report({'INFO'}, result[2])
            else:
                self.report({'WARNING'}, result[2])
            return {'FINISHED'}
        else:
            self.report({'WARNING'}, "No active object found")
            return {'CANCELLED'}
        
class BFU_OT_CopyActiveObjectScaleForUnreal(bpy.types.Operator):
    bl_idname = "object.copy_active_object_scale_for_unreal"
    bl_label = "Copy Active Object Scale for Unreal"
    bl_description = "Copy the scale of the active object to the clipboard in a format suitable for Unreal Engine"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context: bpy.types.Context):  # type: ignore
        active_object = context.active_object
        if active_object:
            result = bfu_object_write_paste_commands.get_object_scale_for_unreal_script_command(active_object)
            if result[0]:
                bbpl.basics.set_windows_clipboard(result[1])
                self.report({'INFO'}, result[2])
            else:
                self.report({'WARNING'}, result[2])
            return {'FINISHED'}
        else:
            self.report({'WARNING'}, "No active object found")
            return {'CANCELLED'}

# -------------------------------------------------------------------
#   Register & Unregister
# -------------------------------------------------------------------

classes = (
    BFU_OT_CopyActiveObjectLocationForUnreal,
    BFU_OT_CopyActiveObjectRotationForUnreal,
    BFU_OT_CopyActiveObjectScaleForUnreal
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    



def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)


