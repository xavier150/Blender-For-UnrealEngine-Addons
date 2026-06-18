# SPDX-FileCopyrightText: Xavier Loux (BleuRaven)
#
# SPDX-License-Identifier: GPL-3.0-or-later

# ----------------------------------------------
#  BBPL -> BleuRaven Blender Python Library
#  https://github.com/xavier150/BBPL
# ----------------------------------------------

import bpy
import importlib
from . import functions
from . import utils
from . import types
from .functions import *

if "functions" in locals():
    importlib.reload(functions)
if "utils" in locals():
    importlib.reload(utils)
if "types" in locals():
    importlib.reload(types)

classes = (
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)  # type: ignore
    
    types.register()


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)  # type: ignore

    types.unregister()
