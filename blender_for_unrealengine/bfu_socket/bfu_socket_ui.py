# SPDX-FileCopyrightText: Xavier Loux (BleuRaven)
#
# SPDX-License-Identifier: GPL-3.0-or-later

# ----------------------------------------------
#  Blender For UnrealEngine
#  https://github.com/xavier150/Blender-For-UnrealEngine-Addons
# ----------------------------------------------


import bpy
from . import bfu_socket_props
from .. import bfu_addon_prefs
from .. import bbpl


def draw_tools_ui(layout: bpy.types.UILayout, context: bpy.types.Context):
    scene = context.scene
    
    accordion = bbpl.blender_layout.layout_accordion.get_accordion(scene, "bfu_tools_socket_properties_expanded")
    if accordion:
        _, panel = accordion.draw(layout)
        if accordion.is_expanded() and panel:
            addon_prefs = bfu_addon_prefs.get_addon_preferences()

            # Draw user tips and check can use buttons
            ready_for_convert_socket = False
            if not bbpl.utils.active_mode_is("OBJECT"):
                panel.label(text="Switch to Object Mode.", icon='INFO')
            else:

                if bbpl.utils.found_type_in_selection("EMPTY", False):
                    if bbpl.utils.active_type_is_not("ARMATURE") and len(bpy.context.selected_objects) > 1:
                        panel.label(text="Click on button for convert to Socket.", icon='INFO')
                        ready_for_convert_socket = True
                    else:
                        panel.label(text="Select with [SHIFT] the socket owner.", icon='INFO')
                else:
                    panel.label(text="Please select your socket Empty(s). Active should be the owner.", icon='INFO')

            # Draw buttons
            convertButtons = panel.row().split(factor=0.80)
            convertStaticSocketButtons = convertButtons.column()
            convertStaticSocketButtons.enabled = ready_for_convert_socket
            convertStaticSocketButtons.operator("object.converttostaticsocket", icon='OUTLINER_DATA_EMPTY')


            if addon_prefs.useGeneratedScripts:

                # Draw user tips and check can use buttons (skeletal_socket)
                ready_for_convert_skeletal_socket = False
                if not bbpl.utils.active_mode_is("OBJECT"):
                    if not bbpl.utils.active_type_is("ARMATURE"):
                        if not bbpl.utils.found_type_in_selection("EMPTY"):
                            panel.label(text="Switch to Object Mode.", icon='INFO')
                else:
                    if bbpl.utils.found_type_in_selection("EMPTY"):
                        if bbpl.utils.active_type_is("ARMATURE") and len(bpy.context.selected_objects) > 1:
                            panel.label(text="Switch to Pose Mode.", icon='INFO')
                        else:
                            panel.label(text="Select with [SHIFT] the socket owner. (Armature)", icon='INFO')
                    else:
                        panel.label(text="Select your socket Empty(s).", icon='INFO')

                if bbpl.utils.active_mode_is("POSE") and bbpl.utils.active_type_is("ARMATURE") and bbpl.utils.found_type_in_selection("EMPTY"):
                    if len(bpy.context.selected_pose_bones) > 0:
                        panel.label(text="Click on button for convert to Socket.", icon='INFO')
                        ready_for_convert_skeletal_socket = True
                    else:
                        panel.label(text="Select the owner bone.", icon='INFO')

                # Draw buttons (skeletal_socket)
                convertButtons = panel.row().split(factor=0.80)
                convertSkeletalSocketButtons = convertButtons.column()
                convertSkeletalSocketButtons.enabled = ready_for_convert_skeletal_socket
                convertSkeletalSocketButtons.operator("object.converttoskeletalsocket",icon='OUTLINER_DATA_EMPTY')
                
            obj = bpy.context.object
            if obj is not None:
                if obj.type == "EMPTY":
                    socketName = panel.column()
                    socketName.prop(obj, "bfu_use_socket_custom_Name")
                    socketNameText = socketName.column()
                    socketNameText.enabled = bfu_socket_props.get_object_use_socket_custom_Name(obj)
                    socketNameText.prop(obj, "bfu_socket_custom_Name")

            copy_skeletalsocket_buttons = panel.column()
            copy_skeletalsocket_buttons.enabled = False
            copy_skeletalsocket_buttons.operator(
                "object.copy_skeletalsocket_command",
                icon='COPYDOWN')
            if obj is not None:
                if obj.type == "ARMATURE":
                    copy_skeletalsocket_buttons.enabled = True
                
        