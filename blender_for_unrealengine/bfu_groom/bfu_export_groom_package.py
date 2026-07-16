# SPDX-FileCopyrightText: Xavier Loux (BleuRaven)
#
# SPDX-License-Identifier: GPL-3.0-or-later

# ----------------------------------------------
#  Blender For UnrealEngine
#  https://github.com/xavier150/Blender-For-UnrealEngine-Addons
# ----------------------------------------------

from pathlib import Path
from typing import List

import bpy

from .. import bbpl
from ..bbpl.utils import SaveUserRenderSimplify
from .. import bfu_utils
from .. import bfu_adv_object
from ..bfu_assets_manager.bfu_asset_manager_type import AssetPackage
from .. import bfu_export
from ..bfu_export_logs.bfu_process_time_logs_types import SafeTimeGroup
from . import bfu_export_procedure
from .bfu_export_procedure import BFU_GroomExportProcedure

def process_groom_simulation_export_from_package(
    op: bpy.types.Operator,
    package: AssetPackage,
) -> bool:

    if package.file:
        return export_single_groom_simulation(
            op=op,
            fullpath=package.file.get_full_path(),
            objs=package.objects
        )
    else:
        return False


def export_single_groom_simulation(
    op: bpy.types.Operator,
    fullpath: Path,
    objs: List[bpy.types.Object]
) -> bool:

    '''
    #####################################################
            #GROOM SIMULATION
    #####################################################
    '''

    # Export a single groom simulation
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
    saved_selection_names.save_new_names(objs)
    saved_base_transforms = bfu_export.bfu_export_utils.SaveTransformObjects(objs[0])


    # [SELECT ONLY] 
    # Select objects for export
    bbpl.utils.safe_mode_set('OBJECT')
    bbpl.utils.select_specific_object_list(objs[0], objs)

    # Selected active that should be used for export.
    if bpy.context.active_object is None:
        raise ValueError("No active object found after duplicate!")
    active: bpy.types.Object = bpy.context.active_object
    bfu_export.bfu_export_utils.set_object_export_name(obj=active, is_skeletal=False)

    frame = scene.frame_current = 1
    
    bfu_adv_object.bfu_adv_obj_utils.apply_object_export_transform(active)

    # [PREPARE SCENE FOR EXPORT]
    # Prepare scene for export (frame range, simplefying, etc.)
    saved_simplify.unsimplify_scene()

    my_timer_group.end_last_timer()

    # Process export
    my_timer_group.start_timer(f"Process export")
    groom_simulation_export_procedure: BFU_GroomExportProcedure = bfu_export_procedure.get_object_export_procedure(active)
    export_result = None
    if (groom_simulation_export_procedure.value == BFU_GroomExportProcedure.STANDARD_ALEMBIC.value):
        export_result = bpy.ops.wm.alembic_export(  # type: ignore
            filepath=str(fullpath),
            check_existing=False,
            selected=True,
            global_scale=1,
            start=frame,
            end=frame,
            uvs=False,
            normals=False,
            vcolors=True
            )
    else:
        print(f"Error: The export procedure '{groom_simulation_export_procedure.value}' was not found!")
    my_timer_group.end_last_timer()

    # [RESTORE ASSET DATA]
    # Restore asset data after export like transforms, animation data, etc.
    my_timer_group.start_timer(f"Clean after export")
    saved_base_transforms.reset_object_transforms()
    saved_selection_names.restore_names()
    saved_simplify.reset_scene()


    for obj in scene.objects:
        bfu_utils.clear_all_bfu_temp_vars(obj)
    my_timer_group.end_last_timer()

    # [RETURN EXPORT RESULT]
    if export_result:
        if export_result == {'FINISHED'}:
            return True
    return False