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
from ..bbpl.blender_layout import layout_doc_button


def draw_tools_ui(layout: bpy.types.UILayout, context: bpy.types.Context):
    scene = context.scene
    
    accordion = bbpl.blender_layout.layout_accordion.get_accordion(scene, "bfu_tools_socket_properties_expanded")
    if accordion:
        _, panel = accordion.draw(layout)
        if accordion.is_expanded() and panel:

            # Draw user documentation button
            layout_doc_button.add_doc_page_operator(
                layout=panel, 
                url="https://github.com/xavier150/Blender-For-UnrealEngine-Addons/wiki/Sockets",
                text="Sockets Documentation"
            )

            draw_convert_static_socket(panel, context)
            draw_convert_skeletal_socket(panel, context)

            obj = bpy.context.object
            if obj is not None:
                if obj.type == "EMPTY":
                    socketName = panel.column()
                    socketName.prop(obj, "bfu_use_socket_custom_name")
                    socketNameText = socketName.column()
                    socketNameText.enabled = bfu_socket_props.get_object_use_socket_custom_name(obj)
                    socketNameText.prop(obj, "bfu_socket_custom_name")

            copy_skeletalsocket_buttons = panel.column()
            copy_skeletalsocket_buttons.enabled = False
            copy_skeletalsocket_buttons.operator(
                "object.copy_skeletalsocket_command",
                icon='COPYDOWN')
            if obj is not None:
                if obj.type == "ARMATURE":
                    copy_skeletalsocket_buttons.enabled = True
                

def draw_convert_static_socket(layout: bpy.types.UILayout, context: bpy.types.Context) -> bpy.types.UILayout:
    def draw_convert_static_socket_tips(layout: bpy.types.UILayout, context: bpy.types.Context) -> bool:
        # Draw user tips and check can use buttons
        ready_for_convert_socket = False
        if not bbpl.utils.active_mode_is("OBJECT"):
            layout.label(text="Switch to Object Mode.", icon='INFO')
        else:

            if bbpl.utils.found_type_in_selection("EMPTY", False):
                if bbpl.utils.active_type_is_not("ARMATURE") and bpy.context.selected_objects and len(bpy.context.selected_objects) > 1:
                    layout.label(text="Click on button for convert to Socket.", icon='INFO')
                    ready_for_convert_socket = True
                else:
                    layout.label(text="Select with [SHIFT] the socket owner.", icon='INFO')
            else:
               layout.label(text="Please select your socket Empty(s). Active should be the owner.", icon='INFO')
        return ready_for_convert_socket

    # Draw buttons
    panel = layout.box()
    ready_for_convert_socket = draw_convert_static_socket_tips(panel, context)
    buttons_ui = panel.row().split(factor=0.80)
    column_button_ui = buttons_ui.column()
    column_button_ui.enabled = ready_for_convert_socket
    column_button_ui.operator("object.converttostaticsocket", icon='OUTLINER_DATA_EMPTY')
    return panel



def draw_convert_skeletal_socket(layout: bpy.types.UILayout, context: bpy.types.Context) -> bpy.types.UILayout:
    
    addon_prefs = bfu_addon_prefs.get_addon_preferences()
    if addon_prefs.use_generated_scripts == False:
        return layout
    
    def draw_convert_skeletal_socket_tips(layout: bpy.types.UILayout, context: bpy.types.Context) -> bool:
        # Draw user tips and check can use buttons (skeletal_socket)
        ready_for_convert_skeletal_socket = False
        if not bbpl.utils.active_mode_is("OBJECT"):
            if not bbpl.utils.active_type_is("ARMATURE"):
                if not bbpl.utils.found_type_in_selection("EMPTY"):
                    layout.label(text="Switch to Object Mode.", icon='INFO')
        else:
            if bbpl.utils.found_type_in_selection("EMPTY"):
                if bbpl.utils.active_type_is("ARMATURE") and bpy.context.selected_objects and len(bpy.context.selected_objects) > 1:
                    layout.label(text="Switch to Pose Mode.", icon='INFO')
                else:
                    layout.label(text="Select with [SHIFT] the socket owner. (Armature)", icon='INFO')
            else:
                layout.label(text="Select your socket Empty(s).", icon='INFO')

        if bbpl.utils.active_mode_is("POSE") and bbpl.utils.active_type_is("ARMATURE") and bbpl.utils.found_type_in_selection("EMPTY"):
            if  bpy.context.selected_pose_bones and len(bpy.context.selected_pose_bones) > 0:
                layout.label(text="Click on button for convert to Socket.", icon='INFO')
                ready_for_convert_skeletal_socket = True
            else:
                layout.label(text="Select the owner bone.", icon='INFO')
        return ready_for_convert_skeletal_socket

    # Draw buttons (skeletal_socket)
    panel = layout.box()
    ready_for_convert_skeletal_socket = draw_convert_skeletal_socket_tips(panel, context)
    buttons_ui = panel.row().split(factor=0.80)
    column_button_ui = buttons_ui.column()
    column_button_ui.enabled = ready_for_convert_skeletal_socket
    column_button_ui.operator("object.converttoskeletalsocket",icon='OUTLINER_DATA_EMPTY')
    return panel
        