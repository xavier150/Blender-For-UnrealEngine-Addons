# SPDX-FileCopyrightText: 2024-2025 Xavier Loux (BleuRaven)
#
# SPDX-License-Identifier: GPL-3.0-or-later

# ----------------------------------------------
#  BBAM -> BleuRaven Blender Addon Manager
#  https://github.com/xavier150/BBAM
# ----------------------------------------------

import shutil
import tempfile
import sys
import os
from typing import Optional, List, Set
from . import manifest_generate
from . import bl_info_generate
from . import config
from . import blender_exec
from .bbam_addon_config.bbam_addon_config_type import BBAM_AddonConfig, BBAM_AddonBuild
from . import utils

def copy_addon_folder(
    src: str,
    dst: str,
    exclude_paths: List[str] = [],
    include_paths: List[str] = []
):
    """
    Copies the addon folder from 'src' to 'dst' while excluding specified files and folders.
    """

    exclude_folders = ["__pycache__", ".git", ".svn", ".vscode", ".idea", "node_modules"]
    exclude_files = [".blend1", ".blend2", ".blend3", ".blend4", ".blend5", ".blend6", ".blend7", ".blend8", ".blend9"]

    # Normalize paths for comparison
    exclude_paths = [os.path.normpath(path) for path in exclude_paths]
    include_paths = [os.path.normpath(path) for path in include_paths]

    # Ignore function to exclude specific files/folders during the copy
    def ignore_files(dir: str, files: List[str]) -> Set[str]:
        ignore_list: Set[str] = set()
        for file in files:
            file_path = os.path.join(dir, file)
            relative_path = os.path.normpath(os.path.relpath(file_path, src))

            # Exclure les dossiers par nom
            if file in exclude_folders and os.path.isdir(file_path):
                continue

            # Exclure les fichiers par extension
            if any(file.endswith(ext) for ext in exclude_files) and os.path.isfile(file_path):
                continue

            # Skip directories if only files should be ignored
            if os.path.isdir(file_path):
                continue

            # Check if the file path should be included
            if any(relative_path.startswith(os.path.normpath(path)) for path in include_paths):
                continue  # Skip excluding this file or folder

            # Check if the file path should be excluded
            if any(relative_path.startswith(os.path.normpath(path)) for path in exclude_paths):
                ignore_list.add(file)
        return ignore_list

    shutil.copytree(src, dst, ignore=ignore_files)


def create_temp_addon_folder(
    addon_path: str, 
    build_config: BBAM_AddonBuild,
) -> str:
    """
    Creates a temporary folder for the addon, copies relevant files, and generates the manifest.
    """
    

    # Step 1: Create a temporary directory for the addon
    temp_dir = tempfile.mkdtemp(prefix="blender_addon_")
    temp_addon_path = os.path.join(temp_dir, os.path.basename(addon_path))

    # Step 2: Copy addon folder to temporary directory, excluding specified paths
    exclude_paths = build_config.exclude_paths
    include_paths = build_config.include_paths
    exclude_paths.append("bbam/")  # Exclude addon manager from the final build
    copy_addon_folder(addon_path, temp_addon_path, exclude_paths, include_paths)
    print(f"Copied build '{build_config.build_id}' to temporary location")
    print(f"Path: {temp_addon_path}")
    return temp_addon_path

def generate_addon_files(
    addon_path: str, 
    addon_config: BBAM_AddonConfig,
    build_config: BBAM_AddonBuild,
    show_debug: bool = True
) -> None:
    
    generate_using_extension_command = utils.get_generate_using_extension_command(build_config.generate_method, build_config.blender_version_min)

    if generate_using_extension_command:
        new_manifest = manifest_generate.generate_new_manifest(addon_config, build_config)
        manifest_generate.save_addon_manifest(addon_path, new_manifest, show_debug)
    else:
        new_manifest = bl_info_generate.generate_new_bl_info(addon_config, build_config)
        bl_info_generate.update_file_bl_info(addon_path, new_manifest, show_debug)

    # Apply hard modifications in python files
    if build_config.hard_modifications:
        for root, _, files in os.walk(addon_path):
            for file in files:
                if file.endswith('.py'):
                    file_path = os.path.join(root, file)

                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                        
                        for modification_key in build_config.hard_modifications:
                            if modification_key == "replace":
                                for modification in build_config.hard_modifications[modification_key]:
                                    content = content.replace(modification["search"], modification["replace"])

                        with open(file_path, 'w', encoding='utf-8') as f:
                            f.write(content)
                    except Exception as e:
                        text = f"Error applying hard modifications to {file_path}: {e}"
                        red_text = f"\033[31m{text}\033[0m"
                        print(red_text, file=sys.stderr)


