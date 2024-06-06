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


# This handle all FBX Export version of Blender.
# Better to look about an class that amange all export type in future?

import bpy
from . import bfu_export_utils
from .. import fbxio
from mathutils import Vector, Matrix, Quaternion



def export_scene_fbx_with_custom_fbx_io(operator, context, filepath='', check_existing=True, filter_glob='*.fbx', use_selection=False, use_visible=False, use_active_collection=False, global_scale=1.0, apply_unit_scale=True, apply_scale_options='FBX_SCALE_NONE', use_space_transform=True, bake_space_transform=False, object_types={'ARMATURE', 'CAMERA', 'EMPTY', 'LIGHT', 'MESH', 'OTHER'}, use_mesh_modifiers=True, use_mesh_modifiers_render=True, mesh_smooth_type='OFF', colors_type='SRGB', prioritize_active_color=False, use_subsurf=False, use_mesh_edges=False, use_tspace=False, use_triangles=False, use_custom_props=False, add_leaf_bones=True, primary_bone_axis='Y', secondary_bone_axis='X', use_armature_deform_only=False, armature_nodetype='NULL', bake_anim=True, bake_anim_use_all_bones=True, bake_anim_use_nla_strips=True, bake_anim_use_all_actions=True, bake_anim_force_startend_keying=True, bake_anim_step=1.0, bake_anim_simplify_factor=1.0, path_mode='AUTO', embed_textures=False, batch_mode='OFF', use_batch_own_dir=True, use_metadata=True, axis_forward='-Z', axis_up='Y', global_matrix=Matrix(), animation_only=False, mirror_symmetry_right_side_bones=False, use_ue_mannequin_bone_alignment=False, disable_free_scale_animation=False):
    # Warning, do not work in 4.0 and older version for the moment!
    # Need do a custom version OF fbx IO per version to fit with Blender API.

    # Check Blender version
    blender_version = bpy.app.version

    # Base parameters for all versions
    params = {
        'filepath': filepath,
        'check_existing': check_existing,
        'filter_glob': filter_glob,
        'use_selection': use_selection,
        'use_visible': use_visible,
        'use_active_collection': use_active_collection,
        'global_scale': global_scale,
        'apply_unit_scale': apply_unit_scale,
        'apply_scale_options': apply_scale_options,
        'use_space_transform': use_space_transform,
        'bake_space_transform': bake_space_transform,
        'object_types': object_types,
        'use_mesh_modifiers': use_mesh_modifiers,
        'use_mesh_modifiers_render': use_mesh_modifiers_render,
        'mesh_smooth_type': mesh_smooth_type,
        'use_subsurf': use_subsurf,
        'use_mesh_edges': use_mesh_edges,
        'use_tspace': use_tspace,
        'use_triangles': use_triangles,
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

    # Add 'colors_type' parameter if Blender version is 3.4 or above
    if blender_version >= (3, 4, 0):
        params['colors_type'] = colors_type

    # Add 'prioritize_active_color' parameter if Blender version is 3.4 or above
    if blender_version >= (3, 5, 0):
        params['prioritize_active_color'] = prioritize_active_color


    # Call the FBX export operator with the appropriate parameters
    fbxio.current_fbxio.export_fbx_bin.save(**params)


def export_scene_fbx(filepath='', check_existing=True, filter_glob='*.fbx', use_selection=False, use_visible=False, use_active_collection=False, global_scale=1.0, apply_unit_scale=True, apply_scale_options='FBX_SCALE_NONE', use_space_transform=True, bake_space_transform=False, object_types={'ARMATURE', 'CAMERA', 'EMPTY', 'LIGHT', 'MESH', 'OTHER'}, use_mesh_modifiers=True, use_mesh_modifiers_render=True, mesh_smooth_type='OFF', colors_type='SRGB', prioritize_active_color=False, use_subsurf=False, use_mesh_edges=False, use_tspace=False, use_triangles=False, use_custom_props=False, add_leaf_bones=True, primary_bone_axis='Y', secondary_bone_axis='X', use_armature_deform_only=False, armature_nodetype='NULL', bake_anim=True, bake_anim_use_all_bones=True, bake_anim_use_nla_strips=True, bake_anim_use_all_actions=True, bake_anim_force_startend_keying=True, bake_anim_step=1.0, bake_anim_simplify_factor=1.0, path_mode='AUTO', embed_textures=False, batch_mode='OFF', use_batch_own_dir=True, use_metadata=True, axis_forward='-Z', axis_up='Y'):
    
    # Check Blender version
    blender_version = bpy.app.version

    # Base parameters for all versions
    params = {
        'filepath': filepath,
        'check_existing': check_existing,
        'filter_glob': filter_glob,
        'use_selection': use_selection,
        'use_visible': use_visible,
        'use_active_collection': use_active_collection,
        'global_scale': global_scale,
        'apply_unit_scale': apply_unit_scale,
        'apply_scale_options': apply_scale_options,
        'use_space_transform': use_space_transform,
        'bake_space_transform': bake_space_transform,
        'object_types': object_types,
        'use_mesh_modifiers': use_mesh_modifiers,
        'use_mesh_modifiers_render': use_mesh_modifiers_render,
        'mesh_smooth_type': mesh_smooth_type,
        'use_subsurf': use_subsurf,
        'use_mesh_edges': use_mesh_edges,
        'use_tspace': use_tspace,
        'use_triangles': use_triangles,
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


    # Add 'colors_type' parameter if Blender version is 3.4 or above
    if blender_version >= (3, 4, 0):
        params['colors_type'] = colors_type

    # Add 'prioritize_active_color' parameter if Blender version is 3.4 or above
    if blender_version >= (3, 5, 0):
        params['prioritize_active_color'] = prioritize_active_color


    # Call the FBX export operator with the appropriate parameters
    bpy.ops.export_scene.fbx(**params)
