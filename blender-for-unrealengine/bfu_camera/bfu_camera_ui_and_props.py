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
from . import bfu_camera_write_paste_commands
from .. import bfu_basics
from .. import bbpl
from .. import languages


def get_preset_values():
    preset_values = [
        'obj.bfu_export_fbx_camera',
        'obj.bfu_fix_axis_flippings'
        ]
    return preset_values

def draw_ui_object_camera(layout: bpy.types.UILayout, obj: bpy.types.Object):
  

    if obj is None:
        return
    
    if obj.type != "CAMERA":
        return

    camera_ui = layout.column()
    scene = bpy.context.scene 
    scene.bfu_camera_properties_expanded.draw(camera_ui)
    if scene.bfu_camera_properties_expanded.is_expend():
        if obj.type == "CAMERA":
            camera_ui_pop = camera_ui.column()
            camera_ui_pop.prop(obj, 'bfu_desired_camera_type')
            if obj.bfu_desired_camera_type == "CUSTOM":
                camera_ui_pop.prop(obj, 'bfu_custom_camera_actor')
                camera_ui_pop.prop(obj, 'bfu_custom_camera_default_actor')
                camera_ui_pop.prop(obj, 'bfu_custom_camera_component')
            camera_ui_pop.prop(obj, 'bfu_export_fbx_camera')
            camera_ui_pop.prop(obj, 'bfu_fix_axis_flippings')
            camera_ui_pop.enabled = obj.bfu_export_type == "export_recursive"
            camera_ui.operator("object.bfu_copy_active_camera_data", icon="COPYDOWN")


def draw_ui_scene_camera(layout: bpy.types.UILayout):

    camera_ui = layout.column()
    scene = bpy.context.scene  
    scene.bfu_camera_tools_expanded.draw(camera_ui)
    if scene.bfu_camera_tools_expanded.is_expend():
        camera_ui.operator("object.copy_selected_cameras_data", icon="COPYDOWN")
    

# Object button
class BFU_OT_CopyActiveCameraOperator(bpy.types.Operator):
    bl_label = "Copy active camera for Unreal"
    bl_idname = "object.bfu_copy_active_camera_data"
    bl_description = "Copy active camera data. (Use CTRL+V in Unreal viewport)"

    def execute(self, context):
        obj = context.object
        result = bfu_camera_write_paste_commands.GetImportCameraScriptCommand([obj])
        if result[0]:
            bfu_basics.setWindowsClipboard(result[1])
            self.report({'INFO'}, result[2])
        else:
            self.report({'WARNING'}, result[2])
        return {'FINISHED'}

# Scene button
class BFU_OT_CopySelectedCamerasOperator(bpy.types.Operator):
    bl_label = "Copy selected camera(s) for Unreal"
    bl_idname = "object.copy_selected_cameras_data"
    bl_description = "Copy selected camera(s) data. (Use CTRL+V in Unreal viewport)"

    def execute(self, context):
        objs = context.selected_objects
        result = bfu_camera_write_paste_commands.GetImportCameraScriptCommand(objs)
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
    BFU_OT_CopyActiveCameraOperator,
    BFU_OT_CopySelectedCamerasOperator
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    
    bpy.types.Scene.bfu_camera_properties_expanded = bbpl.blender_layout.layout_accordion.add_ui_accordion(name="Camera Properties")
    bpy.types.Scene.bfu_camera_tools_expanded = bbpl.blender_layout.layout_accordion.add_ui_accordion(name="Camera")

    bpy.types.Object.bfu_export_fbx_camera = bpy.props.BoolProperty(
        name=(languages.ti('export_camera_as_fbx_name')),
        description=(languages.tt('export_camera_as_fbx_desc')),
        override={'LIBRARY_OVERRIDABLE'},
        default=False,
        )
    bpy.types.Object.bfu_fix_axis_flippings = bpy.props.BoolProperty(
        name="Fix camera axis flippings",
        description=('Disable only if you use extrem camera animation in one frame.'),
        override={'LIBRARY_OVERRIDABLE'},
        default=True,
        )
    bpy.types.Object.bfu_desired_camera_type = bpy.props.EnumProperty(
        name="Camera Type",
        description="Choose the type of camera",
        items=bfu_camera_utils.get_enum_cameras_list(),
        default=bfu_camera_utils.get_enum_cameras_default()
    )

    bpy.types.Object.bfu_custom_camera_actor = bpy.props.StringProperty(
        name="Custom Camera Actor",
        description=('Ref adress for an custom camera actor'),
        override={'LIBRARY_OVERRIDABLE'},
        default="/Script/MyModule.MyCameraActor",
        )
    bpy.types.Object.bfu_custom_camera_default_actor = bpy.props.StringProperty(
        name="Custom Camera Actor(default)",
        description=('Ref adress for an custom camera actor (default)'),
        override={'LIBRARY_OVERRIDABLE'},
        default="/Script/MyModule.Default__MyCameraActor",
        )
    bpy.types.Object.bfu_custom_camera_component = bpy.props.StringProperty(
        name="Custom Camera Component",
        description=('Ref adress for an custom camera component'),
        override={'LIBRARY_OVERRIDABLE'},
        default="/Script/MyModule.MyCameraComponent",
        )

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)

    del bpy.types.Object.bfu_custom_camera_component
    del bpy.types.Object.bfu_custom_camera_default_actor
    del bpy.types.Object.bfu_custom_camera_actor
    del bpy.types.Object.bfu_desired_camera_type
    del bpy.types.Object.bfu_fix_axis_flippings
    del bpy.types.Object.bfu_export_fbx_camera
    del bpy.types.Scene.bfu_camera_tools_expanded
    del bpy.types.Scene.bfu_camera_properties_expanded



