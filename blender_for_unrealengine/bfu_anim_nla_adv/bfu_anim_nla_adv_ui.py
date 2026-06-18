# SPDX-FileCopyrightText: Xavier Loux (BleuRaven)
#
# SPDX-License-Identifier: GPL-3.0-or-later

# ----------------------------------------------
#  Blender For UnrealEngine
#  https://github.com/xavier150/Blender-For-UnrealEngine-Addons
# ----------------------------------------------


import bpy
from .. import bfu_ui
from .. import bbpl
from .. import bfu_alembic_animation
from .. import bfu_export_control
from .. import bfu_anim_nla


def draw_ui_object(layout: bpy.types.UILayout, context: bpy.types.Context, obj: bpy.types.Object):

    scene = bpy.context.scene 
    if scene is None:
        return

    # Hide filters
    if bfu_export_control.bfu_export_control_utils.is_not_export_recursive(obj):
        return
    if bfu_alembic_animation.bfu_alembic_animation_utils.is_alembic_animation(obj):
        return
    
    if bfu_ui.bfu_ui_utils.DisplayPropertyFilter("OBJECT", "ANIM"):
        accordion = bbpl.blender_layout.layout_accordion.get_accordion(scene, "bfu_animation_nla_advanced_properties_expanded")
        if accordion:
            _, panel = accordion.draw(layout)
            if panel:
                transformProp2 = panel.column()
                transformProp2.enabled = bfu_anim_nla.bfu_anim_nla_props.get_object_anim_nla_use(obj)
                transformProp2.prop(obj, "bfu_move_nla_to_center_for_export")
                transformProp2.prop(obj, "bfu_rotate_nla_to_zero_for_export")