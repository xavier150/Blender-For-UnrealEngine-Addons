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
from . import bfu_spline_utils
from . import bfu_spline_write_paste_commands
from .. import bfu_basics
from .. import bbpl
from .. import languages


def get_preset_values():
    preset_values = [
        'obj.bfu_export_fbx_spline',
        'obj.bfu_desired_spline_type',
        'obj.bfu_custom_spline_component',
        'obj.bfu_export_spline_as_static_mesh'
        ]
    return preset_values

def draw_ui_object_spline(layout: bpy.types.UILayout, obj: bpy.types.Object):
  

    if obj is None:
        return
    
    if obj.type != "CURVE":
        return

    spline_ui = layout.column()
    scene = bpy.context.scene 
    scene.bfu_spline_properties_expanded.draw(spline_ui)
    if scene.bfu_spline_properties_expanded.is_expend():
        if obj.type == "CURVE":
            spline_ui_pop = spline_ui.column()
            spline_ui_pop.prop(obj, 'bfu_export_spline_as_static_mesh')
            if obj.bfu_export_spline_as_static_mesh is False:
                spline_ui_pop.prop(obj, 'bfu_desired_spline_type')
                if obj.bfu_desired_spline_type == "CUSTOM":
                    spline_ui_pop.prop(obj, 'bfu_custom_spline_component')
                spline_ui_pop.prop(obj, 'bfu_export_fbx_spline')
                spline_ui_pop.enabled = obj.bfu_export_type == "export_recursive"
                spline_ui.operator("object.bfu_copy_active_spline_data", icon="COPYDOWN")


def draw_ui_scene_spline(layout: bpy.types.UILayout):

    spline_ui = layout.column()
    scene = bpy.context.scene  
    scene.bfu_spline_tools_expanded.draw(spline_ui)
    if scene.bfu_spline_tools_expanded.is_expend():
        spline_ui.operator("object.copy_selected_splines_data", icon="COPYDOWN")
    

# Object button
class BFU_OT_CopyActivesplineOperator(bpy.types.Operator):
    bl_label = "Copy active spline for Unreal"
    bl_idname = "object.bfu_copy_active_spline_data"
    bl_description = "Copy active spline data. (Use CTRL+V in Unreal viewport)"

    def execute(self, context):
        obj = context.object
        result = bfu_spline_write_paste_commands.GetImportSplineScriptCommand([obj])
        if result[0]:
            bfu_basics.setWindowsClipboard(result[1])
            self.report({'INFO'}, result[2])
        else:
            self.report({'WARNING'}, result[2])
        return {'FINISHED'}

# Scene button
class BFU_OT_CopySelectedsplinesOperator(bpy.types.Operator):
    bl_label = "Copy selected spline(s) for Unreal"
    bl_idname = "object.copy_selected_splines_data"
    bl_description = "Copy selected spline(s) data. (Use CTRL+V in Unreal viewport)"

    def execute(self, context):
        objs = context.selected_objects
        result = bfu_spline_write_paste_commands.GetImportSplineScriptCommand(objs)
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
    BFU_OT_CopyActivesplineOperator,
    BFU_OT_CopySelectedsplinesOperator
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    
    bpy.types.Scene.bfu_spline_properties_expanded = bbpl.blender_layout.layout_accordion.add_ui_accordion(name="Spline Properties")
    bpy.types.Scene.bfu_spline_tools_expanded = bbpl.blender_layout.layout_accordion.add_ui_accordion(name="Spline")

    bpy.types.Object.bfu_export_fbx_spline = bpy.props.BoolProperty(
        name=(languages.ti('export_spline_as_fbx_name')),
        description=(languages.tt('export_spline_as_fbx_desc')),
        override={'LIBRARY_OVERRIDABLE'},
        default=False,
        )

    bpy.types.Object.bfu_desired_spline_type = bpy.props.EnumProperty(
        name="Spline Type",
        description="Choose the type of spline",
        items=bfu_spline_utils.get_enum_splines_list(),
        default=bfu_spline_utils.get_enum_splines_default()
    )

    bpy.types.Object.bfu_custom_spline_component = bpy.props.StringProperty(
        name="Custom spline Component",
        description=('Ref adress for an custom spline component'),
        override={'LIBRARY_OVERRIDABLE'},
        default="/Script/Engine.MySplineComponent",
        )
    
    bpy.types.Object.bfu_export_spline_as_static_mesh = bpy.props.BoolProperty(
        name="Force staticMesh",
        description="Force export asset like a StaticMesh if is ARMATURE type",
        override={'LIBRARY_OVERRIDABLE'},
        default=False
        )

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)

    del bpy.types.Object.bfu_export_spline_as_static_mesh
    del bpy.types.Object.bfu_custom_spline_component
    del bpy.types.Object.bfu_desired_spline_type
    del bpy.types.Object.bfu_export_fbx_spline
    del bpy.types.Scene.bfu_spline_tools_expanded
    del bpy.types.Scene.bfu_spline_properties_expanded



