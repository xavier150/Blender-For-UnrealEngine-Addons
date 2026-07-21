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
        if not bbpl.utils.active_mode_is("OBJECT"):
            layout.label(text="(1/4) Switch to Object Mode.", icon='INFO')
            return False

        if not bbpl.utils.found_type_in_selection("EMPTY", True):
            layout.label(text="(2/4) Select socket Empty(s).", icon='INFO')
            return False

        if not (
            bbpl.utils.active_type_is_not("ARMATURE")
            and bpy.context.selected_objects
            and len(bpy.context.selected_objects) > 1
        ):
            layout.label(text="(3/4) Select with [SHIFT] the socket owner.", icon='INFO')
            return False

        layout.label(text="(4/4) Click on button to convert to Socket. (Active is the owner)", icon='INFO')
        return True

    # Draw buttons
    panel = layout.box()
    is_ready = draw_convert_static_socket_tips(panel, context)
    buttons_ui = panel.row().split(factor=0.80)
    column_button_ui = buttons_ui.column()
    column_button_ui.enabled = is_ready
    column_button_ui.operator("object.converttostaticsocket", icon='OUTLINER_DATA_EMPTY')
    return panel



def draw_convert_skeletal_socket(layout: bpy.types.UILayout, context: bpy.types.Context) -> bpy.types.UILayout:
    
    addon_prefs = bfu_addon_prefs.get_addon_preferences()
    if addon_prefs.use_generated_scripts == False:
        return layout
    
    def draw_convert_skeletal_socket_tips(layout: bpy.types.UILayout, context: bpy.types.Context) -> bool:
        # Draw user tips and check can use buttons (skeletal_socket)
        has_empty_selection = bbpl.utils.found_type_in_selection("EMPTY")
        has_owner_selected = (
            bbpl.utils.active_type_is("ARMATURE")
            and bpy.context.selected_objects
            and len(bpy.context.selected_objects) > 1
        )



        if not bbpl.utils.active_mode_is("OBJECT") and not (has_empty_selection or has_owner_selected):
            layout.label(text="(1/6) Switch to Object Mode.", icon='INFO')
            return False

        if not has_empty_selection:
            layout.label(text="(2/6) Select your socket Empty(s).", icon='INFO')
            return False

        if not has_owner_selected:
            layout.label(text="(3/6) Select with [SHIFT] the socket owner. (Armature)", icon='INFO')
            return False

        if not bbpl.utils.active_mode_is("POSE"):
            layout.label(text="(4/6) Switch to Pose Mode.", icon='INFO')
            return False

        if not bpy.context.selected_pose_bones or len(bpy.context.selected_pose_bones) == 0:
            layout.label(text="(5/6) Select the owner bone.", icon='INFO')
            return False

        layout.label(text="(6/6) Click on button for convert to Socket.", icon='INFO')
        return True

    # Draw buttons (skeletal_socket)
    panel = layout.box()
    is_ready = draw_convert_skeletal_socket_tips(panel, context)
    buttons_ui = panel.row().split(factor=0.80)
    column_button_ui = buttons_ui.column()
    column_button_ui.enabled = is_ready
    column_button_ui.operator("object.converttoskeletalsocket",icon='OUTLINER_DATA_EMPTY')
    return panel
        