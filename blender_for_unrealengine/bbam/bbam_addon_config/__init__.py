# SPDX-FileCopyrightText: Xavier Loux (BleuRaven)
#
# SPDX-License-Identifier: GPL-3.0-or-later

# ----------------------------------------------
#  BBAM -> BleuRaven Blender Addon Manager
#  https://github.com/xavier150/BBAM
# ----------------------------------------------

import importlib

from . import bbam_addon_config_type
from . import bbam_addon_config_utils

# Reloading modules if they're already loaded
if "bbam_addon_config_type" in locals():
    importlib.reload(bbam_addon_config_type)
if "bbam_addon_config_utils" in locals():
    importlib.reload(bbam_addon_config_utils)

