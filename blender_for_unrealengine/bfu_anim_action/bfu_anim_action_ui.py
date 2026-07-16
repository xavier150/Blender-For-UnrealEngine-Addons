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
from .. import bfu_alembic_animation
from .. import bfu_camera
from .. import bfu_export_control
from .. import bfu_anim_action
from .. bfu_anim_action.bfu_anim_action_props import BFU_AnimActionExportEnum, BFU_AnimActionStartEndTimeEnum, BFU_AnimNamingTypeEnum


def draw_ui_object(layout: bpy.types.UILayout, context: bpy.types.Context, obj: bpy.types.Object):

    scene = bpy.context.scene 
    if scene is None:
        return

    # Hide filters
    if bfu_export_control.bfu_export_control_utils.is_not_export_self(obj):
        return
    
    is_skeletal_mesh = bfu_skeletal_mesh.bfu_skeletal_mesh_utils.is_skeletal_mesh(obj)
    is_camera = bfu_camera.bfu_camera_utils.is_camera(obj)
    is_alembic_animation = bfu_alembic_animation.bfu_alembic_animation_utils.is_alembic_animation(obj)
    if True not in [is_skeletal_mesh, is_camera, is_alembic_animation]:
        return

    if bfu_ui.bfu_ui_utils.DisplayPropertyFilter("OBJECT", "ANIM"):
        accordion = bbpl.blender_layout.layout_accordion.get_accordion(scene, "bfu_animation_action_properties_expanded")
        if accordion:
            _, panel = accordion.draw(layout)
            if panel:
                if is_skeletal_mesh:
                    # Action list
                    action_list_property = panel.column()
                    action_list_property.prop(obj, 'bfu_anim_action_export_enum')
                    
                    if bfu_anim_action.bfu_anim_action_props.get_object_anim_action_export_enum(obj) == BFU_AnimActionExportEnum.EXPORT_SPECIFIC_LIST:
                        action_list_panel_box = panel.box()                        
                        action_list_panel_box.template_list(
                            # type and unique id
                            "BFU_UL_ActionExportTarget", "",
                            # pointer to the CollectionProperty
                            obj, "bfu_action_asset_list",
                            # pointer to the active identifier
                            obj, "bfu_active_action_asset_list",
                            maxrows=5,
                            rows=5
                        )
                        update_obj_action_list = action_list_panel_box.row(align=True)
                        update_obj_action_list.operator("object.updateobjactionlist", icon='RECOVER_LAST')
                        update_obj_action_list.operator("object.clearobjactionlist", icon='X', text="")

                        wm = context.window_manager
                        action_list_panel_box.prop(wm, 'bfu_debug_show_action_list')

                        select_deselect_obj_action_list = action_list_panel_box.row()
                        select_deselect_obj_action_list.operator("object.selectallobjactionlist")
                        select_deselect_obj_action_list.operator("object.deselectallobjactionlist")
                    elif bfu_anim_action.bfu_anim_action_props.get_object_anim_action_export_enum(obj) == BFU_AnimActionExportEnum.EXPORT_SPECIFIC_PREFIX:
                        panel.prop(obj, 'bfu_prefix_name_to_export')

                # Action Time
                if obj.type != "CAMERA":
                    ActionTimeProperty = panel.column()
                    ActionTimeProperty.enabled = bfu_anim_action.bfu_anim_action_props.get_object_anim_action_export_enum(obj) != BFU_AnimActionExportEnum.DONT_EXPORT
                    ActionTimeProperty.prop(obj, 'bfu_anim_action_start_end_time_enum')
                    
                    if bfu_anim_action.bfu_anim_action_props.get_object_anim_action_start_end_time_enum(obj) == BFU_AnimActionStartEndTimeEnum.WITH_CUSTOMFRAMES:
                        OfsetTime = ActionTimeProperty.row()
                        OfsetTime.prop(obj, 'bfu_anim_action_custom_start_frame')
                        OfsetTime.prop(obj, 'bfu_anim_action_custom_end_frame')
                    if bfu_anim_action.bfu_anim_action_props.get_object_anim_action_start_end_time_enum(obj) != BFU_AnimActionStartEndTimeEnum.WITH_CUSTOMFRAMES:
                        OfsetTime = ActionTimeProperty.row()
                        OfsetTime.prop(obj, 'bfu_anim_action_start_frame_offset')
                        OfsetTime.prop(obj, 'bfu_anim_action_end_frame_offset')

                else:
                    panel.label(
                        text=(
                            "Note: animation start/end use scene frames" +
                            " with the camera for the sequencer.")
                        )

                # Nomenclature
                if is_skeletal_mesh:
                    export_anim_naming = panel.column()
                    export_anim_naming.enabled = bfu_anim_action.bfu_anim_action_props.get_object_anim_action_export_enum(obj) != BFU_AnimActionExportEnum.DONT_EXPORT
                    export_anim_naming.prop(obj, 'bfu_anim_naming_type')
                    if bfu_anim_action.bfu_anim_action_props.get_object_anim_naming_type_enum(obj) == BFU_AnimNamingTypeEnum.INCLUDE_CUSTOM_NAME:
                        export_anim_naming_text = export_anim_naming.column()
                        export_anim_naming_text.prop(obj, 'bfu_anim_naming_custom')