# ====================== BEGIN GPL LICENSE BLOCK ============================
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.	 See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.	 If not, see <http://www.gnu.org/licenses/>.
#  All rights reserved.
#
# ======================= END GPL LICENSE BLOCK =============================

# ----------------------------------------------
#  BBPL -> BleuRaven Blender Python Library
#  BleuRaven.fr
#  XavierLoux.com
# ----------------------------------------------

import bpy
import importlib

classes = (
)



def register():
    for cls in classes:
        bpy.utils.register_class(cls)

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)


def update_data_variable(data, old_var_names, new_var_name, callback=None):
    for old_var_name in old_var_names:
        if old_var_name in data:
            try:
                if callback:
                    new_value = callback(data, old_var_name, new_var_name)
                    setattr(data, new_var_name, new_value)
                else:
                    setattr(data, new_var_name, data[old_var_name])

                del data[old_var_name]
                print(f'"{old_var_name}" updated to "{new_var_name}" in {data.name}')
            except Exception as e:
                print(f'Error updating "{old_var_name}" to "{new_var_name}" in {data.name}: {str(e)}')


class RigActionUpdater:
    """
    """
    def __init__(self):
        self.update_fcurve = 0
        self.remove_fcurve = 0
        self.print_log = False

    def update_action_curve_data_path(self, action, old_data_paths, new_data_path, remove_if_already_exists=False):
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
        cache_action_fcurves = []
        cache_data_paths = []
        for fcurve in action.fcurves:
            cache_action_fcurves.append(fcurve)
            cache_data_paths.append(fcurve.data_path)
            

        for action_fcurve in cache_action_fcurves:
            for old_data_path in old_data_paths:
                current_target = action_fcurve.data_path
                if old_data_path in current_target:

                    # ---

                    new_target = current_target.replace(old_data_path, new_data_path)
                    if new_target not in old_data_path:
                        action_fcurve.data_path = new_target
                        if self.print_log:
                            print(f'"{current_target}" updated to "{new_target}" in {action.name} action.')
                        self.update_fcurve += 1
                    else:
                        if remove_if_already_exists:
                            action.fcurves.remove(action_fcurve)
                            if self.print_log:
                                print(f'"{current_target}" can not be updated to "{new_target}" in {action.name} action. (Alredy exist!) It was removed in {action.name} action.')
                            self.remove_fcurve += 1
                            break #FCurve removed so no neew to test the other old_var_names
                        else:
                            if self.print_log:
                                print(f'"{current_target}" can not be updated to "{new_target}" in {action.name} action. (Alredy exist!)')

    def remove_action_curve_by_data_path(self, action, data_paths):
        """
        Remove FCurves from a given action based on specified data paths.

        Args:
            action (bpy.types.Action): The Blender action containing FCurves to be checked and removed.
            data_paths (list of str): A list of data paths to identify FCurves for removal.

        Returns:
            None
        """
        cache_action_fcurves = []
        cache_data_paths = []
        for fcurve in action.fcurves:
            cache_action_fcurves.append(fcurve)
            cache_data_paths.append(fcurve.data_path)

        for action_fcurve in cache_action_fcurves:
            for data_path in data_paths:
                current_target = action_fcurve.data_path
                if data_path in current_target:

                    # ---

                    action.fcurves.remove(action_fcurve)
                    if self.print_log:
                        print(f'"{current_target}" removed in {action.name} action.')
                    self.remove_fcurve += 1
                    break #FCurve removed so no neew to test the other old_var_names

    def edit_action_curve(self, action, data_paths, callback=None):
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
        cache_action_fcurves = []
        cache_data_paths = []
        for fcurve in action.fcurves:
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
        print(f'{self.update_fcurve} fcurve data_path have been updated.')
        print(f'{self.remove_fcurve} fcurve data_path have been removed.')
