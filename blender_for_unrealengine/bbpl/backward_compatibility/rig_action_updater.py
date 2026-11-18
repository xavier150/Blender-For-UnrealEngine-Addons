
from typing import Callable, List, Optional

import bpy

class RigActionUpdater:
    """
    A class to update FCurves in Blender actions by modifying their data paths.
    """
    def __init__(self):
        self.update_fcurve: int = 0
        self.remove_fcurve: int = 0
        self.print_log: bool = False

    def _fcurve_collections(self, action: bpy.types.Action):
        if bpy.app.version < (4, 4, 0):
            yield action.fcurves
        else:
            for layer in action.layers:
                for strip in layer.strips:
                    if strip.type == 'KEYFRAME':
                        for slot in action.slots:
                            channelbag = strip.channelbag(slot)
                            if channelbag is not None:
                                yield channelbag.fcurves

    def update_action_curve_data_path(self, action: bpy.types.Action, old_data_paths: List[str], new_data_path: str, remove_if_already_exists: bool = False, show_debug: bool = False):
        """
        Update the data paths of FCurves in a given action by replacing old data paths with a new one.

        Args:
            action (bpy.types.Action): The Blender action containing FCurves to be updated.
            old_data_paths (list of str): A list of old data paths to search for and replace.
            new_data_path (str): The new data path to replace the old ones with.
            remove_if_already_exists (bool, optional): If True, remove FCurves if the new data path already exists in them.
                Default is False.

        Returns:
            None
        """
        for fcurves in self._fcurve_collections(action):
            self._update_fcurve_collection(action, fcurves, old_data_paths, new_data_path, remove_if_already_exists, show_debug)

    def _update_fcurve_collection(self, action, fcurves, old_data_paths, new_data_path, remove_if_already_exists, show_debug):
        cache_action_fcurves: List[bpy.types.FCurve] = []
        cache_data_paths: List[str] = []
        for fcurve in fcurves:
            cache_action_fcurves.append(fcurve)
            cache_data_paths.append(fcurve.data_path)
            
        for action_fcurve in cache_action_fcurves:
            for old_data_path in old_data_paths:
                current_target = action_fcurve.data_path

                if old_data_path in current_target:
                    # ---
                    if show_debug: 
                        print(f"{old_data_path} found in {current_target} for action {action.name}.")

                    new_target = current_target.replace(old_data_path, new_data_path)
                    if new_target not in cache_data_paths:
                        action_fcurve.data_path = new_target
                        if self.print_log or show_debug:
                            print(f'"{current_target}" updated to "{new_target}" in {action.name} action.')
                        self.update_fcurve += 1
                    else:
                        if remove_if_already_exists:
                            fcurves.remove(action_fcurve)
                            if self.print_log or show_debug:
                                print(f'"{current_target}" can not be updated to "{new_target}" in {action.name} action. (Already exists!) It was removed in {action.name} action.')
                            self.remove_fcurve += 1
                            break #FCurve removed so no need to test the other old_var_names
                        else:
                            if self.print_log or show_debug:
                                print(f'"{current_target}" can not be updated to "{new_target}" in {action.name} action. (Already exists!)')
                else:
                    if show_debug: 
                        print(f"{old_data_path} not found in {current_target} for action {action.name}.")

    def remove_action_curve_by_data_path(self, action: bpy.types.Action, data_paths: List[str]):
        """
        Remove FCurves from a given action based on specified data paths.

        Args:
            action (bpy.types.Action): The Blender action containing FCurves to be checked and removed.
            data_paths (list of str): A list of data paths to identify FCurves for removal.

        Returns:
            None
        """
        for fcurves in self._fcurve_collections(action):
            self._remove_from_fcurve_collection(action, fcurves, data_paths)

    def _remove_from_fcurve_collection(self, action, fcurves, data_paths):
        cache_action_fcurves: List[bpy.types.FCurve] = []
        cache_data_paths: List[str] = []
        for fcurve in fcurves:
            cache_action_fcurves.append(fcurve)
            cache_data_paths.append(fcurve.data_path)

        for action_fcurve in cache_action_fcurves:
            for data_path in data_paths:
                current_target = action_fcurve.data_path
                if data_path in current_target:

                    # ---

                    fcurves.remove(action_fcurve)
                    if self.print_log:
                        print(f'"{current_target}" removed in {action.name} action.')
                    self.remove_fcurve += 1
                    break #FCurve removed so no need to test the other old_var_names

    def edit_action_curve(self, action: bpy.types.Action, data_paths: List[str], callback: Optional[Callable[[bpy.types.Action, bpy.types.FCurve, str], None]] = None):
        """
        Edit FCurves in a given action based on specified data paths using a custom callback function.

        Args:
            action (bpy.types.Action): The Blender action containing FCurves to be edited.
            data_paths (list of str): A list of data paths to identify FCurves for editing.
            callback (function, optional): A custom callback function that will be called for each matching FCurve.
                The callback function should accept three parameters: `action` (the action containing the FCurve),
                `fcurve` (the FCurve to be edited), and `data_path` (the matching data path). If callback is None,
                no editing is performed.

        Returns:
            None
        """
        for fcurves in self._fcurve_collections(action):
            self._edit_fcurve_collection(action, fcurves, data_paths, callback)

    def _edit_fcurve_collection(self, action, fcurves, data_paths, callback):
        cache_action_fcurves: List[bpy.types.FCurve] = []
        cache_data_paths: List[str] = []
        for fcurve in fcurves:
            cache_action_fcurves.append(fcurve)
            cache_data_paths.append(fcurve.data_path)


        for action_fcurve in cache_action_fcurves:
            for data_path in data_paths:
                current_target = action_fcurve.data_path
                if data_path in current_target:

                    # ---

                    if callback:
                        callback(action, action_fcurve, data_path)


    def print_update_log(self):
        """
        Print a log of the number of FCurves updated and removed.

        Args:
            None

        Returns:
            None
        """
        print(f'{self.update_fcurve} fcurve data_paths have been updated.')
        print(f'{self.remove_fcurve} fcurve data_paths have been removed.')
