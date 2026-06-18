# SPDX-FileCopyrightText: Xavier Loux (BleuRaven)
#
# SPDX-License-Identifier: GPL-3.0-or-later

# ----------------------------------------------
#  BPL -> BleuRaven Python Library
#  https://github.com/xavier150/BPL
# ----------------------------------------------

import os
import platform
import shutil
import re
from typing import List, Tuple
from pathlib import Path
from . import edit_files
from . import edit_fbx_utils
from . import edit_export_fbx_bin
from . import config

# Detect the current operating system
current_system = platform.system()
if current_system == "Windows":
    blender_install_path: Path = config.windows_blender_install_path
elif current_system == "Linux":
    blender_install_path: Path = config.linux_blender_install_path
else:
    raise EnvironmentError("Unsupported operating system for Blender installation path.")



# Get the directory of the current script
current_script_directory: Path = Path(__file__).resolve().parent
# Define the parent directory (one level up from the current script directory)
parent_directory: Path = current_script_directory.parent

class FBXExporterGenerate:
    def __init__(self, version: Tuple[int, int, int], folder: str, files: List[str], new_io_fbx: str):
        self.version: Tuple[int, int, int] = version
        self.folder: str = folder
        self.files: List[str] = files
        self.fbx_addon_version: Tuple[int, int, int] = (0, 0, 0)  # Default version
        self.io_fbx: str = new_io_fbx

        self.is_valid: bool = self.run_init_check()

    def run_init_check(self) -> bool:
        def print_red(message: str):
            print(f"\033[91m{message}\033[0m")
        if not self.get_addon_path().exists():
            print_red(f"Addon path does not exist: {self.get_addon_path()}")
            return False
        if not self.get_addon_init_path().exists():
            print_red(f"Addon init path does not exist: {self.get_addon_init_path()}")
            return False
        return True

    def get_str_version(self):
        return str(self.version[0])+"_"+str(self.version[1])
    
    def get_folder_str_version(self):
        return str(self.version[0])+"."+str(self.version[1])

    def get_addon_path(self) -> Path:
        addon_path = Path(blender_install_path) / self.folder / self.io_fbx
        return addon_path.resolve()
    
    def get_addon_init_path(self) -> Path:
        addon_path = Path(blender_install_path) / self.folder / self.io_fbx / '__init__.py'
        return addon_path.resolve()

    def run_generate(self) -> Tuple[Tuple[int, int, int], str]:
        # Create the destination folder in the parent directory
        self.update_fbx_addon_version()
        version_as_module: str = self.get_str_version()
        print("Start Generate ", version_as_module)
        dest_folder: Path = parent_directory / (config.io_scene_fbx_prefix + version_as_module)
        if not dest_folder.exists():
            dest_folder.mkdir(parents=True)

        new_files: List[Path] = self.copy_export_files(dest_folder)
        new_files.append(self.create_init_file(dest_folder))

        for new_file in new_files:
            print("Process file:", new_file)
            edit_files.add_header_to_file(new_file)
            if str(new_file).endswith('export_fbx_bin.py'):
                edit_export_fbx_bin.update_export_fbx_bin(new_file, self.version, self.fbx_addon_version)
            if str(new_file).endswith('fbx_utils.py'):
                edit_fbx_utils.update_fbx_utils(new_file, self.version)
        return (self.version, version_as_module)
    
    def update_fbx_addon_version(self):
        source_file = Path(self.get_addon_init_path())

        with open(source_file, 'r', newline='\n') as file:
            file_content = file.read()
            
            # Use regular expressions to find bl_info and version
            bl_info_match = re.search(r'bl_info\s*=\s*\{([^}]*)\}', file_content, re.DOTALL)
            if bl_info_match:
                bl_info_lines = bl_info_match.group(1).split('\n')

                # Parse each line to find the version
                for line in bl_info_lines:
                    if 'version' in line:
                        match = re.search(r'\(([^)]+)\)', line)
                        if match:
                            elements = match.group(1).replace(' ', '').split(',')
                            self.fbx_addon_version = tuple(map(int, elements))
                        else:
                            print("Version tuple not found in bl_info")
                        return
            else:
                print("bl_info not found in __init__.py")
            


    def copy_export_files(self, dest_folder: Path) -> List[Path]:
        addon_folder = self.get_addon_path()
        new_files: List[Path] = []
        # Verify if the source folder exists
        if not addon_folder.exists():
            print(f"Source folder does not exist: {addon_folder}")
            return new_files

        # Copy only specified files from the source to the destination
        for file_name in self.files:
            source_file: Path = addon_folder / file_name
            destination_file: Path = dest_folder / file_name
            if source_file.exists():
                shutil.copy2(source_file, destination_file)
                # Force LF line endings
                with open(destination_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                with open(destination_file, 'w', encoding='utf-8', newline='\n') as f:
                    f.write(content)
                new_files.append(destination_file)
            else:
                print(f"File does not exist: {source_file}")

        print(f"Copied specified FBX exporter files.")
        print(f"Source: {addon_folder}")
        print(f"Target: {dest_folder}")
        return new_files


    def create_init_file(self, dest_folder: Path) -> Path:
        files = self.files
        init_file_path = dest_folder / '__init__.py'
        with open(init_file_path, 'w', newline='\n') as init_file:
            # Write imports
            for file_name in files:
                module_name = os.path.splitext(file_name)[0]
                init_file.write(f"from . import {module_name}\n")
            
            
            init_file.write('\nif "bpy" in locals():\n')
            init_file.write("\timport importlib\n")
            
            # Write reloads
            for file_name in files:
                module_name = os.path.splitext(file_name)[0]
                if module_name in ["import_fbx", "fbx_utils"]:
                    
                    init_file.write(f"# import_fbx and fbx_utils should not be reload or the export will produce StructRNA errors. \n")
                    init_file.write(f"#\tif \"{module_name}\" in locals():\n")
                    init_file.write(f"#\t\timportlib.reload({module_name})\n")
                else:
                    init_file.write(f"\tif \"{module_name}\" in locals():\n")
                    init_file.write(f"\t\timportlib.reload({module_name})\n")

        print(f"Created __init__.py in {dest_folder}")
        return init_file_path

def run_all_generate():
    os.system('cls' if os.name == 'nt' else 'clear')
    clean_previous_exports()

    generated_list: List[Tuple[Tuple[int, int, int], str]] = []
    for generator_config in config.generator_configs:
        generator = FBXExporterGenerate(generator_config.version, generator_config.folder, generator_config.files, generator_config.io_fbx)
        if generator.is_valid:
            generated_list.append(generator.run_generate())
       
    root_init_file = create_root_init_file(generated_list)
    edit_files.add_header_to_file(root_init_file)


def create_root_init_file(generated_list: List[Tuple[Tuple[int, int, int], str]]) -> Path:
    init_file_path: Path = Path(parent_directory) / '__init__.py'
    with open(init_file_path, 'w', newline='\n') as init_file:
        init_file.write("import bpy\n")
        init_file.write("import importlib\n")
        init_file.write("blender_version = bpy.app.version\n\n")

        # Write conditional imports
        last_import: str = ""
        for x, generate in enumerate(generated_list):
            version = generate[0]
            str_version = generate[1]
            if x == 0:
                init_file.write(f"if blender_version >= {version}:\n")
            else:
                init_file.write(f"elif blender_version >= {version}:\n")
            last_import = f"    from . import {config.io_scene_fbx_prefix}{str_version} as current_fbxio \n"
            init_file.write(last_import)
            
        init_file.write(f"else:\n")
        if last_import:
            init_file.write(last_import + " #Fall back") # Always fall back to the last version (Used for Blender 2.80 to 2.82)
        else:
            init_file.write(f"    print('ERROR, no custom fbx exporter found for this version of Blender!') \n")
            init_file.write(f"    print(\"Blender version detected:\", blender_version)\n")

        init_file.write("\n")
        
        # Write reloads
        init_file.write(f"if \"current_fbxio\" in locals():\n")
        init_file.write(f"    importlib.reload(current_fbxio)\n")

    print(f"Created root __init__.py in {parent_directory}")
    return init_file_path

def clean_previous_exports():
    for item in os.listdir(parent_directory):
        if item.startswith(config.io_scene_fbx_prefix):
            folder_path: Path = Path(parent_directory) / item
            if folder_path.is_dir():
                shutil.rmtree(folder_path)
                print(f"Deleted folder: {folder_path}")


