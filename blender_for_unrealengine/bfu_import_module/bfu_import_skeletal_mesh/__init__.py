# SPDX-FileCopyrightText: Xavier Loux (BleuRaven)
#
# SPDX-License-Identifier: GPL-3.0-or-later

# ----------------------------------------------
#  Blender For UnrealEngine
#  https://github.com/xavier150/Blender-For-UnrealEngine-Addons
# ----------------------------------------------

import importlib

from . import bfu_import_skeletal_mesh_utils

if "bfu_import_skeletal_mesh_utils" in locals():
    importlib.reload(bfu_import_skeletal_mesh_utils)
