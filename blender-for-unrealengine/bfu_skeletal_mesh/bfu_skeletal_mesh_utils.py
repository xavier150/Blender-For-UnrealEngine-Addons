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

import bpy
import fnmatch
from . import bfu_skeletal_mesh_config
from .. import bbpl
from .. import bfu_basics
from .. import bfu_utils
from .. import bfu_unreal_utils
from .. import bfu_assets_manager

def get_socket_in_desired_childs(obj):
    socket_objs = []
    for obj in bfu_utils.GetExportDesiredChilds(obj):
        if fnmatch.fnmatchcase(obj.name, "SOCKET*"):
            socket_objs.append(obj)
    return socket_objs

def deselect_socket(obj):
    # With skeletal mesh the Socket musts be not exported,
    # Because Unreal Engine will import it as bones.
    socket_objs = get_socket_in_desired_childs(obj)
    for obj in socket_objs:
        obj.select_set(False)


def is_skeletal_mesh(obj):
    asset_class = bfu_assets_manager.bfu_asset_manager_utils.get_asset_class(obj)
    if asset_class:
        if asset_class.get_asset_type_name(obj) == bfu_skeletal_mesh_config.mesh_asset_type_name:
            return True
    return False

def is_not_skeletal_mesh(obj):
    return not is_skeletal_mesh(obj)