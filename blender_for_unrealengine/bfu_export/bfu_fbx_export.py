# SPDX-FileCopyrightText: 2018-2025 Xavier Loux (BleuRaven)
#
# SPDX-License-Identifier: GPL-3.0-or-later

# ----------------------------------------------
#  Blender For UnrealEngine
#  https://github.com/xavier150/Blender-For-UnrealEngine-Addons
# ----------------------------------------------


# This handle all FBX Export version of Blender.
# Better to look about an class that amange all export type in future?

import traceback
from typing import Set, Dict, Any
from mathutils import Matrix

import bpy

from .. import bpl
from .. import fbxio


debug_show_arguments: bool = False

def export_scene_fbx_with_custom_fbx_io(
    operator: bpy.types.Operator, 
    context: bpy.types.Context, 
    filepath: str = '', 
    check_existing: bool = True, 
    filter_glob: str = "*.fbx",
    use_selection: bool = False, 
    use_visible: bool = False, 
    use_active_collection: bool = False, 
    global_scale: float = 1.0, 
    apply_unit_scale: bool = True, 
    apply_scale_options: str = 'FBX_SCALE_NONE', 
    use_space_transform: bool = True, 
    bake_space_transform: bool = False, 
    object_types: Set[str] = {'ARMATURE', 'CAMERA', 'EMPTY', 'LIGHT', 'MESH', 'OTHER'}, 
    use_mesh_modifiers: bool = True, 
    use_mesh_modifiers_render: bool = True, 
    mesh_smooth_type: str = 'OFF', 
    colors_type: str = 'SRGB', 
    prioritize_active_color: bool = False, 
    use_subsurf: bool = False, 
    use_mesh_edges: bool = False, 
    use_tspace: bool = False, 
    use_triangles: bool = False, 
    use_custom_props: bool = False, 
    add_leaf_bones: bool = True, 
    primary_bone_axis: str = 'Y', 
    secondary_bone_axis: str = 'X', 
    use_armature_deform_only: bool = False, 
    armature_nodetype: str = 'NULL', 
    bake_anim: bool = True, 
    bake_anim_use_all_bones: bool = True, 
    bake_anim_use_nla_strips: bool = True, 
    bake_anim_use_all_actions: bool = True, 
    bake_anim_force_startend_keying: bool = True, 
    bake_anim_step: float = 1.0, 
    bake_anim_simplify_factor: float = 1.0, 
    path_mode: str = 'AUTO', 
    embed_textures: bool = False, 
    batch_mode: str = 'OFF', 
    use_batch_own_dir: bool = True, 
    use_metadata: bool = True, 
    axis_forward: str = '-Z', 
    axis_up: str = 'Y', 
    global_matrix: Matrix = Matrix(), 
    animation_only: bool = False, 
    mirror_symmetry_right_side_bones: bool = False, 
    use_ue_mannequin_bone_alignment: bool = False, 
    disable_free_scale_animation: bool = False,
):
    # Warning, do not work in 4.0 and older version for the moment!
    # Need do a custom version OF fbx IO per version to fit with Blender API.

    # Check Blender version
    blender_version = bpy.app.version

    # Base parameters for all versions
    params: Dict[str, Any] = {
        'filepath': filepath,
        'check_existing': check_existing,
        'filter_glob': filter_glob,
        'use_selection': use_selection,
        'use_active_collection': use_active_collection,
        'global_scale': global_scale,
        'apply_unit_scale': apply_unit_scale,
        'apply_scale_options': apply_scale_options,
        'bake_space_transform': bake_space_transform,
        'object_types': object_types,
        'use_mesh_modifiers': use_mesh_modifiers,
        'use_mesh_modifiers_render': use_mesh_modifiers_render,
        'mesh_smooth_type': mesh_smooth_type,
        'use_subsurf': use_subsurf,
        'use_mesh_edges': use_mesh_edges,
        'use_tspace': use_tspace,
        'use_custom_props': use_custom_props,
        'add_leaf_bones': add_leaf_bones,
        'primary_bone_axis': primary_bone_axis,
        'secondary_bone_axis': secondary_bone_axis,
        'use_armature_deform_only': use_armature_deform_only,
        'armature_nodetype': armature_nodetype,
        'bake_anim': bake_anim,
        'bake_anim_use_all_bones': bake_anim_use_all_bones,
        'bake_anim_use_nla_strips': bake_anim_use_nla_strips,
        'bake_anim_use_all_actions': bake_anim_use_all_actions,
        'bake_anim_force_startend_keying': bake_anim_force_startend_keying,
        'bake_anim_step': bake_anim_step,
        'bake_anim_simplify_factor': bake_anim_simplify_factor,
        'path_mode': path_mode,
        'embed_textures': embed_textures,
        'batch_mode': batch_mode,
        'use_batch_own_dir': use_batch_own_dir,
        'use_metadata': use_metadata,
        'axis_forward': axis_forward,
        'axis_up': axis_up,
    }

    # Specific with custom fbx io:
    params['operator'] = operator
    params['context'] = context
    params['global_matrix'] = global_matrix
    params['animation_only'] = animation_only
    params['mirror_symmetry_right_side_bones'] = mirror_symmetry_right_side_bones
    params['use_ue_mannequin_bone_alignment'] = use_ue_mannequin_bone_alignment
    params['disable_free_scale_animation'] = disable_free_scale_animation

    if blender_version >= (2, 90, 0):
        params['use_visible'] = use_visible
        params['use_space_transform'] = use_space_transform

    if blender_version >= (3, 2, 0):
        params['use_triangles'] = use_triangles

    if blender_version >= (3, 4, 0):
        params['colors_type'] = colors_type

    if blender_version >= (3, 5, 0):
        params['prioritize_active_color'] = prioritize_active_color

    try:
        # Call the FBX export operator with the appropriate parameters
        if debug_show_arguments:
            print("(Custom) EXPORT PARMS:", params)
        return fbxio.current_fbxio.export_fbx_bin.save(**params)  # type: ignore
    except Exception as e:  # type: ignore
        # Capture and print the detailed error information
        error_message = traceback.format_exc()
        print(bpl.color_set.red(error_message))


