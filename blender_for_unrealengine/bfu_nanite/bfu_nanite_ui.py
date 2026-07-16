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
from .. import bfu_skeletal_mesh
from .. import bfu_export_control

def draw_obj_ui(layout: bpy.types.UILayout, context: bpy.types.Context, obj: bpy.types.Object):

    scene = bpy.context.scene 
    addon_prefs = bfu_addon_prefs.get_addon_preferences()

    # Hide filters
    if addon_prefs.useGeneratedScripts is False:
        return
    if not bfu_utils.draw_proxy_propertys(obj):
        return
    if bfu_export_control.bfu_export_control_utils.is_not_export_self(obj):
        return
    
    is_static_mesh = bfu_static_mesh.bfu_static_mesh_utils.is_static_mesh(obj)
    is_skeletal_mesh = bfu_skeletal_mesh.bfu_skeletal_mesh_utils.is_skeletal_mesh(obj)
    if is_static_mesh == False and is_skeletal_mesh == False:
        return # Check only static and skeletal meshs for the moment.

    if bfu_ui.bfu_ui_utils.DisplayPropertyFilter("OBJECT", "MISC"):
        accordion = bbpl.blender_layout.layout_accordion.get_accordion(scene, "bfu_object_nanite_properties_expanded")
        if accordion:
            _, panel = accordion.draw(layout)
            if panel:
                panel.prop(obj, 'bfu_build_nanite_mode')

