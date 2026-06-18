# SPDX-FileCopyrightText: Xavier Loux (BleuRaven)
#
# SPDX-License-Identifier: GPL-3.0-or-later

# ----------------------------------------------
#  Blender For UnrealEngine
#  https://github.com/xavier150/Blender-For-UnrealEngine-Addons
# ----------------------------------------------


import bpy
from .. import bbpl
from .. import bfu_addon_prefs
from .. import bfu_debug_settings


def draw_ui_scene(layout: bpy.types.UILayout, context: bpy.types.Context):
    scene = context.scene
    addon_prefs = bfu_addon_prefs.get_addon_preferences()
    events = bfu_debug_settings.root_events
    events.new_event("Draw Nomenclature Panel")

    accordion = bbpl.blender_layout.layout_accordion.get_accordion(scene, "bfu_nomenclature_properties_expanded")
    if accordion:
        _, panel = accordion.draw(layout)
        if panel:

            # Prefix
            events.add_sub_event("Draw Nomenclature Presets")
            propsPrefix = panel.row()
            propsPrefix = propsPrefix.column()
            propsPrefix.prop(scene, 'bfu_static_mesh_prefix_export_name', icon='OBJECT_DATA')
            propsPrefix.prop(scene, 'bfu_skeletal_mesh_prefix_export_name', icon='OBJECT_DATA')
            propsPrefix.prop(scene, 'bfu_skeleton_prefix_export_name', icon='OBJECT_DATA')
            propsPrefix.prop(scene, 'bfu_alembic_animation_prefix_export_name', icon='OBJECT_DATA')
            propsPrefix.prop(scene, 'bfu_groom_simulation_prefix_export_name', icon='OBJECT_DATA')
            propsPrefix.prop(scene, 'bfu_anim_prefix_export_name', icon='OBJECT_DATA')
            propsPrefix.prop(scene, 'bfu_pose_prefix_export_name', icon='OBJECT_DATA')
            propsPrefix.prop(scene, 'bfu_camera_prefix_export_name', icon='OBJECT_DATA')
            propsPrefix.prop(scene, 'bfu_spline_prefix_export_name', icon='OBJECT_DATA')

            # Sub folder
            events.stop_last_and_start_new_event("Draw Anim Subfolder")
            propsSub = panel.row()
            propsSub = propsSub.column()
            propsSub.prop(scene, 'bfu_anim_subfolder_name', icon='FILE_FOLDER')

            if addon_prefs.useGeneratedScripts:
                bfu_unreal_import_module = propsSub.column()
                bfu_unreal_import_module.prop(scene, 'bfu_unreal_import_module', icon='FILE_FOLDER')
                bfu_unreal_import_location = propsSub.column()
                bfu_unreal_import_location.prop(scene, 'bfu_unreal_import_location', icon='FILE_FOLDER')

            # File path
            events.stop_last_and_start_new_event("Draw Export File Path")
            filePath = panel.row()
            filePath = filePath.column()
            filePath.prop(scene, 'bfu_export_static_mesh_file_path')
            filePath.prop(scene, 'bfu_export_skeletal_mesh_file_path')
            filePath.prop(scene, 'bfu_export_skeletal_animation_file_path')
            filePath.prop(scene, 'bfu_export_alembic_file_path')
            filePath.prop(scene, 'bfu_export_groom_file_path')
            filePath.prop(scene, 'bfu_export_camera_file_path')
            filePath.prop(scene, 'bfu_export_spline_file_path')
            filePath.prop(scene, 'bfu_export_other_file_path')

            # File name
            events.stop_last_and_start_new_event("Draw Export File Name")
            fileName = panel.row()
            fileName = fileName.column()
            fileName.prop(scene, 'bfu_file_export_log_name', icon='FILE')
            if addon_prefs.useGeneratedScripts:
                fileName.prop(
                    scene,
                    'bfu_file_import_asset_script_name',
                    icon='FILE')
                fileName.prop(
                    scene,
                    'bfu_file_import_sequencer_script_name',
                    icon='FILE')
            events.stop_last_event()

    events.stop_last_event()