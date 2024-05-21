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
from . import bfu_camera_config
from .. import bfu_assets_manager

def get_enum_cameras_list():
    camera_types = [
        ("REGULAR", "Regular", "Regular camera, for standard gameplay views."),
        ("CINEMATIC", "Cinematic", "The Cine Camera Actor is a specialized Camera Actor with additional settings that replicate real-world film camera behavior. You can use the Filmback, Lens, and Focus settings to create realistic scenes, while adhering to industry standards."),
        ("ARCHVIS", "ArchVis", "Support for ArchVis Tools Cameras."),
        ("CUSTOM", "Custom", "If you use an custom camera actor."),
    ]
    return camera_types



def get_enum_cameras_default():
    return "CINEMATIC"

def is_camera(obj):
    asset_class = bfu_assets_manager.bfu_asset_manager_utils.get_asset_class(obj)
    if asset_class:
        if asset_class.get_asset_type_name(obj) == bfu_camera_config.asset_type_name:
            return True
    return False