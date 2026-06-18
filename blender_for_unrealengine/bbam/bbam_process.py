# SPDX-FileCopyrightText: Xavier Loux (BleuRaven)
#
# SPDX-License-Identifier: GPL-3.0-or-later

# ----------------------------------------------
#  BBAM -> BleuRaven Blender Addon Manager
#  https://github.com/xavier150/BBAM
# ----------------------------------------------

import os

from . import config
from . import addon_file_management
from . import utils
from . import blender_utils
from . import bbam_addon_config
from .bbam_addon_config.bbam_addon_config_type import BBAM_AddonConfig

def process_install_from_blender(current_only: bool = False):
    print("Installing addon from Blender...")
    print(f"Current only: {current_only}")

    """
    Loads the addon's configuration file to retrieve its manifest data and initiates
    the installation process within Blender.
    """

    # Construct absolute paths for addon and manifest file
    addon_path = os.path.abspath(os.path.join(__file__, '..', '..'))

    addon_config = bbam_addon_config.bbam_addon_config_utils.load_addon_config_from_json(addon_path)
    if addon_config is not None:
        print("Successfully loaded addon configuration.")
        install_from_blender_with_build_data(addon_path, addon_config, current_only)
    else:  
        print(f"Error: Failed to load addon configuration from '{addon_path}'.")


def install_from_blender_with_build_data(
    addon_path: str, 
    addon_config: BBAM_AddonConfig,
    current_only: bool = False,
):
    """
    Manages the addon installation in Blender based on the build data from the manifest.
    """
    # Import bpy lib here when exec from Blender.
    import bpy

    # Get Blender executable path from bpy
    blender_executable_path = bpy.app.binary_path

    # Process each build specified in the manifest data
    for build_key in addon_config.builds:
        build_data = addon_config.builds[build_key]
        should_install = utils.get_should_install_for_curren_version(build_data.auto_install_range)
        if current_only:
            # Build only for the current Blender version, so build only if the addon should be installed
            should_build = should_install
        else:
            should_build = True

        if should_build:
            print("")
            print("---------------------------------------------------------")
            print(f"Processing build: {build_key}")

            steps = utils.BBAM_TimedTaskManager()
            steps.set_step_count(5)
            steps.start_new_task(1, "Create temporary addon folder")
            # Create temporary addon folder
            temp_addon_path = addon_file_management.create_temp_addon_folder(
                addon_path = addon_path, 
                build_config = build_data,
            )

            steps.end_current_task_and_start_new(2, "Generate addon files")
            addon_file_management.generate_addon_files(
                addon_path = temp_addon_path, 
                addon_config = addon_config,
                build_config = build_data,
                show_debug = config.show_debug,
            )

            steps.end_current_task_and_start_new(3, "Start build addon as ZIP")
            # Zip the addon folder for installation
            zip_file = addon_file_management.zip_addon_folder(
                src = temp_addon_path, 
                addon_path = addon_path, 
                addon_config = addon_config,
                build_config = build_data,
                blender_executable_path = blender_executable_path
            )
            steps.end_current_task()
            
            if zip_file:
                steps.start_new_task(4, "Validate ZIP file")
                validate_success = addon_file_management.validate_zip_file(
                    zip_file = zip_file, 
                    build_config = build_data,
                    blender_executable_path = blender_executable_path
                )
                steps.end_current_task()

                if validate_success:
                    # Check if the addon should be installed based on Blender's version
                    if should_install:
                        pkg_id = build_data.pkg_id
                        module = build_data.module
                        # Uninstall previous versions if they exist
                        steps.start_new_task(4, "Uninstall previous addon version")
                        blender_utils.uninstall_addon_from_blender(pkg_id, module)

                        steps.end_current_task_and_start_new(5, "Install addon from ZIP")
                        blender_utils.install_zip_addon_from_blender(zip_file, module)
                        steps.end_current_task()
                    else:
                        print(f"Skipping installation for build '{build_key}'.")

                else:
                    print(f"Validation failed for build '{build_key}'. Skipping installation.")
            else:
                print(f"Error: Failed to create ZIP file for build '{build_key}'.")