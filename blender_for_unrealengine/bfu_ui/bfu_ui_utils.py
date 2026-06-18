# SPDX-FileCopyrightText: Xavier Loux (BleuRaven)
#
# SPDX-License-Identifier: GPL-3.0-or-later

# ----------------------------------------------
#  Blender For UnrealEngine
#  https://github.com/xavier150/Blender-For-UnrealEngine-Addons
# ----------------------------------------------


import bpy


def DisplayPropertyFilter(active_tab:str, active_sub_tab:str) -> bool:
    # Define more easily the options which must be displayed or not

    scene = bpy.context.scene
    if scene.bfu_active_tab == active_tab == "OBJECT":
        if scene.bfu_active_object_tab == active_sub_tab or scene.bfu_active_object_tab == "ALL":
            return True
        
    if scene.bfu_active_tab == active_tab == "SCENE":
        return True
    
    return False



classes = (
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)

