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
import importlib

from . import __internal__
from . import blender_layout
from . import backward_compatibility
from . import blender_rig
from . import blender_addon
from . import basics
from . import utils
from . import rig_bone_visual
from . import skin_utils
from . import anim_utils
from . import scene_utils
from . import ui_utils

if "__internal__" in locals():
    importlib.reload(__internal__)
if "blender_layout" in locals():
    importlib.reload(blender_layout)
if "backward_compatibility" in locals():
    importlib.reload(backward_compatibility)
if "blender_rig" in locals():
    importlib.reload(blender_rig)
if "blender_addon" in locals():
    importlib.reload(blender_addon)
if "basics" in locals():
    importlib.reload(basics)
if "utils" in locals():
    importlib.reload(utils)
if "rig_bone_visual" in locals():
    importlib.reload(rig_bone_visual)
if "skin_utils" in locals():
    importlib.reload(skin_utils)
if "anim_utils" in locals():
    importlib.reload(anim_utils)
if "scene_utils" in locals():
    importlib.reload(scene_utils)
if "ui_utils" in locals():
    importlib.reload(ui_utils)


classes = (
)



def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    blender_layout.register()
    backward_compatibility.register()
    blender_rig.register()
    blender_addon.register()


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)

    blender_addon.unregister()
    blender_rig.unregister()
    backward_compatibility.unregister()
    blender_layout.unregister()