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
from .. import bfu_skeletal_mesh
from .. import bfu_export_control
from .. import bfu_anim_nla
from ..bfu_anim_nla.bfu_anim_nla_props import BFU_AnimNLAStartEndTimeEnum

def draw_ui_object(layout: bpy.types.UILayout, context: bpy.types.Context, obj: bpy.types.Object):

    scene = bpy.context.scene 
    if scene is None:
        return


    # Hide filters
    if bfu_export_control.bfu_export_control_utils.is_not_export_recursive(obj):
        return
    is_skeletal_mesh = bfu_skeletal_mesh.bfu_skeletal_mesh_utils.is_skeletal_mesh(obj)
    
    if bfu_ui.bfu_ui_utils.DisplayPropertyFilter("OBJECT", "ANIM"):
        accordion = bbpl.blender_layout.layout_accordion.get_accordion(scene, "bfu_animation_nla_properties_expanded")
        if accordion:
            _, panel = accordion.draw(layout)
            if panel:
                # NLA
                if is_skeletal_mesh:
                    NLAAnim = panel.row()
                    NLAAnim.prop(obj, 'bfu_anim_nla_use')
                    NLAAnimChild = NLAAnim.column()
                    NLAAnimChild.enabled = bfu_anim_nla.bfu_anim_nla_props.get_object_anim_nla_use(obj)
                    NLAAnimChild.prop(obj, 'bfu_anim_nla_export_name')

                # NLA Time
                if obj.type != "CAMERA":
                    NLATimeProperty = panel.column()
                    NLATimeProperty.enabled = bfu_anim_nla.bfu_anim_nla_props.get_object_anim_nla_use(obj)
                    NLATimeProperty.prop(obj, 'bfu_anim_nla_start_end_time_enum')
                    if bfu_anim_nla.bfu_anim_nla_props.get_object_anim_nla_start_end_time_enum(obj) == BFU_AnimNLAStartEndTimeEnum.WITH_CUSTOMFRAMES:
                        OfsetTime = NLATimeProperty.row()
                        OfsetTime.prop(obj, 'bfu_anim_nla_custom_start_frame')
                        OfsetTime.prop(obj, 'bfu_anim_nla_custom_end_frame')
                    if bfu_anim_nla.bfu_anim_nla_props.get_object_anim_nla_start_end_time_enum(obj) != BFU_AnimNLAStartEndTimeEnum.WITH_CUSTOMFRAMES:
                        OfsetTime = NLATimeProperty.row()
                        OfsetTime.prop(obj, 'bfu_anim_nla_start_frame_offset')
                        OfsetTime.prop(obj, 'bfu_anim_nla_end_frame_offset')