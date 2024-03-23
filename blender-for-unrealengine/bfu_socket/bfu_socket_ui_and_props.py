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
from .. import bfu_basics
from .. import bfu_utils
from .. import bfu_ui
from .. import bbpl

class BFU_OT_ConvertToStaticSocketButton(bpy.types.Operator):
    bl_label = "Convert to StaticMesh socket"
    bl_idname = "object.converttostaticsocket"
    bl_description = (
        "Convert selected Empty(s) to Unreal sockets" +
        " ready for export (StaticMesh)")

    def execute(self, context):
        ConvertedObj = bfu_utils.Ue4SubObj_set("ST_Socket")
        if len(ConvertedObj) > 0:
            self.report({'INFO'}, str(len(ConvertedObj)) + " object(s) of the selection have be converted to UE Socket. (Static)")
        else:
            self.report({'WARNING'}, "Please select two objects. (Active mesh object is the owner of the socket)")
        return {'FINISHED'}

class BFU_OT_ConvertToSkeletalSocketButton(bpy.types.Operator):
    bl_label = "Convert to SkeletalMesh socket"
    bl_idname = "object.converttoskeletalsocket"
    bl_description = (
        "Convert selected Empty(s)" +
        " to Unreal sockets ready for export (SkeletalMesh)")

    def execute(self, context):
        ConvertedObj = bfu_utils.Ue4SubObj_set("SKM_Socket")
        if len(ConvertedObj) > 0:
            self.report({'INFO'}, str(len(ConvertedObj)) + " object(s) of the selection have be converted to UE Socket. (Skeletal)")
        else:
            self.report({'WARNING'}, "Please select two objects. (Active armature object is the owner of the socket)")
        return {'FINISHED'}

class BFU_OT_CopySkeletalSocketButton(bpy.types.Operator):
    bl_label = "Copy Skeletal Mesh socket for Unreal"
    bl_idname = "object.copy_skeletalsocket_command"
    bl_description = "Copy Skeletal Socket Script command"

    def execute(self, context):
        obj = context.object
        if obj:
            if obj.type == "ARMATURE":
                bfu_basics.setWindowsClipboard(bfu_utils.GetImportSkeletalMeshSocketScriptCommand(obj))
                self.report(
                    {'INFO'},
                    "Skeletal sockets copied. Paste in Unreal Engine Skeletal Mesh assets for import sockets. (Ctrl+V)")
        return {'FINISHED'}

def draw_ui_scene_socket(layout: bpy.types.UILayout):
    scene = bpy.context.scene
    scene.bfu_socket_expanded.draw(layout)
    if scene.bfu_socket_expanded.is_expend():
        addon_prefs = bfu_basics.GetAddonPrefs()

        # Draw user tips and check can use buttons
        ready_for_convert_socket = False
        if not bbpl.utils.active_mode_is("OBJECT"):
            layout.label(text="Switch to Object Mode.", icon='INFO')
        else:

            if bbpl.utils.found_type_in_selection("EMPTY", False):
                if bbpl.utils.active_type_is_not("ARMATURE") and len(bpy.context.selected_objects) > 1:
                    layout.label(text="Click on button for convert to Socket.", icon='INFO')
                    ready_for_convert_socket = True
                else:
                    layout.label(text="Select with [SHIFT] the socket owner.", icon='INFO')
            else:
                layout.label(text="Please select your socket Empty(s). Active should be the owner.", icon='INFO')

        # Draw buttons
        convertButtons = layout.row().split(factor=0.80)
        convertStaticSocketButtons = convertButtons.column()
        convertStaticSocketButtons.enabled = ready_for_convert_socket
        convertStaticSocketButtons.operator("object.converttostaticsocket", icon='OUTLINER_DATA_EMPTY')


        if addon_prefs.useGeneratedScripts:

            # Draw user tips and check can use buttons (skeletal_socket)
            ready_for_convert_skeletal_socket = False
            if not bbpl.utils.active_mode_is("OBJECT"):
                if not bbpl.utils.active_type_is("ARMATURE"):
                    if not bbpl.utils.found_type_in_selection("EMPTY"):
                        layout.label(text="Switch to Object Mode.", icon='INFO')
            else:
                if bbpl.utils.found_type_in_selection("EMPTY"):
                    if bbpl.utils.active_type_is("ARMATURE") and len(bpy.context.selected_objects) > 1:
                        layout.label(text="Switch to Pose Mode.", icon='INFO')
                    else:
                        layout.label(text="Select with [SHIFT] the socket owner. (Armature)", icon='INFO')
                else:
                    layout.label(text="Select your socket Empty(s).", icon='INFO')

            if bbpl.utils.active_mode_is("POSE") and bbpl.utils.active_type_is("ARMATURE") and bbpl.utils.found_type_in_selection("EMPTY"):
                if len(bpy.context.selected_pose_bones) > 0:
                    layout.label(text="Click on button for convert to Socket.", icon='INFO')
                    ready_for_convert_skeletal_socket = True
                else:
                    layout.label(text="Select the owner bone.", icon='INFO')

            # Draw buttons (skeletal_socket)
            convertButtons = layout.row().split(factor=0.80)
            convertSkeletalSocketButtons = convertButtons.column()
            convertSkeletalSocketButtons.enabled = ready_for_convert_skeletal_socket
            convertSkeletalSocketButtons.operator("object.converttoskeletalsocket",icon='OUTLINER_DATA_EMPTY')
            
        obj = bpy.context.object
        if obj is not None:
            if obj.type == "EMPTY":
                socketName = layout.column()
                socketName.prop(obj, "bfu_use_socket_custom_Name")
                socketNameText = socketName.column()
                socketNameText.enabled = obj.bfu_use_socket_custom_Name
                socketNameText.prop(obj, "bfu_socket_custom_Name")

        copy_skeletalsocket_buttons = layout.column()
        copy_skeletalsocket_buttons.enabled = False
        copy_skeletalsocket_buttons.operator(
            "object.copy_skeletalsocket_command",
            icon='COPYDOWN')
        if obj is not None:
            if obj.type == "ARMATURE":
                copy_skeletalsocket_buttons.enabled = True
            
        

# -------------------------------------------------------------------
#   Register & Unregister
# -------------------------------------------------------------------

classes = (
    BFU_OT_ConvertToStaticSocketButton,
    BFU_OT_ConvertToSkeletalSocketButton,
    BFU_OT_CopySkeletalSocketButton,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)

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


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)

    del bpy.types.Object.bfu_socket_custom_Name
    del bpy.types.Object.bfu_custom_camera_component
