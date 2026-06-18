# SPDX-FileCopyrightText: Xavier Loux (BleuRaven)
#
# SPDX-License-Identifier: GPL-3.0-or-later

# ----------------------------------------------
#  BBPL -> BleuRaven Blender Python Library
#  https://github.com/xavier150/BBPL
# ----------------------------------------------

import bpy
import importlib
from . import data_variable_updater
from . import rig_action_updater
from . import skin_weight_mesh_updater

if "data_variable_updater" in locals():
    importlib.reload(data_variable_updater)
if "rig_action_updater" in locals():
    importlib.reload(rig_action_updater)
if "skin_weight_mesh_updater" in locals():
    importlib.reload(skin_weight_mesh_updater)


classes = (
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
