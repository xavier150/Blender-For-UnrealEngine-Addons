# SPDX-FileCopyrightText: Xavier Loux (BleuRaven)
#
# SPDX-License-Identifier: GPL-3.0-or-later

# ----------------------------------------------
#  Blender For UnrealEngine
#  https://github.com/xavier150/Blender-For-UnrealEngine-Addons
# ----------------------------------------------

import bpy
import importlib

from . import bfu_anim_action_operator_action_group
from . import bfu_anim_action_props
from . import bfu_anim_action_operators
from . import bfu_anim_action_ui
from . import bfu_anim_action_utils

if "bfu_anim_action_operator_action_group" in locals():
    importlib.reload(bfu_anim_action_operator_action_group)
if "bfu_anim_action_props" in locals():
    importlib.reload(bfu_anim_action_props)
if "bfu_anim_action_operators" in locals():
    importlib.reload(bfu_anim_action_operators)
if "bfu_anim_action_ui" in locals():
    importlib.reload(bfu_anim_action_ui)
if "bfu_anim_action_utils" in locals():
    importlib.reload(bfu_anim_action_utils)

classes = (
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    bfu_anim_action_operator_action_group.register()
    bfu_anim_action_props.register()
    bfu_anim_action_operators.register()

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)

    bfu_anim_action_operators.unregister()
    bfu_anim_action_props.unregister()
    bfu_anim_action_operator_action_group.unregister()