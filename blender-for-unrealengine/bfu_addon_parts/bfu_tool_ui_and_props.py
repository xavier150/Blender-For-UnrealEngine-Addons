import bpy

from bpy.props import (
        StringProperty,
        BoolProperty,
        )

from bpy.types import (
        Operator,
        )

from .. import bfu_basics
from .. import bfu_utils
from .. import bfu_ui


class BFU_PT_BlenderForUnrealTool(bpy.types.Panel):
    # Tool panel with Collisions And Sockets

    bl_idname = "BFU_PT_BlenderForUnrealTool"
    bl_label = "Tool"
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


    class BFU_OT_ConvertToStaticSocketButton(Operator):
        bl_label = "Convert to StaticMesh socket"
        bl_idname = "object.converttostaticsocket"
        bl_description = (
            "Convert selected Empty(s) to Unreal sockets" +
            " ready for export (StaticMesh)")

        def execute(self, context):
            ConvertedObj = bfu_utils.Ue4SubObj_set("ST_Socket")
            if len(ConvertedObj) > 0:
                self.report(
                    {'INFO'},
                    str(len(ConvertedObj)) +
                    " object(s) of the selection have be" +
                    " converted to UE4 Socket. (Static)")
            else:
                self.report(
                    {'WARNING'},
                    "Please select two objects." +
                    " (Active object is the owner of the socket)")
            return {'FINISHED'}

    class BFU_OT_ConvertToSkeletalSocketButton(Operator):
        bl_label = "Convert to SkeletalMesh socket"
        bl_idname = "object.converttoskeletalsocket"
        bl_description = (
            "Convert selected Empty(s)" +
            " to Unreal sockets ready for export (SkeletalMesh)")

        def execute(self, context):
            ConvertedObj = bfu_utils.Ue4SubObj_set("SKM_Socket")
            if len(ConvertedObj) > 0:
                self.report(
                    {'INFO'},
                    str(len(ConvertedObj)) +
                    " object(s) of the selection have" +
                    " be converted to UE4 Socket. (Skeletal)")
            else:
                self.report(
                    {'WARNING'},
                    "Please select two objects. " +
                    "(Active object is the owner of the socket)")
            return {'FINISHED'}

    class BFU_OT_CopySkeletalSocketButton(Operator):
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

    class BFU_OT_ComputAllLightMap(Operator):
        bl_label = "Calculate all surface area"
        bl_idname = "object.computalllightmap"
        bl_description = (
            "Click to calculate the surface of the all object in the scene"
            )

        def execute(self, context):
            updated = bfu_utils.UpdateAreaLightMapList()
            self.report(
                {'INFO'},
                "The light maps of " + str(updated) +
                " object(s) have been updated."
                )
            return {'FINISHED'}

    def draw(self, context):

        addon_prefs = bfu_basics.GetAddonPrefs()
        layout = self.layout
        scene = bpy.context.scene
        obj = context.object

        def ActiveModeIs(targetMode):
            # Return True is active mode ==
            obj = bpy.context.active_object
            if obj is not None:
                if obj.mode == targetMode:
                    return True
            return False

        def ActiveTypeIs(targetType):
            # Return True is active type ==
            obj = bpy.context.active_object
            if obj is not None:
                if obj.type == targetType:
                    return True
            return False

        def ActiveTypeIsNot(targetType):
            # Return True is active type ==
            obj = bpy.context.active_object
            if obj is not None:
                if obj.type != targetType:
                    return True
            return False

        def FoundTypeInSelect(targetType, include_active=True):
            # Return True if a specific type is found
            select = bpy.context.selected_objects
            if not include_active:
                if bpy.context.active_object:
                    if bpy.context.active_object in select:
                        select.remove(bpy.context.active_object)

            for obj in select:
                if obj.type == targetType:
                    return True
            return False

        ready_for_convert_collider = False
        ready_for_convert_socket = False


        scene.bfu_camera_expanded.draw(layout)
        if scene.bfu_camera_expanded.is_expend():
            copy_camera_buttons = layout.column()
            copy_camera_buttons.operator("object.copy_regular_cameras_command", icon="COPYDOWN")
            copy_camera_buttons.operator("object.copy_cine_cameras_command", icon="COPYDOWN")


        scene.bfu_collision_socket_expanded.draw(layout)
        if scene.bfu_collision_socket_expanded.is_expend():
            if not ActiveModeIs("OBJECT"):
                layout.label(text="Switch to Object Mode.", icon='INFO')
            else:
                if FoundTypeInSelect("MESH", False):
                    if ActiveTypeIsNot("ARMATURE") and len(bpy.context.selected_objects) > 1:
                        layout.label(text="Click on button for convert to collider.", icon='INFO')
                        ready_for_convert_collider = True
                    else:
                        layout.label(text="Select with [SHIFT] the collider owner.", icon='INFO')

                elif FoundTypeInSelect("EMPTY", False):
                    if ActiveTypeIsNot("ARMATURE") and len(bpy.context.selected_objects) > 1:
                        layout.label(text="Click on button for convert to Socket.", icon='INFO')
                        ready_for_convert_socket = True
                    else:
                        layout.label(text="Select with [SHIFT] the socket owner.", icon='INFO')
                else:
                    layout.label(text="Select your collider Object(s) or socket Empty(s).", icon='INFO')

            convertButtons = layout.row().split(factor=0.80)
            convertStaticCollisionButtons = convertButtons.column()
            convertStaticCollisionButtons.enabled = ready_for_convert_collider
            convertStaticCollisionButtons.operator("object.converttoboxcollision", icon='MESH_CUBE')
            convertStaticCollisionButtons.operator("object.converttoconvexcollision", icon='MESH_ICOSPHERE')
            convertStaticCollisionButtons.operator("object.converttocapsulecollision", icon='MESH_CAPSULE')
            convertStaticCollisionButtons.operator("object.converttospherecollision", icon='MESH_UVSPHERE')

            convertButtons = layout.row().split(factor=0.80)
            convertStaticSocketButtons = convertButtons.column()
            convertStaticSocketButtons.enabled = ready_for_convert_socket
            convertStaticSocketButtons.operator(
                "object.converttostaticsocket",
                icon='OUTLINER_DATA_EMPTY')

            if addon_prefs.useGeneratedScripts:

                ready_for_convert_skeletal_socket = False
                if not ActiveModeIs("OBJECT"):
                    if not ActiveTypeIs("ARMATURE"):
                        if not FoundTypeInSelect("EMPTY"):
                            layout.label(text="Switch to Object Mode.", icon='INFO')
                else:
                    if FoundTypeInSelect("EMPTY"):
                        if ActiveTypeIs("ARMATURE") and len(bpy.context.selected_objects) > 1:
                            layout.label(text="Switch to Pose Mode.", icon='INFO')
                        else:
                            layout.label(text="Select with [SHIFT] the socket owner. (Armature)", icon='INFO')
                    else:
                        layout.label(text="Select your socket Empty(s).", icon='INFO')

                if ActiveModeIs("POSE") and ActiveTypeIs("ARMATURE") and FoundTypeInSelect("EMPTY"):
                    if len(bpy.context.selected_pose_bones) > 0:
                        layout.label(text="Click on button for convert to Socket.", icon='INFO')
                        ready_for_convert_skeletal_socket = True
                    else:
                        layout.label(text="Select the owner bone.", icon='INFO')

                convertButtons = self.layout.row().split(factor=0.80)
                convertSkeletalSocketButtons = convertButtons.column()
                convertSkeletalSocketButtons.enabled = ready_for_convert_skeletal_socket
                convertSkeletalSocketButtons.operator(
                    "object.converttoskeletalsocket",
                    icon='OUTLINER_DATA_EMPTY')

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

        scene.bfu_lightmap_expanded.draw(layout)
        if scene.bfu_lightmap_expanded.is_expend():
            checkButton = layout.column()
            checkButton.operator("object.computalllightmap", icon='TEXTURE')

# -------------------------------------------------------------------
#   Register & Unregister
# -------------------------------------------------------------------

classes = (
    BFU_PT_BlenderForUnrealTool,
    BFU_PT_BlenderForUnrealTool.BFU_OT_ConvertToStaticSocketButton,
    BFU_PT_BlenderForUnrealTool.BFU_OT_ConvertToSkeletalSocketButton,
    BFU_PT_BlenderForUnrealTool.BFU_OT_CopySkeletalSocketButton,
    BFU_PT_BlenderForUnrealTool.BFU_OT_ComputAllLightMap,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
