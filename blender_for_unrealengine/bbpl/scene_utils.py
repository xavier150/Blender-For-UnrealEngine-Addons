# SPDX-FileCopyrightText: Xavier Loux (BleuRaven)
#
# SPDX-License-Identifier: GPL-3.0-or-later

# ----------------------------------------------
#  BBPL -> BleuRaven Blender Python Library
#  https://github.com/xavier150/BBPL
# ----------------------------------------------

from typing import Dict, Any
import bpy


def get_use_local_view():
    """
    Check if the user use local view in an area
    """
    context = bpy.context
    screen = context.screen
    if screen is None:
        return

    areas = screen.areas
    for area in areas:
        if area.type == 'VIEW_3D':  # type: ignore
            # Check if using local view
            if area.spaces.active.local_view:  # type: ignore
                return True
    return False

def move_to_global_view():
    """
    Move from local view to global view in all 3D view areas. 
    Thanks Cmomoney!

    Blender 4.0 -> Set localview with context temp_override
    Blender 3.6 and older -> Set localview with custom context override
    """
    context = bpy.context
    screen = context.screen
    if screen is None:
        return

    
    areas = screen.areas
    for area in areas:
        if area.type == 'VIEW_3D':  # type: ignore
            # Check if using local view
            if area.spaces.active.local_view:  # type: ignore
                for region in area.regions:
                    if region.type == 'WINDOW':  # type: ignore
                        # Override context and switch to global view
                        
                        if bpy.app.version >= (4, 0, 0):
                            with context.temp_override(area=area, region=region):  # type: ignore
                                # switch to global view
                                bpy.ops.view3d.localview()  # type: ignore
                        else:
                            override_context: Dict[str, Any] = context.copy()  # type: ignore
                            override_context['area'] = area
                            override_context['region'] = region
                            # switch to global view
                            bpy.ops.view3d.localview(override_context)  # type: ignore


def move_to_local_view():
    """
    Move from global view to local view in the specified local view areas.
    """
    # TODO: Implement the code to move to local view
    pass


def is_tweak_mode():
    """
    Checks if the Blender scene is in tweak mode.

    Returns:
        bool: True if the scene is in tweak mode, False otherwise.
    """
    scene = bpy.context.scene
    if scene is None:
        return
    
    return scene.is_nla_tweakmode


def enter_tweak_mode():
    """
    Enters tweak mode in the Blender NLA editor.

    Returns:
        None
    """
    # TODO bpy.ops.nla.tweakmode_enter()
    pass


def exit_tweak_mode():
    """
    Exits tweak mode in the Blender NLA editor.

    Returns:
        None
    """
    # TODO bpy.ops.nla.tweakmode_exit()
    pass
