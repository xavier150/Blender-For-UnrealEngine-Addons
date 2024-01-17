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

# ----------------------------------------------
#  BBPL -> BleuRaven Blender Python Library
#  BleuRaven.fr
#  XavierLoux.com
# ----------------------------------------------

import bpy

def get_use_local_view():
    """
    Check if the user use local view in an area
    """
    areas = bpy.context.screen.areas
    for area in areas:
        if area.type == 'VIEW_3D':
            if area.spaces.active.local_view:  # Check if using local view
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
    areas = context.screen.areas
    for area in areas:
        if area.type == 'VIEW_3D':
            if area.spaces.active.local_view:  # Check if using local view
                for region in area.regions:
                    if region.type == 'WINDOW':
                        # Override context and switch to global view
                        
                        if bpy.app.version >= (4, 0, 0):
                            with context.temp_override(area=area, region=region):
                                bpy.ops.view3d.localview() #switch to global view
                        else:
                            override_context = context.copy()
                            override_context['area'] = area
                            override_context['region'] = region
                            bpy.ops.view3d.localview(override_context) #switch to global view


def move_to_local_view(local_view_areas):
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
    return bpy.context.scene.is_nla_tweakmode


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
