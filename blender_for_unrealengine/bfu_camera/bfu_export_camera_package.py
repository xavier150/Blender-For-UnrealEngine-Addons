# SPDX-FileCopyrightText: Xavier Loux (BleuRaven)
#
# SPDX-License-Identifier: GPL-3.0-or-later

# ----------------------------------------------
#  Blender For UnrealEngine
#  https://github.com/xavier150/Blender-For-UnrealEngine-Addons
# ----------------------------------------------

from pathlib import Path
from typing import TYPE_CHECKING, Tuple, Optional

import bpy

from .. import bbpl
from ..bbpl.utils import SaveUserRenderSimplify
from .. import bfu_utils
from ..bfu_assets_manager.bfu_asset_manager_type import AssetPackage
from .. import bfu_export
from ..bfu_export_logs.bfu_process_time_logs_types import SafeTimeGroup
from .. import bfu_anim_base
from . import bfu_export_procedure
from .bfu_export_procedure import BFU_CameraExportProcedure



def process_camera_export_from_package(
    op: bpy.types.Operator,
    package: AssetPackage,
) -> bool:

    if package.file:
        return export_camera_animation(
            op=op,
            fullpath=package.file.get_full_path(),
            obj=package.objects[0],
            frame_range=package.frame_range

        )
    else:
        return False

def export_camera_animation(
    op: bpy.types.Operator,
    fullpath: Path,
    obj: bpy.types.Object,
    frame_range: Optional[Tuple[float, float]]
) -> bool:

    '''
    #####################################################
            #CAMERA
    #####################################################
    '''

    # Export single camera
    my_timer_group = SafeTimeGroup()
    my_timer_group.start_timer(f"Prepare export")
    scene = bpy.context.scene
    if scene is None:
        raise ValueError("No active scene found!")

    # [SAVE ASSET DATA]
    # Save asset data before export like transforms, animation data, etc.
    # So can be restored after export.
    saved_simplify: SaveUserRenderSimplify = SaveUserRenderSimplify()
    saved_selection_names = bfu_export.bfu_export_utils.SavedObjectNames()
    saved_selection_names.save_new_name(obj)
    saved_frame_range: Tuple[int, int] = (scene.frame_start, scene.frame_end)
    saved_camera_delta_scale = obj.delta_scale.copy()


    # [SELECT ONLY] 
    # Select objects for export
    bbpl.utils.safe_mode_set('OBJECT')
    bbpl.utils.select_specific_object(obj)

    # Selected active that should be used for export.
    if bpy.context.active_object is None:
        raise ValueError("No active object found after duplicate!")
    active: bpy.types.Object = bpy.context.active_object
    bfu_export.bfu_export_utils.set_object_export_name(obj=active, is_skeletal=False)

    if TYPE_CHECKING:
        class FakeObject(bpy.types.Object):
            bfu_camera_export_procedure: str
            bfu_convert_geometry_node_attribute_to_uv: bool
            bfu_convert_geometry_node_attribute_to_uv_name: str
            bfu_fbx_export_with_custom_props: bool
            bfu_export_deform_only: bool
            bfu_export_with_meta_data: bool
            bfu_mirror_symmetry_right_side_bones: bool
            bfu_use_ue_mannequin_bone_alignment: bool
            bfu_disable_free_scale_animation: bool
            bfu_fbx_export_with_custom_props: bool
            bfu_simplify_anim_for_export: float
        active = FakeObject()  # type: ignore

    # Select and rescale camera for export
    active.delta_scale *= 0.01

    # [PREPARE SCENE FOR EXPORT]
    # Prepare scene for export (frame range, simplefying, etc.)
    if frame_range:
        scene.frame_start = int(frame_range[0])
        scene.frame_end = int(frame_range[1]) + 1
    saved_simplify.unsimplify_scene()

    my_timer_group.end_last_timer()

    # Process export
    my_timer_group.start_timer(f"Process export")
    camera_export_procedure: BFU_CameraExportProcedure = bfu_export_procedure.get_object_export_procedure(active)
    export_result = None
    if (camera_export_procedure.value == BFU_CameraExportProcedure.STANDARD_FBX.value):
        export_result = bfu_export.bfu_fbx_export.export_scene_fbx(
            filepath=str(fullpath),
            check_existing=False,
            use_selection=True,
            apply_unit_scale=True,
            global_scale=bfu_utils.GetObjExportScale(active),
            apply_scale_options='FBX_SCALE_NONE',
            object_types={'CAMERA'},
            use_custom_props=active.bfu_fbx_export_with_custom_props,
            add_leaf_bones=False,
            use_armature_deform_only=active.bfu_export_deform_only,
            bake_anim=True,
            bake_anim_use_nla_strips=False,
            bake_anim_use_all_actions=False,
            bake_anim_force_startend_keying=True,
            bake_anim_step=bfu_anim_base.bfu_anim_base_props.get_object_sample_anim_for_export(active),
            bake_anim_simplify_factor=active.bfu_simplify_anim_for_export,
            path_mode='AUTO',
            embed_textures=False,
            batch_mode='OFF',
            use_batch_own_dir=True,
            use_metadata=active.bfu_export_with_meta_data,
            primary_bone_axis=bfu_export.bfu_export_utils.get_final_fbx_export_primary_bone_axis(active),
            secondary_bone_axis=bfu_export.bfu_export_utils.get_final_fbx_export_secondary_bone_axis(active),
            use_space_transform=bfu_export.bfu_export_utils.get_static_fbx_export_use_space_transform(active),
            axis_forward=bfu_export.bfu_export_utils.get_static_fbx_export_axis_forward(active),
            axis_up=bfu_export.bfu_export_utils.get_static_fbx_export_axis_up(active),
            bake_space_transform=False
            )
    elif (camera_export_procedure.value == BFU_CameraExportProcedure.STANDARD_GLTF.value):
        # @TODO: Implement GLTF export for camera
        # bpy.ops.export_scene.gltf()
        pass
    else:
        print(f"Error: The export procedure '{camera_export_procedure}' was not found!")
    my_timer_group.end_last_timer()

    # [RESTORE ASSET DATA]
    # Restore asset data after export like transforms, animation data, etc.
    my_timer_group.start_timer(f"Clean after export")
    saved_selection_names.restore_names()
    saved_simplify.reset_scene()
    scene.frame_start = saved_frame_range[0]
    scene.frame_end = saved_frame_range[1]

    # Reset camera scale
    active.delta_scale = saved_camera_delta_scale

    for obj in scene.objects:
        bfu_utils.clear_all_bfu_temp_vars(obj)
    my_timer_group.end_last_timer()

    # [RETURN EXPORT RESULT]
    if export_result:
        if export_result == {'FINISHED'}:
            return True
    return False