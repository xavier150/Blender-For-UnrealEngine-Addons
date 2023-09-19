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

'''
This addons allows to easily export several objects, animation, cameras, [...] at the same time for use in game engines
like Unreal Engine of Unity by removing the usual constraints while respecting engine naming conventions
and a clean tree structure.
It also contains a small toolkit for collisions and sockets.

Asset = Object to export in game engine.
Sub object are object in assets like collision or sockets.

Addon for Blender by Xavier Loux (BleuRaven)
xavierloux.com
xavierloux.loux@gmail.com
'''

import bpy
import importlib

from . import bps
from . import bbpl
from . import bfu_propertys
from . import bfu_addon_parts
from . import bfu_ui_utils
from . import bfu_addon_pref
from . import bfu_export_logs
from . import bfu_ui
from . import bfu_check_potential_error
from .export import bfu_export_asset
from . import bfu_write_text
from . import bfu_basics
from . import bfu_utils


if "bps" in locals():
    importlib.reload(bps)
if "bbpl" in locals():
    importlib.reload(bbpl)
if "bfu_propertys" in locals():
    importlib.reload(bfu_propertys)
if "bfu_addon_parts" in locals():
    importlib.reload(bfu_addon_parts)
if "bfu_ui_utils" in locals():
    importlib.reload(bfu_ui_utils)
if "bfu_addon_pref" in locals():
    importlib.reload(bfu_addon_pref)
if "bfu_export_logs" in locals():
    importlib.reload(bfu_export_logs)
if "bfu_ui" in locals():
    importlib.reload(bfu_ui)
if "bfu_check_potential_error" in locals():
    importlib.reload(bfu_check_potential_error)
if "bfu_export_asset" in locals():
    importlib.reload(bfu_export_asset)
if "bfu_write_text" in locals():
    importlib.reload(bfu_write_text)
if "bfu_basics" in locals():
    importlib.reload(bfu_basics)
if "bfu_utils" in locals():
    importlib.reload(bfu_utils)

bl_info = {
    'name': 'Blender for UnrealEngine',
    'author': 'Loux Xavier (BleuRaven)',
    'version': (0, 4, 2),
    'blender': (2, 80, 0),
    'location': 'View3D > UI > Unreal Engine',
    'description': "This add-ons allows to easily export several "
    "objects at the same time for use in unreal engine 4.",
    'warning': '',
    "wiki_url": "https://github.com/xavier150/Blender-For-UnrealEngine-Addons/wiki",
    'tracker_url': 'https://github.com/xavier150/Blender-For-UnrealEngine-Addons/issues',
    'support': 'COMMUNITY',
    'category': 'Import-Export'}


class BFUCachedAction(bpy.types.PropertyGroup):
    """
    Represents a cached action for Blender File Utils (BFU).
    """
    name: bpy.props.StringProperty()


classes = (
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    bfu_propertys.register()
    bfu_addon_parts.register()
    bfu_ui_utils.register()
    bfu_addon_pref.register()
    bfu_export_logs.register()
    bfu_ui.register()
    bfu_check_potential_error.register()


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)

    bfu_propertys.unregister()
    bfu_addon_parts.unregister()
    bfu_ui_utils.unregister()
    bfu_addon_pref.unregister()
    bfu_export_logs.unregister()
    bfu_ui.unregister()
    bfu_check_potential_error.unregister()
