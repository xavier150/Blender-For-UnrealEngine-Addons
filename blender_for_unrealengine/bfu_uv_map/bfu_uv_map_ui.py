# SPDX-FileCopyrightText: Xavier Loux (BleuRaven)
#
# SPDX-License-Identifier: GPL-3.0-or-later

# ----------------------------------------------
#  Blender For UnrealEngine
#  https://github.com/xavier150/Blender-For-UnrealEngine-Addons
# ----------------------------------------------


import bpy
from .. import bfu_utils
from .. import bfu_ui
from .. import bbpl
from .. import bfu_export_control


def draw_obj_ui(layout: bpy.types.UILayout, context: bpy.types.Context, obj: bpy.types.Object):

    scene = bpy.context.scene 

    # Hide filters
    if obj is None:
        return
    if not bfu_utils.draw_proxy_propertys(obj):
        return
    if bfu_export_control.bfu_export_control_utils.is_not_export_recursive(obj):
        return

    if bfu_ui.bfu_ui_utils.DisplayPropertyFilter("OBJECT", "MISC"):
        accordion = bbpl.blender_layout.layout_accordion.get_accordion(scene, "bfu_object_uv_map_properties_expanded")
        _, panel = accordion.draw(layout)
        if accordion.is_expanded():
            # Geometry Node Uv
            bfu_convert_geometry_node_attribute_to_uv = panel.column()
            convert_geometry_node_attribute_to_uv_use = bfu_convert_geometry_node_attribute_to_uv.row()
            convert_geometry_node_attribute_to_uv_use.prop(obj, 'bfu_convert_geometry_node_attribute_to_uv')
            bbpl.blender_layout.layout_doc_button.add_doc_page_operator(convert_geometry_node_attribute_to_uv_use, url="https://github.com/xavier150/Blender-For-UnrealEngine-Addons/wiki/UV-Maps#geometry-node-uv")
            bfu_convert_geometry_node_attribute_to_uv_name = bfu_convert_geometry_node_attribute_to_uv.column()
            bfu_convert_geometry_node_attribute_to_uv_name.prop(obj, 'bfu_convert_geometry_node_attribute_to_uv_name')
            bfu_convert_geometry_node_attribute_to_uv_name.enabled = obj.bfu_convert_geometry_node_attribute_to_uv

            # Extreme UV Scale
            ui_correct_extrem_uv_scale = panel.column()
            ui_correct_extrem_uv_scale_use = ui_correct_extrem_uv_scale.row()
            ui_correct_extrem_uv_scale_use.prop(obj, 'bfu_use_correct_extrem_uv_scale')
            bbpl.blender_layout.layout_doc_button.add_doc_page_operator(ui_correct_extrem_uv_scale_use, url="https://github.com/xavier150/Blender-For-UnrealEngine-Addons/wiki/UV-Maps#extreme-uv-scale")
            ui_correct_extrem_uv_scale_options = ui_correct_extrem_uv_scale.column()
            ui_correct_extrem_uv_scale_options.prop(obj, 'bfu_correct_extrem_uv_scale_step_scale')
            ui_correct_extrem_uv_scale_options.prop(obj, 'bfu_correct_extrem_uv_scale_use_absolute')
            ui_correct_extrem_uv_scale_options.enabled = obj.bfu_use_correct_extrem_uv_scale


def draw_tools_ui(layout: bpy.types.UILayout, context: bpy.types.Context):
    scene = context.scene
    accordion = bbpl.blender_layout.layout_accordion.get_accordion(scene, "bfu_tools_uv_map_properties_expanded")
    _, panel = accordion.draw(layout)
    if accordion.is_expanded():
        ready_for_correct_extrem_uv_scale = False
        obj = bpy.context.object
        if obj and obj.type == "MESH":
            if bbpl.utils.active_mode_is("EDIT"):
                ready_for_correct_extrem_uv_scale = True
            else:
                panel.label(text="Switch to Edit Mode.", icon='INFO')
        else:
            panel.label(text="Select an mesh object", icon='INFO')


            # Draw buttons (correct_extrem_uv)
        Buttons_correct_extrem_uv_scale = panel.row()
        Button_correct_extrem_uv_scale = Buttons_correct_extrem_uv_scale.column()
        Button_correct_extrem_uv_scale.enabled = ready_for_correct_extrem_uv_scale
        Button_correct_extrem_uv_scale.operator("object.correct_extrem_uv", icon='UV')
        bbpl.blender_layout.layout_doc_button.add_doc_page_operator(Buttons_correct_extrem_uv_scale, url="https://github.com/xavier150/Blender-For-UnrealEngine-Addons/wiki/UV-Maps#extreme-uv-scale")
