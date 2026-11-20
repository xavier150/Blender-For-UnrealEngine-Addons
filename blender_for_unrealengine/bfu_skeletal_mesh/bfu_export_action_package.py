# SPDX-FileCopyrightText: Xavier Loux (BleuRaven)
#
# SPDX-License-Identifier: GPL-3.0-or-later

# ----------------------------------------------
#  Blender For UnrealEngine
#  https://github.com/xavier150/Blender-For-UnrealEngine-Addons
# ----------------------------------------------

from pathlib import Path
from typing import List, Tuple, Optional

import bpy

from .. import bbpl
from .. import bfu_addon_prefs
from .. import bfu_adv_object
from .. import bfu_anim_action_adv
from .. import bfu_anim_base
from .. import bfu_custom_property
from .. import bfu_export
from .. import bfu_material
from .. import bfu_skeletal_mesh
from .. import bfu_utils
from ..bbpl.utils import SaveUserRenderSimplify
from ..bfu_assets_manager.bfu_asset_manager_type import AssetPackage
from ..bfu_export_logs.bfu_process_time_logs_types import SafeTimeGroup
from ..bfu_skeletal_mesh.bfu_export_procedure import BFU_SkeletonExportProcedure


def process_action_animation_export_from_package(
    op: bpy.types.Operator,
    package: AssetPackage
) -> bool:

    if package.file and package.action:
        return export_as_action_animation(
            op=op,
            fullpath=package.file.get_full_path(),
            armature=package.objects[0],
            mesh_parts=package.objects[1:],
            target_action=package.action,
            frame_range=package.frame_range,
        )
    else:
        return False


