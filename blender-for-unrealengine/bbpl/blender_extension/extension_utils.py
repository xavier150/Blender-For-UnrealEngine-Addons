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


def get_package_version(pkg_id):

    version = None

    # @TODO this look like a bad way to do this. Need found how use bpy.ops.extensions.
    file_path = os.path.join(bpy.utils.user_resource('EXTENSIONS'), 'user_default', pkg_id, "blender_manifest.toml")
    with open(file_path, 'r') as file:
        for line in file:
            if line.startswith("version"):
                # Extraire la partie droite de la ligne après le signe '=' et enlever les espaces et guillemets
                version = line.split('=')[1].strip().strip('"')
                break

    return version

def get_package_path(pkg_id):
    # @TODO this look like a bad way to do this. Need found how use bpy.ops.extensions.
    return os.path.join(bpy.utils.user_resource('EXTENSIONS'), 'user_default', pkg_id)