def get_zip_output_filename(
    addon_path: str, 
    addon_config: BBAM_AddonConfig,
    build_config: BBAM_AddonBuild,
):
    """
    Generates the output filename for the ZIP file based on naming conventions in the manifest.
    """

    # Formatting output filename
    version_str = addon_config.addon_manifest.get_version_as_string()
    output_folder_path = os.path.abspath(os.path.join(addon_path, '..', config.build_output_folder))
    formatted_file_name = build_config.naming.replace("{Name}", build_config.pkg_id).replace("{Version}", version_str)
    output_filepath = os.path.join(output_folder_path, formatted_file_name)
    return output_filepath

def zip_addon_folder(
    src: str, 
    addon_path: str, 
    addon_config: BBAM_AddonConfig,
    build_config: BBAM_AddonBuild,
    blender_executable_path: str
) -> Optional[str]:
    """
    Creates a ZIP archive of the addon folder, either through Blender's extension command
    or by using a simple ZIP method.
    """
    generate_using_extension_command = utils.get_generate_using_extension_command(build_config.generate_method, build_config.blender_version_min)

    # Define output file path and ensure the output directory exists
    output_filepath = get_zip_output_filename(addon_path, addon_config, build_config)
    output_dir = os.path.dirname(output_filepath)
    os.makedirs(output_dir, exist_ok=True)



    # Run addon zip process based on the specified generation method
    if generate_using_extension_command:
        print("Start build with extension command")
        result = blender_exec.build_extension(src, output_filepath, blender_executable_path)
        if result.returncode == 0:
            created_filename = blender_exec.get_build_file(result)
            if created_filename:
                print(f"EXTENTION_COMMAND created successfully at {created_filename}")
                return created_filename
            else:
                print("Error: No created filename found in the result of the extension command.")
                return None
        else:  
            print(f"Error: Build failed with return code {result.returncode}.", file=sys.stderr)
            print(result.stdout, file=sys.stderr)
            print(result.stderr, file=sys.stderr)
            return None

    else:
        print("Start creating simple ZIP file with root folder using shutil")

        # Specify the root folder name inside the ZIP file
        root_folder_name = build_config.module

        # Create a temporary directory
        with tempfile.TemporaryDirectory() as temp_dir:
            # Copy the source folder to a temporary root folder
            temp_root = os.path.join(temp_dir, root_folder_name)
            shutil.copytree(src, temp_root)

            # Use shutil to create the ZIP archive from the temporary directory
            base_name = os.path.splitext(output_filepath)[0]  # Path without .zip extension
            shutil.make_archive(base_name, 'zip', temp_dir, root_folder_name)
        
        print(f"SIMPLE_ZIP created successfully at {output_filepath}")
        return output_filepath
    
def validate_zip_file(
    zip_file: str, 
    build_config: BBAM_AddonBuild,
    blender_executable_path: str
) -> bool:
    """
    Validates the generated ZIP file
    """
    generate_using_extension_command = utils.get_generate_using_extension_command(build_config.generate_method, build_config.blender_version_min)


        # Run addon zip process based on the specified generation method
    if generate_using_extension_command:
        print("Start validate with extension command")
        result = blender_exec.validate_extension(zip_file, blender_executable_path)
        if result.returncode == 0:
            print("Validation successful.")
            return True
        else:
            print(f"Validation failed with return code {result.returncode}.", file=sys.stderr)
            print(result.stdout, file=sys.stderr)
            print(result.stderr, file=sys.stderr)
            return False

    else:
        print("No validation needed for SIMPLE_ZIP method.")
        return True
    
    return False

    
