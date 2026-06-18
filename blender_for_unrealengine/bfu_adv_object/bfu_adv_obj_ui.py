# SPDX-FileCopyrightText: Xavier Loux (BleuRaven)
#
# SPDX-License-Identifier: GPL-3.0-or-later

# ----------------------------------------------
#  Blender For UnrealEngine
#  https://github.com/xavier150/Blender-For-UnrealEngine-Addons
# ----------------------------------------------


import bpy
from ..bfu_simple_file_type_enum import BFU_FileTypeEnum
from .. import bpl
from .. import bfu_utils
from .. import bfu_ui
from .. import bbpl
from .. import bfu_alembic_animation
from .. import bfu_camera
from .. import bfu_static_mesh
from .. import bfu_skeletal_mesh
from .. import bfu_custom_property
from .. import bfu_export_control
from .. import bfu_adv_object

def draw_ui_object(layout: bpy.types.UILayout, context: bpy.types.Context, obj: bpy.types.Object):

    scene = bpy.context.scene 

    # Hide filters
    if not bfu_utils.draw_proxy_propertys(obj):
        return
    if bfu_export_control.bfu_export_control_utils.is_not_export_recursive(obj):
        return

    if bfu_ui.bfu_ui_utils.DisplayPropertyFilter("OBJECT", "GENERAL"):
        accordion = bbpl.blender_layout.layout_accordion.get_accordion(scene, "bfu_object_advanced_properties_expanded")
        if accordion:
            _, panel = accordion.draw(layout)
            if panel:
                transformProp = panel.column()
                is_not_alembic_animation = not bfu_alembic_animation.bfu_alembic_animation_utils.is_alembic_animation(obj)
                is_not_camera = not bfu_camera.bfu_camera_utils.is_camera(obj)
                if is_not_alembic_animation and is_not_camera:
                    transformProp.prop(obj, "bfu_move_to_center_for_export")
                    transformProp.prop(obj, "bfu_rotate_to_zero_for_export")
                    transformProp.prop(obj, "bfu_additional_location_for_export")
                    transformProp.prop(obj, "bfu_additional_rotation_for_export")

                transformProp_scale = transformProp.row()
                transformProp_scale.prop(obj, 'bfu_export_global_scale')
                if bfu_skeletal_mesh.bfu_skeletal_mesh_utils.is_not_skeletal_mesh(obj):
                    preset = bfu_static_mesh.bfu_export_procedure.get_obj_static_fbx_procedure_preset(obj)
                    if(bfu_static_mesh.bfu_export_procedure.get_obj_can_edit_scale(obj) == False):
                        transformProp_scale.enabled = False
                
                if bfu_camera.bfu_camera_utils.is_camera(obj):
                    transformProp.prop(obj, "bfu_additional_location_for_export")

                AxisProperty = panel.column()
                
                if bfu_skeletal_mesh.bfu_skeletal_mesh_utils.is_skeletal_mesh(obj):
                    export_type = bfu_skeletal_mesh.bfu_export_procedure.get_obj_export_file_type(obj)
                else:
                    export_type = bfu_static_mesh.bfu_export_procedure.get_obj_export_file_type(obj)

                if export_type.value == BFU_FileTypeEnum.FBX.value:
                    AxisProperty.prop(obj, 'bfu_override_procedure_preset')
                    if bfu_adv_object.bfu_adv_obj_props.get_object_override_procedure_preset(obj):
                        AxisProperty.prop(obj, 'bfu_fbx_export_use_space_transform')
                        AxisProperty.prop(obj, 'bfu_fbx_export_axis_forward')
                        AxisProperty.prop(obj, 'bfu_fbx_export_axis_up')
                        bbpl.blender_layout.layout_doc_button.add_doc_page_operator(AxisProperty, text="About axis Transforms", url="https://github.com/xavier150/Blender-For-UnrealEngine-Addons/wiki/Axis-Transforms")
                        if bfu_skeletal_mesh.bfu_skeletal_mesh_utils.is_skeletal_mesh(obj):
                            BoneAxisProperty = panel.column()
                            BoneAxisProperty.prop(obj, 'bfu_fbx_export_primary_bone_axis')
                            BoneAxisProperty.prop(obj, 'bfu_fbx_export_secondary_bone_axis')
                    else:
                        box = panel.box()
                        if bfu_skeletal_mesh.bfu_skeletal_mesh_utils.is_skeletal_mesh(obj):
                            preset = bfu_skeletal_mesh.bfu_export_procedure.get_obj_skeleton_fbx_procedure_preset(obj)
                        else:
                            preset = bfu_static_mesh.bfu_export_procedure.get_obj_static_fbx_procedure_preset(obj)
                        var_lines = box.column()
                        for key, value in preset.items():
                            display_key = bpl.utils.format_property_name(key)
                            var_lines.label(text=f"{display_key}: {value}\n")
                export_data = panel.column()
                bfu_custom_property.bfu_custom_property_ui.draw_ui_custom_property(export_data, obj)
                export_data.prop(obj, "bfu_export_with_meta_data")