def export_scene_fbx(
    filepath: str = '', 
    check_existing: bool = True, 
    filter_glob: str = '*.fbx', 
    use_selection: bool = False, 
    use_visible: bool = False, 
    use_active_collection: bool = False, 
    global_scale: float = 1.0, 
    apply_unit_scale: bool = True, 
    apply_scale_options: str = 'FBX_SCALE_NONE', 
    use_space_transform: bool = True, 
    bake_space_transform: bool = False, 
    object_types: Set[str] = {'ARMATURE', 'CAMERA', 'EMPTY', 'LIGHT', 'MESH', 'OTHER'}, 
    use_mesh_modifiers: bool = True, 
    use_mesh_modifiers_render: bool = True, 
    mesh_smooth_type: str = 'OFF', 
    colors_type: str = 'SRGB', 
    prioritize_active_color: bool = False, 
    use_subsurf: bool = False, 
    use_mesh_edges: bool = False, 
    use_tspace: bool = False, 
    use_triangles: bool = False, 
    use_custom_props: bool = False, 
    add_leaf_bones: bool = True, 
    primary_bone_axis: str = 'Y',
    secondary_bone_axis: str = 'X', 
    use_armature_deform_only: bool = False, 
    armature_nodetype: str = 'NULL', 
    bake_anim: bool = True, 
    bake_anim_use_all_bones: bool = True, 
    bake_anim_use_nla_strips: bool = True, 
    bake_anim_use_all_actions: bool = True, 
    bake_anim_force_startend_keying: bool = True, 
    bake_anim_step: float = 1.0, 
    bake_anim_simplify_factor: float = 1.0, 
    path_mode: str = 'AUTO', 
    embed_textures: bool = False, 
    batch_mode: str = 'OFF', 
    use_batch_own_dir: bool = True, 
    use_metadata: bool = True, 
    axis_forward: str = '-Z', 
    axis_up: str = 'Y'):

    # Check Blender version
    blender_version = bpy.app.version

    # Base parameters for all versions
    params: Dict[str, Any] = {
        'filepath': filepath,
        'check_existing': check_existing,
        'filter_glob': filter_glob,
        'use_selection': use_selection,
        'use_active_collection': use_active_collection,
        'global_scale': global_scale,
        'apply_unit_scale': apply_unit_scale,
        'apply_scale_options': apply_scale_options,
        'bake_space_transform': bake_space_transform,
        'object_types': object_types,
        'use_mesh_modifiers': use_mesh_modifiers,
        'use_mesh_modifiers_render': use_mesh_modifiers_render,
        'mesh_smooth_type': mesh_smooth_type,
        'use_subsurf': use_subsurf,
        'use_mesh_edges': use_mesh_edges,
        'use_tspace': use_tspace,
        'use_custom_props': use_custom_props,
        'add_leaf_bones': add_leaf_bones,
        'primary_bone_axis': primary_bone_axis,
        'secondary_bone_axis': secondary_bone_axis,
        'use_armature_deform_only': use_armature_deform_only,
        'armature_nodetype': armature_nodetype,
        'bake_anim': bake_anim,
        'bake_anim_use_all_bones': bake_anim_use_all_bones,
        'bake_anim_use_nla_strips': bake_anim_use_nla_strips,
        'bake_anim_use_all_actions': bake_anim_use_all_actions,
        'bake_anim_force_startend_keying': bake_anim_force_startend_keying,
        'bake_anim_step': bake_anim_step,
        'bake_anim_simplify_factor': bake_anim_simplify_factor,
        'path_mode': path_mode,
        'embed_textures': embed_textures,
        'batch_mode': batch_mode,
        'use_batch_own_dir': use_batch_own_dir,
        'use_metadata': use_metadata,
        'axis_forward': axis_forward,
        'axis_up': axis_up,
    }
    
    if blender_version >= (2, 90, 0):
        params['use_visible'] = use_visible
        params['use_space_transform'] = use_space_transform

    if blender_version >= (3, 2, 0):
        params['use_triangles'] = use_triangles

    if blender_version >= (3, 4, 0):
        params['colors_type'] = colors_type

    if blender_version >= (3, 5, 0):
        params['prioritize_active_color'] = prioritize_active_color


    try:
        # Call the FBX export operator with the appropriate parameters
        if (debug_show_arguments):
            print("(Blender) EXPORT PARMS:", params)
        return bpy.ops.export_scene.fbx(**params)
    except Exception as e:  # type: ignore
        # Capture and print the detailed error information
        error_message = traceback.format_exc()
        print(bpl.color_set.red(error_message))
