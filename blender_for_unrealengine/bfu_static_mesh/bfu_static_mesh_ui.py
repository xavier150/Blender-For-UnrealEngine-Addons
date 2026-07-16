# SPDX-FileCopyrightText: Xavier Loux (BleuRaven)
#
# SPDX-License-Identifier: GPL-3.0-or-later

# ----------------------------------------------
#  Blender For UnrealEngine
#  https://github.com/xavier150/Blender-For-UnrealEngine-Addons
# ----------------------------------------------


import bpy
from .. import bfu_base_object
from .. import bfu_ui
from .. import bfu_export_control
from . import bfu_static_mesh_utils

def draw_ui_object(layout: bpy.types.UILayout, context: bpy.types.Context, obj: bpy.types.Object):
    
    scene = bpy.context.scene 
    if scene is None:
        raise ValueError("No active scene found!")

    if bfu_ui.bfu_ui_utils.DisplayPropertyFilter("OBJECT", "GENERAL"):
        if bfu_base_object.bfu_base_obj_props.get_scene_object_properties_expanded(scene):
            if bfu_static_mesh_utils.is_static_mesh(obj):
                if bfu_export_control.bfu_export_control_utils.is_export_self(obj):

                    StaticMeshUI = layout.column()
                    export_procedure_prop = StaticMeshUI.column()
                    export_procedure_prop.prop(obj, 'bfu_static_export_procedure')


def draw_ui_scene(layout: bpy.types.UILayout):
    pass