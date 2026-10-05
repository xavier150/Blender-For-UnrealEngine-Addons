# SPDX-FileCopyrightText: Xavier Loux (BleuRaven)
#
# SPDX-License-Identifier: GPL-3.0-or-later

# ----------------------------------------------
#  BBPL -> BleuRaven Blender Python Library
#  https://github.com/xavier150/BBPL
# ----------------------------------------------

import bpy
import importlib
from . import utils
from . import item_types
from . import category_types
from . import list_types
from . import operators
from . import types

if "utils" in locals():
    importlib.reload(utils)
if "item_types" in locals():
    importlib.reload(item_types)
if "category_types" in locals():
    importlib.reload(category_types)
if "list_types" in locals():
    importlib.reload(list_types)
if "operators" in locals():
    importlib.reload(operators)
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