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


import os
import bpy
import addon_utils
from .. import __internal__


def get_addon_version(addon_name):
    version = (0, 0, 0)
    for mod in addon_utils.modules():
        if mod.bl_info['name'] == addon_name:
            return mod.bl_info.get('version', (0, 0, 0))
    return version

def get_addon_version_str(addon_name):
    version = get_addon_version(addon_name)
    return '.'.join([str(x) for x in version])

def get_addon_file(addon_name):
    for mod in addon_utils.modules():
        if mod.bl_info['name'] == addon_name:
            return mod.__file__
    return "Not Found"

def get_addon_path(addon_name):
    for mod in addon_utils.modules():
        if mod.bl_info['name'] == addon_name:
            return os.path.dirname(mod.__file__)
    return "Not Found"