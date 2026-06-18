# SPDX-FileCopyrightText: Xavier Loux (BleuRaven)
#
# SPDX-License-Identifier: GPL-3.0-or-later

# ----------------------------------------------
#  BBAM -> BleuRaven Blender Addon Manager
#  https://github.com/xavier150/BBAM
# ----------------------------------------------

import os
import importlib

from . import bbam_addon_config
from . import bbam_process
from . import config
from . import manifest_generate
from . import bl_info_generate
from . import addon_file_management
from . import utils
from . import blender_exec
from . import blender_utils

# Reloading modules if they're already loaded
if "bbam_addon_config" in locals():
    importlib.reload(bbam_addon_config)
if "bbam_process" in locals():
    importlib.reload(bbam_process)
if "config" in locals():
    importlib.reload(config)
if "manifest_generate" in locals():
    importlib.reload(manifest_generate)
if "bl_info_generate" in locals():
    importlib.reload(bl_info_generate)
if "addon_file_management" in locals():
    importlib.reload(addon_file_management)
if "utils" in locals():
    importlib.reload(utils)
if "blender_exec" in locals():
    importlib.reload(blender_exec)
if "blender_utils" in locals():
    importlib.reload(blender_utils)


def install_from_blender(current_only: bool = False):
    # Clear the console before starting the installation process
    os.system('cls' if os.name == 'nt' else 'clear')
    bbam_process.process_install_from_blender(current_only)