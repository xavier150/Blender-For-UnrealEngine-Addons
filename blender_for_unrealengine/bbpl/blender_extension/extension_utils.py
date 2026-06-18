# SPDX-FileCopyrightText: Xavier Loux (BleuRaven)
#
# SPDX-License-Identifier: GPL-3.0-or-later

# ----------------------------------------------
#  BBPL -> BleuRaven Blender Python Library
#  https://github.com/xavier150/BBPL
# ----------------------------------------------

import os
import bpy
from typing import Optional
from ... import __package__ as base_package  # type: ignore

def get_package_version(pkg_idname: Optional[str] = None, repo_module: str = 'user_default') -> Optional[str]:
    if bpy.app.version < (4, 2, 0):
        print("Blender extensions are not supported under 4.2. Please use bbpl.blender_addon.addon_utils instead.")
        return None
    
    manifest_filename = "blender_manifest.toml"
    
    if pkg_idname:
        file_path = os.path.join(bpy.utils.user_resource('EXTENSIONS'), repo_module, pkg_idname, manifest_filename)
    else:
        from addon_utils import _extension_module_name_decompose  # type: ignore
        repo_module, pkg_idname = _extension_module_name_decompose(base_package)  # type: ignore
        file_path = os.path.join(bpy.utils.user_resource('EXTENSIONS'), repo_module, pkg_idname, manifest_filename)  # type: ignore
    
    version = None
    if os.path.isfile(file_path):  # type: ignore
        with open(file_path, 'r') as file:  # type: ignore
            for line in file:
                if line.startswith("version"):
                    version = line.split('=')[1].strip().strip('"')
                    break
    else:
        print(f"File {file_path} does not exist.")
    
    return version

def get_package_path(pkg_idname: Optional[str] = None, repo_module: str = 'user_default') -> Optional[str]:
    if bpy.app.version < (4, 2, 0):
        print("Blender extensions are not supported under 4.2. Please use bbpl.blender_addon.addon_utils instead.")
        return None

    if pkg_idname:
        return os.path.join(bpy.utils.user_resource('EXTENSIONS'), repo_module, pkg_idname)
    else:
        from addon_utils import _extension_module_name_decompose  # type: ignore
        repo_module, pkg_idname = _extension_module_name_decompose(base_package)  # type: ignore
        return os.path.join(bpy.utils.user_resource('EXTENSIONS'), repo_module, pkg_idname)  # type: ignore

