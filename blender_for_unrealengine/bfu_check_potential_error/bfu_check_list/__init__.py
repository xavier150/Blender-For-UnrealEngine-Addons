# SPDX-FileCopyrightText: Xavier Loux (BleuRaven)
#
# SPDX-License-Identifier: GPL-3.0-or-later

# ----------------------------------------------
#  Blender For UnrealEngine
#  https://github.com/xavier150/Blender-For-UnrealEngine-Addons
# ----------------------------------------------

import bpy
import os
import importlib
import inspect
from typing import List, Any, Dict
from ..bfu_check_types import bfu_checker
from .. import bfu_check_utils
from ... import bpl
from ... import bfu_cached_assets
from ...bfu_cached_assets.bfu_cached_assets_blender_class import AssetToSearch, AssetDataSearchMode

# Dynamic import and reload for layers.
def get_modules_from_directory(directory: str):
    module_names: List[str] = []
    if os.path.isdir(directory):
        for file in os.listdir(directory):
            if file.endswith(".py") and file != "__init__.py":
                module_name = file[:-3]  # Remove '.py'
                module_names.append(module_name)
    return module_names

# Path to the 'types' directory (adjust based on project structure)
types_dir = os.path.join(os.path.dirname(__file__), "types")

# Import and reload modules dynamically
module_names = get_modules_from_directory(types_dir)

modules: Dict[str, Any] = {}
all_classes: List[Any] = []
for module_name in module_names:
    module = importlib.import_module(f".types.{module_name}", package=__package__)
    importlib.reload(module)
    modules[module_name] = module

    # Get all classes in the current module and avoid duplicates
    all_classes.extend([
        obj for _, obj in inspect.getmembers(module) 
        if inspect.isclass(obj) and obj.__module__ == module.__name__ and obj not in all_classes
    ])

def run_all_check()-> Dict[str, str]:
    # Clear existing potential errors before starting the checks
    bfu_check_utils.clear_potential_errors()

    # Collect all valid checker classes
    checker_classes = [
        cls for cls in all_classes
        if issubclass(cls, bfu_checker)
        and cls is not bfu_checker
        and (hasattr(cls, "run_asset_check") or hasattr(cls, "run_scene_check"))
    ]

    total: int = len(checker_classes)

    bpl.advprint.print_simple_title("Run check potential issues.")
    final_asset_cache = bfu_cached_assets.bfu_cached_assets_blender_class.get_final_asset_cache()
    final_asset_list_to_export = final_asset_cache.get_final_asset_list(AssetToSearch.ALL_ASSETS, AssetDataSearchMode.FULL, force_cache_update=True)

    check_info: Dict[str, str] = {}

    for index, my_check_cls in enumerate(checker_classes, start=1):
        counter = bpl.utils.CounterTimer()
        instance = my_check_cls()
        check_name = instance.check_name
        print(f"Check {index}/{total}: {check_name}...")

        # Count errors before and after to determine how many were added by this check
        before = len(bpy.context.scene.bfu_export_potential_errors)  # type: ignore

        # First run the scene check
        instance.run_scene_check(scene=bpy.context.scene)  # type: ignore

        # Then run the asset check for each asset in the final asset list
        for asset in final_asset_list_to_export:
            instance.run_asset_check(asset)


        after = len(bpy.context.scene.bfu_export_potential_errors)  # type: ignore
        new_issues = after - before

        # Display result with appropriate color
        if new_issues > 0:
            issue_result = bpl.color_set.red(f"{new_issues} issue(s)")
        else:
            issue_result = bpl.color_set.green("no issues")

        print(f"{check_name} finished in: {counter.get_str_time()} with {issue_result}\n")


    check_info["Total Check(s)"] = str(total) + " For more details, see console log."
    return check_info

def run_issue_correction(my_po_error) -> bool:
    checker_classes = [
        cls for cls in all_classes
        if issubclass(cls, bfu_checker)
        and cls is not bfu_checker
        and hasattr(cls, "run_correction")
    ]

    for my_check_cls in checker_classes:
        instance = my_check_cls()
        if hasattr(instance, "run_correction"):
            result = instance.run_correction(my_po_error)
            if result:
                return True
    return False