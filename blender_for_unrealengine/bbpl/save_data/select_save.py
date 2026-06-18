# SPDX-FileCopyrightText: Xavier Loux (BleuRaven)
#
# SPDX-License-Identifier: GPL-3.0-or-later

# ----------------------------------------------
#  BBPL -> BleuRaven Blender Python Library
#  https://github.com/xavier150/BBPL
# ----------------------------------------------

import bpy
from typing import List, Optional
from .. import utils

class UserSelectSave():
    """
    Manager for user selection.
    """

    def __init__(self):
        # Select
        self.user_active: Optional[bpy.types.Object] = None
        self.user_active_name: Optional[str] = None
        self.user_selecteds: List[bpy.types.Object] = []
        self.user_selected_names: List[str] = []

        # Stats
        self.user_mode: Optional[str] = None

    def save_current_select(self):
        """
        Save user selection.
        """

        # Save data (This can take time)

        # Select
        self.user_active = bpy.context.active_object  # Save current active object
        if self.user_active:
            self.user_active_name = self.user_active.name

        self.user_selecteds = bpy.context.selected_objects  # Save current selected objects
        self.user_selected_names = [obj.name for obj in bpy.context.selected_objects]

    def reset_select(self, use_names: bool = False):
        """
        Reset user selection at the last save.
        """

        scene = bpy.context.scene
        if scene is None:
            return

        self.save_mode(use_names)
        utils.safe_mode_set("OBJECT", bpy.ops.object)  # type: ignore
        for obj in bpy.context.selected_objects:
            obj.select_set(False)

        view_layer = bpy.context.view_layer
        if view_layer:
            if use_names:
                for obj in scene.objects:
                    if obj.name in self.user_selected_names:
                            if obj.name in view_layer.objects:
                                scene.objects.get(obj.name).select_set(True)  # Use the name because can be duplicated name  # type: ignore

                if self.user_active_name:
                    if self.user_active_name in scene.objects:
                        if self.user_active_name in view_layer.objects:
                            view_layer.objects.active = scene.objects.get(self.user_active_name)
            
            
            else:
                for obj in scene.objects:  # Resets previous selected object if still exist
                    if obj in self.user_selecteds:
                        obj.select_set(True)  # type: ignore

                view_layer.objects.active = self.user_active

        self.reset_mode_at_save()

    def save_mode(self, use_names: bool = False):
        """
        Save user mode.
        """

        user_active = self.get_user_active(use_names)
        if user_active:
            if bpy.ops.object.mode_set.poll():  # type: ignore
                self.user_mode = user_active.mode  # Save current mode  # type: ignore

    def reset_mode_at_save(self):
        """
        Reset user mode at the last save.
        """
        if self.user_mode:
            utils.safe_mode_set(self.user_mode, bpy.ops.object)  # type: ignore

    def get_user_active(self, use_names: bool = False) -> Optional[bpy.types.Object]:

        scene = bpy.context.scene
        if scene is None:
            return None
        
        if use_names:
            view_layer = bpy.context.view_layer
            if view_layer:
                if self.user_active_name:
                    if self.user_active_name in scene.objects:
                        if self.user_active_name in view_layer.objects:
                            return scene.objects.get(self.user_active_name)
            return None
        else:
            return self.user_active