# SPDX-FileCopyrightText: Xavier Loux (BleuRaven)
#
# SPDX-License-Identifier: GPL-3.0-or-later

# ----------------------------------------------
#  Blender For UnrealEngine
#  https://github.com/xavier150/Blender-For-UnrealEngine-Addons
# ----------------------------------------------


import bpy
from .. import bbpl
from .. import bfu_ui
from .. import bfu_skeletal_mesh
from .. import bfu_modular_skeletal_mesh
from .. import bfu_export_control
from .. import bfu_base_object
from .. import bfu_alembic_animation


def draw_general_ui_object(layout: bpy.types.UILayout, obj: bpy.types.Object):
    if not isinstance(obj.data, bpy.types.Armature):
        return
    
    scene = bpy.context.scene 
    if scene is None:
        return
    
    if bfu_ui.bfu_ui_utils.DisplayPropertyFilter("OBJECT", "GENERAL"):
        if bfu_base_object.bfu_base_obj_props.get_scene_object_properties_expanded(scene):
            if bfu_export_control.bfu_export_control_utils.is_export_self(obj):
                if not bfu_alembic_animation.bfu_alembic_animation_props.get_object_export_as_alembic_animation(obj):
                    AssetType2 = layout.column()
                    # Show asset type
                    AssetType2.prop(obj, "bfu_export_skeletal_mesh_as_static_mesh")

def draw_ui_object(layout: bpy.types.UILayout, context: bpy.types.Context, obj: bpy.types.Object):
    
    scene = bpy.context.scene 
    if scene is None:
        return

    if not isinstance(obj.data, bpy.types.Armature):
        return
    is_skeletal_mesh = bfu_skeletal_mesh.bfu_skeletal_mesh_utils.is_skeletal_mesh(obj)
    if is_skeletal_mesh is False:
        return
    if bfu_export_control.bfu_export_control_utils.is_not_export_self(obj):
        return

    if bfu_ui.bfu_ui_utils.DisplayPropertyFilter("OBJECT", "GENERAL"):
        accordion = bbpl.blender_layout.layout_accordion.get_accordion(scene, "bfu_modular_skeletal_mesh_properties_expanded")
        if accordion:
            _, panel = accordion.draw(layout)
            if panel:
                # SkeletalMesh prop
                if not obj.bfu_export_as_lod_mesh:
                    modular_skeletal_mesh = panel.column()
                    modular_skeletal_mesh.prop(obj, "bfu_modular_skeletal_mesh_mode")
                    if obj.bfu_modular_skeletal_mesh_mode == "every_meshs":
                        modular_skeletal_mesh.prop(obj, "bfu_modular_skeletal_mesh_every_meshs_separate")
                    if obj.bfu_modular_skeletal_mesh_mode == "specified_parts":
                        bfu_modular_skeletal_mesh.bfu_modular_skeletal_mesh_utils.get_modular_skeletal_specified_parts_meshs_template(obj).draw(modular_skeletal_mesh)

def draw_ui_scene(layout: bpy.types.UILayout):
    pass