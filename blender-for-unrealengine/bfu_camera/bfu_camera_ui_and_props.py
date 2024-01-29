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
from . import bfu_camera_utils
from .. import bfu_basics
from .. import bfu_utils
from .. import bfu_ui
from .. import bbpl
from .. import languages
from ..bbpl.blender_layout.layout_expend_section.types import (
        BBPL_UI_ExpendSection,
        )

def get_preset_values():
    preset_values = [
        'obj.bfu_export_fbx_camera',
        'obj.bfu_fix_axis_flippings'
        ]
    return preset_values

def draw_ui_object_camera(layout: bpy.types.UILayout, obj: bpy.types.Object):
    scene = bpy.context.scene   

    if obj is None:
        return
    
    if obj.type != "CAMERA":
        return

    camera_ui = layout.column()
    scene.bfu_export_filter_properties_expanded.draw(camera_ui)
    if scene.bfu_export_filter_properties_expanded.is_expend():
        if obj.type == "CAMERA":

            camera_ui_pop = camera_ui.column()
            camera_ui_pop.prop(obj, 'bfu_export_fbx_camera')
            camera_ui_pop.prop(obj, 'bfu_fix_axis_flippings')
            camera_ui_pop.enabled = obj.bfu_export_type == "export_recursive"
            
            camera_ui.operator("object.copy_regular_camera_command", icon="COPYDOWN")
            camera_ui.operator("object.copy_cine_camera_command", icon="COPYDOWN")


def draw_ui_scene_camera(layout: bpy.types.UILayout, obj: bpy.types.Object):
    return
    

# Object button
class BFU_OT_CopyRegularCameraButton(bpy.types.Operator):
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

class BFU_OT_CopyCineCameraButton(bpy.types.Operator):
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
class BFU_OT_CopyRegularCamerasButton(bpy.types.Operator):
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

class BFU_OT_CopyCineCamerasButton(bpy.types.Operator):
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

class BFU_UI_CamerasExpendSection(BBPL_UI_ExpendSection):
    pass

# -------------------------------------------------------------------
#   Register & Unregister
# -------------------------------------------------------------------

classes = (
    BFU_OT_CopyRegularCameraButton,
    BFU_OT_CopyCineCameraButton,
    BFU_OT_CopyRegularCamerasButton,
    BFU_OT_CopyCineCamerasButton,
    BFU_UI_CamerasExpendSection
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    
    bpy.types.Scene.bfu_export_filter_properties_expanded = bpy.props.PointerProperty(type=BFU_UI_CamerasExpendSection, name="Camera Properties")
    bpy.types.Object.bfu_export_fbx_camera = bpy.props.BoolProperty(
        name=(languages.ti('export_camera_as_fbx_name')),
        description=(languages.tt('export_camera_as_fbx_desc')),
        override={'LIBRARY_OVERRIDABLE'},
        default=False,
        )
    bpy.types.Object.bfu_fix_axis_flippings = bpy.props.BoolProperty(
        name="Fix camera axis flippings",
        description=(
            'Disable only if you use extrem camera animation in one frame.'
            ),
        override={'LIBRARY_OVERRIDABLE'},
        default=True,
        )

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)

    del bpy.types.Object.bfu_fix_axis_flippings
    del bpy.types.Object.bfu_export_fbx_camera
    del bpy.types.Scene.bfu_export_filter_properties_expanded
