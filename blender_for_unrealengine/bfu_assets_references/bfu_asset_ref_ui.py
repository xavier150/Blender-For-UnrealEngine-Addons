# SPDX-FileCopyrightText: Xavier Loux (BleuRaven)
#
# SPDX-License-Identifier: GPL-3.0-or-later

# ----------------------------------------------
#  Blender For UnrealEngine
#  https://github.com/xavier150/Blender-For-UnrealEngine-Addons
# ----------------------------------------------


import bpy
from .. import bbpl
from .. import bfu_utils
from .. import bfu_ui
from .. import bfu_skeletal_mesh
from .. import bfu_export_control
from .. import bfu_addon_prefs
from .. import bfu_lod
from .. import bfu_assets_references
from ..bfu_assets_references.bfu_asset_ref_props import BFU_EngineRefSkeletalMeshSearchModeEnum, BFU_EngineRefSkeletonSearchModeEnum


def draw_ui_object(layout: bpy.types.UILayout, context: bpy.types.Context, obj: bpy.types.Object):
    
    scene = bpy.context.scene 
    if scene is None:
        return
    addon_prefs = bfu_addon_prefs.get_addon_preferences()

    # Hide filters
    if not bfu_utils.draw_proxy_propertys(obj):
        return
    if addon_prefs.use_generated_scripts is False:
        return
    if bfu_export_control.bfu_export_control_utils.is_not_export_self(obj):
        return
    is_skeletal_mesh = bfu_skeletal_mesh.bfu_skeletal_mesh_utils.is_skeletal_mesh(obj)
    if is_skeletal_mesh is False:
        return
    
    # Draw UI
    if bfu_ui.bfu_ui_utils.DisplayPropertyFilter("OBJECT", "GENERAL"):   
        accordion = bbpl.blender_layout.layout_accordion.get_accordion(scene, "bfu_engine_ref_properties_expanded")
        if accordion:
            _, panel = accordion.draw(layout)
            if panel:
                # SkeletalMesh prop
                if is_skeletal_mesh:
                    if not bfu_lod.bfu_lod_props.get_object_export_as_lod_mesh(obj):
                        unreal_engine_refs = panel.column()
                        draw_skeleton_prop(unreal_engine_refs, obj)
                        draw_skeletal_mesh_prop(unreal_engine_refs, obj)


def draw_skeleton_prop(layout: bpy.types.UILayout, obj: bpy.types.Object):
    layout.prop(obj, "bfu_engine_ref_skeleton_search_mode")
    if bfu_assets_references.bfu_asset_ref_props.get_object_engine_ref_skeleton_search_mode(obj).value == BFU_EngineRefSkeletonSearchModeEnum.AUTO.value:
        pass
    if bfu_assets_references.bfu_asset_ref_props.get_object_engine_ref_skeleton_search_mode(obj).value == BFU_EngineRefSkeletonSearchModeEnum.CUSTOM_NAME.value:
        layout.prop(obj, "bfu_engine_ref_skeleton_custom_name")
    if bfu_assets_references.bfu_asset_ref_props.get_object_engine_ref_skeleton_search_mode(obj).value == BFU_EngineRefSkeletonSearchModeEnum.CUSTOM_PATH_NAME.value:
        layout.prop(obj, "bfu_engine_ref_skeleton_custom_path")
        layout.prop(obj, "bfu_engine_ref_skeleton_custom_name")
    if bfu_assets_references.bfu_asset_ref_props.get_object_engine_ref_skeleton_search_mode(obj).value == BFU_EngineRefSkeletonSearchModeEnum.CUSTOM_REFERENCE.value:
        layout.prop(obj, "bfu_engine_ref_skeleton_custom_ref")

def draw_skeletal_mesh_prop(layout: bpy.types.UILayout, obj: bpy.types.Object):
    layout.prop(obj, "bfu_engine_ref_skeletal_mesh_search_mode")
    if bfu_assets_references.bfu_asset_ref_props.get_object_engine_ref_skeletal_mesh_search_mode(obj).value == BFU_EngineRefSkeletalMeshSearchModeEnum.AUTO.value:
        pass
    if bfu_assets_references.bfu_asset_ref_props.get_object_engine_ref_skeletal_mesh_search_mode(obj).value == BFU_EngineRefSkeletalMeshSearchModeEnum.CUSTOM_NAME.value:
        layout.prop(obj, "bfu_engine_ref_skeletal_mesh_custom_name")
    if bfu_assets_references.bfu_asset_ref_props.get_object_engine_ref_skeletal_mesh_search_mode(obj).value == BFU_EngineRefSkeletalMeshSearchModeEnum.CUSTOM_PATH_NAME.value:
        layout.prop(obj, "bfu_engine_ref_skeletal_mesh_custom_path")
        layout.prop(obj, "bfu_engine_ref_skeletal_mesh_custom_name")
    if bfu_assets_references.bfu_asset_ref_props.get_object_engine_ref_skeletal_mesh_search_mode(obj).value == BFU_EngineRefSkeletalMeshSearchModeEnum.CUSTOM_REFERENCE.value:
        layout.prop(obj, "bfu_engine_ref_skeletal_mesh_custom_ref")