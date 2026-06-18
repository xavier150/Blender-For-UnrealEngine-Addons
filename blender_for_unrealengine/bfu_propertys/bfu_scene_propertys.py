# SPDX-FileCopyrightText: Xavier Loux (BleuRaven)
#
# SPDX-License-Identifier: GPL-3.0-or-later

# ----------------------------------------------
#  Blender For UnrealEngine
#  https://github.com/xavier150/Blender-For-UnrealEngine-Addons
# ----------------------------------------------

import bpy
from .. import bbpl

classes = (
)



def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.Scene.bfu_active_tab = bpy.props.EnumProperty(
            items=(
            ('OBJECT', 'Object', 'Object tab.'),
            ('SCENE', 'Scene', 'Scene and world tab.')
            ),
            options={"HIDDEN", "SKIP_SAVE"}
        )
    

    bpy.types.Scene.bfu_active_object_tab = bpy.props.EnumProperty(
        items=(
            ('GENERAL', 'General', 'General object tab.'),
            ('ANIM', 'Animations', 'Animations tab.'),
            ('MISC', 'Misc', 'Misc tab.'),
            ('ALL', 'All', 'All tabs.')
            ),
            options={"HIDDEN", "SKIP_SAVE"}
        )


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)

    del bpy.types.Scene.bfu_active_object_tab
    del bpy.types.Scene.bfu_active_tab