def export_as_action_animation(
    op: bpy.types.Operator,
    fullpath: Path,
    armature: bpy.types.Object,
    mesh_parts: List[bpy.types.Object],
    target_action: bpy.types.Action,
    frame_range: Optional[Tuple[float, float]]
):

    '''
    #####################################################
            #SKELETAL ACTION
    #####################################################
    '''

    if not isinstance(armature.data, bpy.types.Armature):
        raise TypeError(f"The armature object is not a valid Armature type! Inputs: armature: {armature.name}")  

    # Export a single action like a animation or pose
    my_timer_group = SafeTimeGroup()
    my_timer_group.start_timer(f"Prepare export")
    scene = bpy.context.scene
    if scene is None:
        raise ValueError("No active scene found!")
    unit_settings = scene.unit_settings
    if unit_settings is None:
        raise ValueError("No scene unit settings found!")

    addon_prefs = bfu_addon_prefs.get_addon_preferences()
    is_library = bfu_utils.get_object_is_library(armature)

    # [SAVE ASSET DATA]
    # Save asset data before export like transforms, animation data, etc.
    # So can be restored after export.
    saved_simplify: SaveUserRenderSimplify = SaveUserRenderSimplify()
    saved_selection_names = bfu_export.bfu_export_utils.SavedObjectNames()
    saved_selection_names.save_new_name(armature)
    saved_selection_names.save_new_names(mesh_parts)
    saved_unit_scale = unit_settings.scale_length
    animation_data = bbpl.anim_utils.AnimationManagment()
    animation_data.save_animation_data(armature)
    saved_frame_range: Tuple[int, int] = (scene.frame_start, scene.frame_end)


    # [SELECT AND DUPLICATE] 
    # Select and duplicate objects for export (Export the duplicated objects)
    bbpl.utils.safe_mode_set('OBJECT')
    bbpl.utils.select_specific_object_list(armature, mesh_parts)
    # Deselect sockets because Unreal Engine detect them as bones
    bfu_skeletal_mesh.bfu_skeletal_mesh_utils.deselect_socket(armature) 

    duplicate_data = bfu_export.bfu_export_utils.DuplicateData()
    if not is_library:
        duplicate_data.duplicate_select_for_export_with_rename_and_reparent(bpy.context, False)

    # Duplicated active that should be used for export.
    if bpy.context.active_object is None:
        raise ValueError("No active object found after duplicate!")
    active: bpy.types.Object = bpy.context.active_object
    bfu_export.bfu_export_utils.set_duplicated_object_export_name(
        duplicated_obj=active, 
        original_obj=armature, 
        is_skeletal=True
    )

    # [MAKE REAL COPY] 
    # Make objects real to be able to edit before export.
    bfu_export.bfu_export_utils.convert_selected_to_mesh()
    bfu_export.bfu_export_utils.make_select_visual_real()

    # Apply only desirect action for export
    if active.animation_data is None:  # type: ignore
        active.animation_data_create().action = target_action  # Apply desired action
    else:
        active.animation_data.action = target_action  # Apply desired action
    
    if addon_prefs.bake_armature_animations:
        bfu_export.bfu_export_utils.bake_armature_animation(active, scene.frame_start, scene.frame_end)

    bfu_anim_action_adv.bfu_anim_action_adv_utils.apply_action_export_transform(active)  # Apply export transform before rescale

    # This will rescale the rig and unit scale to get a root bone egal to 1
    should_rescale_rig = bfu_export.bfu_export_utils.get_should_rescale_skeleton_for_fbx_export(active)
    rrf: Optional[float] = None
    animation_scale_factor: Optional[float] = None
    export_objects: List[bpy.types.Object] = []
    my_skeletal_export_scale: Optional[bfu_utils.SkeletalExportScale] = None
    if should_rescale_rig:
        rrf = bfu_export.bfu_export_utils.get_rescale_rig_factor()  # rigRescaleFactor
        print("debug_S1 -> rrf:", rrf)
        print(f"Rescale rig factor: {rrf}")
        print("debug_S2 -> unit_settings.scale_length:", unit_settings.scale_length)
        unit_settings.scale_length = 0.01
        print("debug_S3 -> unit_settings.scale_length after change:", unit_settings.scale_length)
        export_objects = list(bpy.context.selected_objects or [])
        if active not in export_objects:
            export_objects.append(active)
        skeletal_export_scale = bfu_utils.SkeletalExportScale(active)
        print("debug_S4 -> skeletal_export_scale created:", skeletal_export_scale)
        my_skeletal_export_scale = skeletal_export_scale
        print("debug_S4 -> my_skeletal_export_scale assigned:", my_skeletal_export_scale)
        skeletal_export_scale.apply_skeletal_export_scale(rrf)
        print("debug_S5 -> skeletal_export_scale applied with rrf:", rrf)
        rescale_animation_factor = rrf*active.scale.z
        print("debug_S6 -> rescale_animation_factor:", rescale_animation_factor)
        animation_scale_factor = rescale_animation_factor
        print("debug_S7 -> animation_scale_factor assigned:", animation_scale_factor)
        print("debug_S8 -> object_location_scale_factor:", round(saved_unit_scale, 8)/0.01)
        bbpl.scene.scale_utils.scale_animations(
            rescale_animation_factor,
            [],
            [],
            object_location_scale_factor=round(saved_unit_scale, 8)/0.01,
        )
        bbpl.scene.scale_utils.scale_rigs_data(
            rrf,
            export_objects,
            [],
            use_armature_constraint=False,
            curve_hook_matrix_scale_factor=100.0,
        )
        bbpl.anim_utils.reset_armature_pose(active)
        bbpl.scene.scale_utils.scale_rigs_data(
            rrf,
            [active],
            [],
            use_shape_key_drivers=False,
            use_modifiers=False,
            use_curve_hooks=False,
        )
        bbpl.anim_utils.copy_drivers(armature, active)

    # animation_data.action is ReadOnly with tweakmode in 2.8
    if (scene.is_nla_tweakmode):
        if active.animation_data:
            active.animation_data.use_tweak_mode = False

    if addon_prefs.ignore_nla_for_action:  # Reset NLA
        if active.animation_data:
            active.animation_data.action_extrapolation = 'HOLD'
            active.animation_data.action_blend_type = 'REPLACE'
            active.animation_data.action_influence = 1

    # [PREPARE SCENE FOR EXPORT]
    # Prepare scene for export (frame range, simplefying, etc.)
    if frame_range:
        scene.frame_start = int(frame_range[0])
        scene.frame_end = int(frame_range[1])
    saved_simplify.unsimplify_scene()

    my_timer_group.end_last_timer()

    # Process export
    my_timer_group.start_timer(f"Process export")
    skeleton_export_procedure: BFU_SkeletonExportProcedure = bfu_skeletal_mesh.bfu_export_procedure.get_object_export_procedure(active)
    export_result = None
    if (skeleton_export_procedure.value == BFU_SkeletonExportProcedure.CUSTOM_FBX_EXPORT.value):
        export_result = bfu_export.bfu_fbx_export.export_scene_fbx_with_custom_fbx_io(
            operator=op,
            context=bpy.context,
            filepath=str(fullpath),
            check_existing=False,
            use_selection=True,
            animation_only=bfu_anim_base.bfu_anim_base_props.get_object_export_animation_without_mesh(active),
            global_matrix=bfu_export.bfu_export_utils.get_skeleton_axis_conversion(active),
            apply_unit_scale=True,
            global_scale=bfu_adv_object.bfu_adv_obj_props.get_object_export_global_scale(active),
            apply_scale_options='FBX_SCALE_NONE',
            object_types={'ARMATURE', 'EMPTY', 'MESH'},
            use_custom_props=bfu_custom_property.bfu_custom_property_props.get_object_fbx_export_with_custom_props(active),
            mesh_smooth_type="FACE",
            add_leaf_bones=False,
            use_armature_deform_only=bfu_skeletal_mesh.bfu_skeletal_mesh_props.get_object_export_deform_only(active),
            bake_anim=True,
            bake_anim_use_nla_strips=False,
            bake_anim_use_all_actions=False,
            bake_anim_force_startend_keying=True,
            bake_anim_step=bfu_anim_base.bfu_anim_base_props.get_object_sample_anim_for_export(active),
            bake_anim_simplify_factor=bfu_anim_base.bfu_anim_base_props.get_object_simplify_anim_for_export(active),
            path_mode='AUTO',
            embed_textures=False,
            batch_mode='OFF',
            use_batch_own_dir=True,
            use_metadata=bfu_adv_object.bfu_adv_obj_props.get_object_export_with_meta_data(active),
            primary_bone_axis=bfu_export.bfu_export_utils.get_final_fbx_export_primary_bone_axis(active),
            secondary_bone_axis=bfu_export.bfu_export_utils.get_final_fbx_export_secondary_bone_axis(active),
            mirror_symmetry_right_side_bones=bfu_skeletal_mesh.bfu_skeletal_mesh_props.get_object_mirror_symmetry_right_side_bones(active),
            use_ue_mannequin_bone_alignment=bfu_skeletal_mesh.bfu_skeletal_mesh_props.get_object_use_ue_mannequin_bone_alignment(active),
            disable_free_scale_animation=bfu_anim_base.bfu_anim_base_props.get_object_disable_free_scale_animation(active),
            use_space_transform=bfu_export.bfu_export_utils.get_skeleton_fbx_export_use_space_transform(active),
            axis_forward=bfu_export.bfu_export_utils.get_skeleton_export_axis_forward(active),
            axis_up=bfu_export.bfu_export_utils.get_skeleton_export_axis_up(active),
            bake_space_transform=False
            )
    elif (skeleton_export_procedure == BFU_SkeletonExportProcedure.STANDARD_FBX.value):
        export_result = bfu_export.bfu_fbx_export.export_scene_fbx(
            filepath=str(fullpath),
            check_existing=False,
            use_selection=True,
            apply_unit_scale=True,
            global_scale=bfu_adv_object.bfu_adv_obj_props.get_object_export_global_scale(active),
            apply_scale_options='FBX_SCALE_NONE',
            object_types={'ARMATURE', 'EMPTY', 'MESH'},
            use_custom_props=bfu_custom_property.bfu_custom_property_props.get_object_fbx_export_with_custom_props(active),
            mesh_smooth_type="FACE",
            add_leaf_bones=False,
            use_armature_deform_only=bfu_skeletal_mesh.bfu_skeletal_mesh_props.get_object_export_deform_only(active),
            bake_anim=True,
            bake_anim_use_nla_strips=False,
            bake_anim_use_all_actions=False,
            bake_anim_force_startend_keying=True,
            bake_anim_step=bfu_anim_base.bfu_anim_base_props.get_object_sample_anim_for_export(active),
            bake_anim_simplify_factor=bfu_anim_base.bfu_anim_base_props.get_object_simplify_anim_for_export(active),
            path_mode='AUTO',
            embed_textures=False,
            batch_mode='OFF',
            use_batch_own_dir=True,
            use_metadata=bfu_adv_object.bfu_adv_obj_props.get_object_export_with_meta_data(active),
            primary_bone_axis=bfu_export.bfu_export_utils.get_final_fbx_export_primary_bone_axis(active),
            secondary_bone_axis=bfu_export.bfu_export_utils.get_final_fbx_export_secondary_bone_axis(active),
            use_space_transform=bfu_export.bfu_export_utils.get_skeleton_fbx_export_use_space_transform(active),
            axis_forward=bfu_export.bfu_export_utils.get_skeleton_export_axis_forward(active),
            axis_up=bfu_export.bfu_export_utils.get_skeleton_export_axis_up(active),
            bake_space_transform=False
            )
    elif (skeleton_export_procedure == BFU_SkeletonExportProcedure.STANDARD_GLTF.value):
        export_result = bpy.ops.export_scene.gltf(
            filepath=str(fullpath),
            check_existing=False,
            use_selection=True,
            export_def_bones=bfu_skeletal_mesh.bfu_skeletal_mesh_props.get_object_export_deform_only(active),
            export_materials=bfu_material.bfu_material_utils.get_gltf_export_materials(active, is_animation=True),
            export_image_format=bfu_material.bfu_material_utils.get_gltf_export_textures(active, is_animation=True),
            export_apply = True,
            export_animations=True,
            export_animation_mode='ACTIVE_ACTIONS',
            # Set the animation name that imported in Unreal Engine.
            # Consider that the file name is the asset_import_name
            export_nla_strips_merged_animation_name=fullpath.stem,
            export_anim_scene_split_object=False,
            export_frame_range=True,
            export_negative_frame="CROP",
            export_anim_slide_to_zero=True,

            # If export_try_sparse_sk is True the import fail in Unreal Engine 5.4 and older versions.
            # It a bug from the Interchange pipeline when the skeletal mesh contrains several shape keys. (morph targets)
            # That now fixed since Unreal Engine 5.5. but I keep it on False for compatibility.
            export_try_sparse_sk=False,
            )
    else:
        print(f"Error: The export procedure '{skeleton_export_procedure}' was not found!")
    my_timer_group.end_last_timer()

    # [RESTORE ASSET DATA]
    # Restore asset data after export like transforms, animation data, etc.
    my_timer_group.start_timer(f"Clean after export")
    unit_settings.scale_length = saved_unit_scale
    saved_selection_names.restore_names()
    saved_simplify.reset_scene()
    animation_data.set_animation_data(armature, copy_nla=True)
    scene.frame_start = saved_frame_range[0]
    scene.frame_end = saved_frame_range[1]

    bbpl.anim_utils.reset_armature_pose(armature)

    # This will rescale the rig and unit scale to get a root bone egal to 1
    if should_rescale_rig:
        if rrf is None or animation_scale_factor is None or my_skeletal_export_scale is None:
            raise RuntimeError("Export scale state is missing during cleanup.")
        bbpl.scene.scale_utils.scale_rigs_data(
            1/rrf,
            [active],
            [],
            use_shape_key_drivers=False,
            use_modifiers=False,
            use_curve_hooks=False,
        )
        my_skeletal_export_scale.ResetSkeletalExportScale()  # type: ignore
        bbpl.scene.scale_utils.scale_animations(
            1/animation_scale_factor,
            [],
            [],
            object_location_scale_factor=0.01/round(saved_unit_scale, 8),
        )
        bbpl.scene.scale_utils.scale_rigs_data(
            1/rrf,
            export_objects,
            [],
            use_armature_constraint=False,
            curve_hook_matrix_scale_factor=0.01,
        )

    if not is_library:
        if bpy.context.selected_objects:
            bfu_utils.clean_delete_objects(list(bpy.context.selected_objects))

        for data in duplicate_data.data_to_remove:
            data.remove_data()

        duplicate_data.reset_duplicate_name_after_export()

    for obj in scene.objects:
        bfu_utils.clear_all_bfu_temp_vars(obj)
    my_timer_group.end_last_timer()

    # [RETURN EXPORT RESULT]
    if export_result:
        if export_result == {'FINISHED'}:
            return True
    return False