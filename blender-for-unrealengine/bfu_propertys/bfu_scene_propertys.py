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
from .. import bbpl

classes = (
)



def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.Scene.bfu_object_properties_expanded = bbpl.blender_layout.layout_accordion.add_ui_accordion(name="Object Properties")
    bpy.types.Scene.bfu_object_lod_properties_expanded = bbpl.blender_layout.layout_accordion.add_ui_accordion(name="Lod")
    bpy.types.Scene.bfu_object_collision_properties_expanded = bbpl.blender_layout.layout_accordion.add_ui_accordion(name="Collision")
    bpy.types.Scene.bfu_object_light_map_properties_expanded = bbpl.blender_layout.layout_accordion.add_ui_accordion(name="Light map")
    bpy.types.Scene.bfu_object_uv_map_properties_expanded = bbpl.blender_layout.layout_accordion.add_ui_accordion(name="UV map")

    bpy.types.Scene.bfu_animation_action_properties_expanded = bbpl.blender_layout.layout_accordion.add_ui_accordion(name="Actions Properties")
    bpy.types.Scene.bfu_animation_action_advanced_properties_expanded = bbpl.blender_layout.layout_accordion.add_ui_accordion(name="Actions Advanced Properties")
    bpy.types.Scene.bfu_animation_nla_properties_expanded = bbpl.blender_layout.layout_accordion.add_ui_accordion(name="NLA Properties")
    bpy.types.Scene.bfu_animation_nla_advanced_properties_expanded = bbpl.blender_layout.layout_accordion.add_ui_accordion(name="NLA Advanced Properties")
    bpy.types.Scene.bfu_animation_advanced_properties_expanded = bbpl.blender_layout.layout_accordion.add_ui_accordion(name="Animation Advanced Properties")

    bpy.types.Scene.bfu_engine_ref_properties_expanded = bbpl.blender_layout.layout_accordion.add_ui_accordion(name="Engine Refs")

    bpy.types.Scene.bfu_collection_properties_expanded = bbpl.blender_layout.layout_accordion.add_ui_accordion(name="Collection Properties")
    bpy.types.Scene.bfu_object_advanced_properties_expanded = bbpl.blender_layout.layout_accordion.add_ui_accordion(name="Object advanced Properties")
    bpy.types.Scene.bfu_collision_expanded = bbpl.blender_layout.layout_accordion.add_ui_accordion(name="Collision")
    bpy.types.Scene.bfu_socket_expanded = bbpl.blender_layout.layout_accordion.add_ui_accordion(name="Socket")
    bpy.types.Scene.bfu_uvmap_expanded = bbpl.blender_layout.layout_accordion.add_ui_accordion(name="UV Map")
    bpy.types.Scene.bfu_lightmap_expanded = bbpl.blender_layout.layout_accordion.add_ui_accordion(name="Light Map")
    bpy.types.Scene.bfu_nomenclature_properties_expanded = bbpl.blender_layout.layout_accordion.add_ui_accordion(name="Nomenclature")
    bpy.types.Scene.bfu_export_filter_properties_expanded = bbpl.blender_layout.layout_accordion.add_ui_accordion(name="Export filters")
    bpy.types.Scene.bfu_export_process_properties_expanded = bbpl.blender_layout.layout_accordion.add_ui_accordion(name="Export process")
    bpy.types.Scene.bfu_script_tool_expanded = bbpl.blender_layout.layout_accordion.add_ui_accordion(name="Copy Import Script")

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
    del bpy.types.Scene.bfu_object_lod_properties_expanded
    del bpy.types.Scene.bfu_object_collision_properties_expanded
    del bpy.types.Scene.bfu_object_light_map_properties_expanded
    del bpy.types.Scene.bfu_object_uv_map_properties_expanded

    del bpy.types.Scene.bfu_animation_action_properties_expanded
    del bpy.types.Scene.bfu_animation_action_advanced_properties_expanded
    del bpy.types.Scene.bfu_animation_nla_properties_expanded
    del bpy.types.Scene.bfu_animation_nla_advanced_properties_expanded
    del bpy.types.Scene.bfu_animation_advanced_properties_expanded

    del bpy.types.Scene.bfu_engine_ref_properties_expanded

    del bpy.types.Scene.bfu_collection_properties_expanded
    del bpy.types.Scene.bfu_object_advanced_properties_expanded
    del bpy.types.Scene.bfu_collision_expanded
    del bpy.types.Scene.bfu_uvmap_expanded
    del bpy.types.Scene.bfu_socket_expanded
    del bpy.types.Scene.bfu_lightmap_expanded
    del bpy.types.Scene.bfu_nomenclature_properties_expanded
    del bpy.types.Scene.bfu_export_filter_properties_expanded
    del bpy.types.Scene.bfu_export_process_properties_expanded
    del bpy.types.Scene.bfu_script_tool_expanded

    del bpy.types.Scene.bfu_active_object_tab

