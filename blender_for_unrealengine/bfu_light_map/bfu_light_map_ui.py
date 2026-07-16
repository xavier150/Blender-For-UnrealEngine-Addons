# SPDX-FileCopyrightText: Xavier Loux (BleuRaven)
#
# SPDX-License-Identifier: GPL-3.0-or-later

# ----------------------------------------------
#  Blender For UnrealEngine
#  https://github.com/xavier150/Blender-For-UnrealEngine-Addons
# ----------------------------------------------


import bpy
from .. import bfu_addon_prefs
from .. import bfu_utils
from .. import bfu_ui
from .. import bbpl
from .. import bfu_static_mesh
from .. import bfu_export_control
from .. import bfu_light_map
from ..bfu_light_map.bfu_light_map_props import BFU_StaticMeshLightMapMode
from . import bfu_light_map_utils


def draw_obj_ui(layout: bpy.types.UILayout, context: bpy.types.Context, obj: bpy.types.Object):

    scene = bpy.context.scene 
    if scene is None:
        return
    
    addon_prefs = bfu_addon_prefs.get_addon_preferences()

    # Hide filters
    is_static_mesh = bfu_static_mesh.bfu_static_mesh_utils.is_static_mesh(obj)
    if addon_prefs.useGeneratedScripts is False:
        return
    if not bfu_utils.draw_proxy_propertys(obj):
        return
    if bfu_export_control.bfu_export_control_utils.is_not_export_self(obj):
        return
    
    if bfu_ui.bfu_ui_utils.DisplayPropertyFilter("OBJECT", "MISC"):
        accordion = bbpl.blender_layout.layout_accordion.get_accordion(scene, "bfu_object_light_map_properties_expanded")
        if accordion:
            _, panel = accordion.draw(layout)
            if panel:
                if is_static_mesh:
                    StaticMeshLightMapRes = panel.box()
                    StaticMeshLightMapRes.prop(obj, 'bfu_static_mesh_light_map_mode')
                    if bfu_light_map.bfu_light_map_props.get_object_static_mesh_light_map_mode(obj).value == BFU_StaticMeshLightMapMode.CUSTOM_MAP.value:
                        CustomLightMap = StaticMeshLightMapRes.column()
                        CustomLightMap.prop(obj, 'bfu_static_mesh_custom_light_map_res')
                    if bfu_light_map.bfu_light_map_props.get_object_static_mesh_light_map_mode(obj).value == BFU_StaticMeshLightMapMode.SURFACE_AREA.value:
                        SurfaceAreaLightMap = StaticMeshLightMapRes.column()
                        SurfaceAreaLightMapButton = SurfaceAreaLightMap.row()
                        SurfaceAreaLightMapButton.operator("object.comput_lightmap", icon='TEXTURE')
                        SurfaceAreaLightMapButton.operator("object.comput_all_lightmap", icon='TEXTURE')
                        SurfaceAreaLightMap.prop(obj, 'bfu_use_static_mesh_light_map_world_scale')
                        SurfaceAreaLightMap.prop(obj, 'bfu_static_mesh_light_map_surface_scale')
                        SurfaceAreaLightMap.prop(obj, 'bfu_static_mesh_light_map_round_power_of_two')
                    if bfu_light_map.bfu_light_map_props.get_object_static_mesh_light_map_mode(obj).value != BFU_StaticMeshLightMapMode.DEFAULT.value:
                        CompuntedLightMap = str(bfu_light_map_utils.get_compunted_light_map(obj))
                        StaticMeshLightMapRes.label(text='Compunted light map: ' + CompuntedLightMap)
                    bfu_generate_light_map_uvs = panel.row()
                    bfu_generate_light_map_uvs.prop(obj, 'bfu_generate_light_map_uvs')

def draw_tools_ui(layout: bpy.types.UILayout, context: bpy.types.Context):
    scene = context.scene
    accordion = bbpl.blender_layout.layout_accordion.get_accordion(scene, "bfu_tools_light_map_properties_expanded")
    if accordion:
        _, panel = accordion.draw(layout)
        if panel:
            checkButton = panel.column()
            checkButton.operator("object.comput_all_lightmap", icon='TEXTURE')