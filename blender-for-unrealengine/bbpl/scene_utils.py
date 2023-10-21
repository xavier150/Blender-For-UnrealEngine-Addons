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
#  xavierloux.com
# ----------------------------------------------

import bpy


def move_to_global_view():
    """
    Move from local view to global view in all 3D view areas.
    """
    local_view_areas = []

    for area in bpy.context.screen.areas:
        if area.type == 'VIEW_3D':
            space = area.spaces[0]
            if space.local_view:  # Check if using local view
                local_view_areas.append(area)

    for local_view_area in local_view_areas:
        for region in local_view_area.regions:
            if region.type == 'WINDOW':
                # Override context and switch to global view
                override = {'area': local_view_area, 'region': region}
                bpy.ops.view3d.localview(override)

    return local_view_areas


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
