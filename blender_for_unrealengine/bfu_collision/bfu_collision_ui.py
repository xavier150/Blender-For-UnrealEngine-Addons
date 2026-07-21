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
from .. import bfu_static_mesh
from .. import bfu_skeletal_mesh
from .. import bfu_export_control
from .. import bfu_addon_prefs
from .. import bfu_lod
from ..bbpl.blender_layout import layout_doc_button


def draw_ui_object(layout: bpy.types.UILayout, context: bpy.types.Context, obj: bpy.types.Object):
    scene = bpy.context.scene 
    addon_prefs = bfu_addon_prefs.get_addon_preferences()

    # Hide filters
    is_static_mesh = bfu_static_mesh.bfu_static_mesh_utils.is_static_mesh(obj)
    is_skeletal_mesh = bfu_skeletal_mesh.bfu_skeletal_mesh_utils.is_skeletal_mesh(obj)
    if addon_prefs.use_generated_scripts is False:
        return
    if not bfu_utils.draw_proxy_propertys(obj):
        return
    if bfu_export_control.bfu_export_control_utils.is_not_export_self(obj):
        return
    if is_static_mesh == False and is_skeletal_mesh == False:
        return

    if bfu_ui.bfu_ui_utils.DisplayPropertyFilter("OBJECT", "MISC"):
        accordion = bbpl.blender_layout.layout_accordion.get_accordion(scene, "bfu_object_collision_properties_expanded")
        if accordion:
            _, panel = accordion.draw(layout)
            if accordion.is_expanded() and panel:
                # StaticMesh prop
                if is_static_mesh:
                    if not bfu_lod.bfu_lod_props.get_object_export_as_lod_mesh(obj):
                        auto_generate_collision = panel.row()
                        auto_generate_collision.prop(
                            obj,
                            'bfu_auto_generate_collision'
                            )
                        collision_trace_flag = panel.row()
                        collision_trace_flag.prop(
                            obj,
                            'bfu_collision_trace_flag'
                            )
                # SkeletalMesh prop
                if is_skeletal_mesh:
                    if not bfu_lod.bfu_lod_props.get_object_export_as_lod_mesh(obj):
                        create_physics_asset = panel.row()
                        create_physics_asset.prop(obj, "bfu_create_physics_asset")
                        enable_skeletal_mesh_per_poly_collision = panel.row()
                        enable_skeletal_mesh_per_poly_collision.prop(obj, 'bfu_enable_skeletal_mesh_per_poly_collision')


def draw_tools_ui(layout: bpy.types.UILayout, context: bpy.types.Context):
    scene = context.scene
    
    accordion = bbpl.blender_layout.layout_accordion.get_accordion(scene, "bfu_tools_collision_properties_expanded")
    if accordion:
        _, panel = accordion.draw(layout)
        if accordion.is_expanded() and panel:

            # Draw user documentation button
            layout_doc_button.add_doc_page_operator(
                layout=panel, 
                url="https://github.com/xavier150/Blender-For-UnrealEngine-Addons/wiki/Collisions",
                text="Collisions Documentation"
            )

            setting_panel = panel.column(align=True)
            setting_panel.prop(scene, "bfu_keep_original_geometry_for_collision")
            setting_panel.prop(scene, "bfu_use_world_space_for_collision")
            setting_panel.prop(scene, "bfu_use_fast_bounding_box_approximation")  # New option for fast/slow MVBB

            draw_create_collision(panel, context)
            draw_convert_collider(panel, context)
        
            # Draw button toggle visibility panel
            sub_tool_panel = panel.column()
            sub_tool_panel.operator("object.toggle_collision_visibility", text="Toggle Collision Visibility", icon='HIDE_OFF')
            sub_tool_panel.operator("object.select_collision_from_current_selection", text="Select Collision from Current Selection", icon='RESTRICT_SELECT_OFF')


def draw_create_collision(layout: bpy.types.UILayout, context: bpy.types.Context) -> bpy.types.UILayout:
    def draw_create_collision_tips_steps(layout: bpy.types.UILayout, context: bpy.types.Context) -> bool:
        if not bbpl.utils.active_mode_is("OBJECT"):
            layout.label(text="(1/3) Switch to Object Mode.", icon='INFO')
            return False

        if not bbpl.utils.found_type_in_selection("MESH", True):
            layout.label(text="(2/3) Select the mesh object(s) on which to create colliders.", icon='INFO')
            return False

        if bbpl.utils.active_type_is_not("MESH"):
            layout.label(text=f"Active need to be a mesh object.", icon='ERROR')
            return False

        layout.label(text="(3/3) Click on button to create collision from selection.", icon='INFO')
        return True

    
    # Draw create new collider panel
    panel = layout.box()
    is_ready = draw_create_collision_tips_steps(panel, context)
    buttons_ui = panel.row().split(factor=0.80)
    column_button_ui = buttons_ui.column()
    column_button_ui.enabled = is_ready
    column_button_ui.operator("object.createboxcollisionfromselection", icon='MESH_CUBE')
    column_button_ui.operator("object.createconvexcollisionfromselection", icon='MESH_ICOSPHERE')
    column_button_ui.operator("object.createcapsulecollisionfromselection", icon='MESH_CAPSULE')
    column_button_ui.operator("object.createspherecollisionfromselection", icon='MESH_UVSPHERE')
    return panel

def draw_convert_collider(layout: bpy.types.UILayout, context: bpy.types.Context) -> bpy.types.UILayout:
    def draw_convert_collider_tips(layout: bpy.types.UILayout, context: bpy.types.Context) -> bool:
        if not bbpl.utils.active_mode_is("OBJECT"):
            layout.label(text="(1/4) Switch to Object Mode.", icon='INFO')
            return False

        if not bbpl.utils.found_type_in_selection("MESH", True):
            layout.label(text="(2/4) Select your collider object(s).", icon='INFO')
            return False

        if not (
            bbpl.utils.active_type_is_not("ARMATURE")
            and bpy.context.selected_objects
            and len(bpy.context.selected_objects) > 1
        ):
            layout.label(text="(3/4) Select with [SHIFT] the collider owner.", icon='INFO')
            return False

        layout.label(text="(4/4) Click on button to convert to collider. (Active is the owner)", icon='INFO')
        return True
    
    # Draw convert to collider panel
    panel = layout.box()
    is_ready = draw_convert_collider_tips(panel, context)
    buttons_ui = panel.row().split(factor=0.80)
    column_button_ui = buttons_ui.column()
    column_button_ui.enabled = is_ready
    column_button_ui.operator("object.converttoboxcollision", icon='MESH_CUBE')
    column_button_ui.operator("object.converttoconvexcollision", icon='MESH_ICOSPHERE')
    column_button_ui.operator("object.converttocapsulecollision", icon='MESH_CAPSULE')
    column_button_ui.operator("object.converttospherecollision", icon='MESH_UVSPHERE')
    return panel
