# ====================== BEGIN GPL LICENSE BLOCK ============================
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.	 See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.	 If not, see <http://www.gnu.org/licenses/>.
#  All rights reserved.
#
# ======================= END GPL LICENSE BLOCK =============================


import bpy


classes = (
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.Scene.bfu_object_properties_expanded = bpy.props.BoolProperty()
    bpy.types.Scene.bfu_object_import_properties_expanded = bpy.props.BoolProperty()
    bpy.types.Scene.bfu_object_lod_properties_expanded = bpy.props.BoolProperty()
    bpy.types.Scene.bfu_object_collision_properties_expanded = bpy.props.BoolProperty()
    bpy.types.Scene.bfu_object_material_properties_expanded = bpy.props.BoolProperty()
    bpy.types.Scene.bfu_object_vertex_color_properties_expanded = bpy.props.BoolProperty()
    bpy.types.Scene.bfu_object_light_map_properties_expanded = bpy.props.BoolProperty()
    bpy.types.Scene.bfu_object_uv_map_properties_expanded = bpy.props.BoolProperty()
    bpy.types.Scene.bfu_animation_action_properties_expanded = bpy.props.BoolProperty()
    bpy.types.Scene.bfu_animation_action_advanced_properties_expanded = bpy.props.BoolProperty()
    bpy.types.Scene.bfu_animation_nla_properties_expanded = bpy.props.BoolProperty()
    bpy.types.Scene.bfu_animation_nla_advanced_properties_expanded = bpy.props.BoolProperty()
    bpy.types.Scene.bfu_animation_advanced_properties_expanded = bpy.props.BoolProperty()
    bpy.types.Scene.bfu_skeleton_properties_expanded = bpy.props.BoolProperty()
    bpy.types.Scene.bfu_collection_properties_expanded = bpy.props.BoolProperty()
    bpy.types.Scene.bfu_object_advanced_properties_expanded = bpy.props.BoolProperty()
    bpy.types.Scene.bfu_export_type_expanded = bpy.props.BoolProperty()
    bpy.types.Scene.bfu_camera_expanded = bpy.props.BoolProperty()
    bpy.types.Scene.bfu_collision_socket_expanded = bpy.props.BoolProperty()
    bpy.types.Scene.bfu_lightmap_expanded = bpy.props.BoolProperty()
    bpy.types.Scene.bfu_nomenclature_properties_expanded = bpy.props.BoolProperty()
    bpy.types.Scene.bfu_export_filter_properties_expanded = bpy.props.BoolProperty()
    bpy.types.Scene.bfu_export_process_properties_expanded = bpy.props.BoolProperty()
    bpy.types.Scene.bfu_script_tool_expanded = bpy.props.BoolProperty()

    bpy.types.Scene.bfu_active_tab = bpy.props.EnumProperty(
        items=(
            ('OBJECT', 'Object', 'Object tab.'),
            ('SCENE', 'Scene', 'Scene and world tab.')
            )
        )

    bpy.types.Scene.bfu_active_object_tab = bpy.props.EnumProperty(
        items=(
            ('GENERAL', 'General', 'General object tab.'),
            ('ANIM', 'Animations', 'Animations tab.'),
            ('MISC', 'Misc', 'Misc tab.'),
            ('ALL', 'All', 'All tabs.')
            )
        )

    bpy.types.Scene.bfu_active_scene_tab = bpy.props.EnumProperty(
        items=(
            ('GENERAL', 'Scene', 'General scene tab'),
            ('ALL', 'All', 'All tabs.')
            )
        )


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)

    del bpy.types.Scene.bfu_object_properties_expanded
    del bpy.types.Scene.bfu_object_import_properties_expanded
    del bpy.types.Scene.bfu_animation_action_properties_expanded
    del bpy.types.Scene.bfu_animation_action_advanced_properties_expanded
    del bpy.types.Scene.bfu_animation_nla_properties_expanded
    del bpy.types.Scene.bfu_animation_nla_advanced_properties_expanded
    del bpy.types.Scene.bfu_animation_advanced_properties_expanded
    del bpy.types.Scene.bfu_collection_properties_expanded
    del bpy.types.Scene.bfu_object_advanced_properties_expanded
    del bpy.types.Scene.bfu_collision_socket_expanded
    del bpy.types.Scene.bfu_lightmap_expanded
    del bpy.types.Scene.bfu_nomenclature_properties_expanded
    del bpy.types.Scene.bfu_export_filter_properties_expanded
    del bpy.types.Scene.bfu_export_process_properties_expanded
    del bpy.types.Scene.bfu_script_tool_expanded

    del bpy.types.Scene.bfu_active_object_tab

