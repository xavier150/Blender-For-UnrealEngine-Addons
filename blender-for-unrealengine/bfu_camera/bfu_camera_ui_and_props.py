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

from bpy.types import (
        Operator,
        )

from . import bfu_camera_utils
from .. import bfu_basics
from .. import bfu_utils
from .. import bfu_ui


# Object button
class BFU_OT_CopyRegularCameraButton(Operator):
    bl_label = "Copy Regular Camera for Unreal"
    bl_idname = "object.copy_regular_camera_command"
    bl_description = "Copy Regular Camera Script command"

    def execute(self, context):
        obj = context.object
        result = bfu_camera_utils.GetImportCameraScriptCommand([obj], False)
        if result[0]:
            bfu_basics.setWindowsClipboard(result[1])
            self.report({'INFO'}, result[2])
        else:
            self.report({'WARNING'}, result[2])
        return {'FINISHED'}

class BFU_OT_CopyCineCameraButton(Operator):
    bl_label = "Copy Cine Camera for Unreal"
    bl_idname = "object.copy_cine_camera_command"
    bl_description = "Copy Cine Camera Script command"

    def execute(self, context):
        obj = context.object
        result = bfu_camera_utils.GetImportCameraScriptCommand([obj], True)
        if result[0]:
            bfu_basics.setWindowsClipboard(result[1])
            self.report({'INFO'}, result[2])
        else:
            self.report({'WARNING'}, result[2])
        return {'FINISHED'}

# Scene button
class BFU_OT_CopyRegularCamerasButton(Operator):
    bl_label = "Copy Regular Cameras for Unreal"
    bl_idname = "object.copy_regular_cameras_command"
    bl_description = "Copy Regular Cameras Script command"

    def execute(self, context):
        objs = context.selected_objects
        result = bfu_camera_utils.GetImportCameraScriptCommand(objs, False)
        if result[0]:
            bfu_basics.setWindowsClipboard(result[1])
            self.report({'INFO'}, result[2])
        else:
            self.report({'WARNING'}, result[2])
        return {'FINISHED'}

class BFU_OT_CopyCineCamerasButton(Operator):
    bl_label = "Copy Cine Cameras for Unreal"
    bl_idname = "object.copy_cine_cameras_command"
    bl_description = "Copy Cine Cameras Script command"

    def execute(self, context):
        objs = context.selected_objects
        result = bfu_camera_utils.GetImportCameraScriptCommand(objs, True)
        if result[0]:
            bfu_basics.setWindowsClipboard(result[1])
            self.report({'INFO'}, result[2])
        else:
            self.report({'WARNING'}, result[2])
        return {'FINISHED'}


# -------------------------------------------------------------------
#   Register & Unregister
# -------------------------------------------------------------------

classes = (
    BFU_OT_CopyRegularCameraButton,
    BFU_OT_CopyCineCameraButton,
    BFU_OT_CopyRegularCamerasButton,
    BFU_OT_CopyCineCamerasButton,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
