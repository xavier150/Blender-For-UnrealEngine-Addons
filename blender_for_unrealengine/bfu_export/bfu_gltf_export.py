# SPDX-FileCopyrightText: Xavier Loux (BleuRaven)
#
# SPDX-License-Identifier: GPL-3.0-or-later

# ----------------------------------------------
#  Blender For UnrealEngine
#  https://github.com/xavier150/Blender-For-UnrealEngine-Addons
# ----------------------------------------------


# This handle all FBX Export version of Blender.
# Better to look about an class that amange all export type in future?

import traceback
from typing import Dict, Any

import bpy

from .. import bpl


debug_show_arguments: bool = False

def export_scene_gltf(
        filepath: str = '', 
        check_existing: bool = True, 
        filter_glob: str = "*.glb",
        use_selection: bool = False, 
        use_visible: bool = False, 
        use_armature_deform_only: bool = False,
        use_active_collection: bool = False, 
        use_mesh_edges: bool = False, 
        bake_anim: bool = True,
    ):
    # Base parameters for all versions
    params: Dict[str, Any] = {
        'filepath': filepath,
        'check_existing': check_existing,
        'filter_glob': filter_glob,
        'use_selection': use_selection,
        'use_visible': use_visible,
        'use_active_collection': use_active_collection,
        'use_mesh_edges': use_mesh_edges,
        'export_def_bones': use_armature_deform_only,
        'export_bake_animation': bake_anim,
    }

    try:
        # Call the FBX export operator with the appropriate parameters
        if debug_show_arguments:
            print("(Blender) EXPORT PARMS:", params)
        return bpy.ops.export_scene.gltf(**params)
    except Exception as e:  # type: ignore
        # Capture and print the detailed error information
        error_message = traceback.format_exc()
        print(bpl.color_set.red(error_message))
