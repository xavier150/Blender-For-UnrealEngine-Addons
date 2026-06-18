# SPDX-FileCopyrightText: Xavier Loux (BleuRaven)
#
# SPDX-License-Identifier: GPL-3.0-or-later

# ----------------------------------------------
#  BPL -> BleuRaven Python Library
#  https://github.com/xavier150/BPL
# ----------------------------------------------

from pathlib import Path

def print_edit_error(text: str):
    print(f"\033[91m{text}\033[0m")

def get_file_content(file_path: Path) -> str:
    # Lire le contenu du fichier Python
    with open(file_path, 'r+', encoding='utf-8', newline='\n') as f:
        content = f.read()
    return content

def add_header_to_file(file_path: Path):
    header = (
        "# --------------------------------------------- \n"
        "# This file is a modified copy of Blender io_scene_fbx from Blender for the addon Blender-For-UnrealEngine.\n"
        "# Do not modify directly this file!\n"
        "# If you want to make modifications, you need: \n"
        "# 1. Do the changes in generator.py and edit_files.py\n"
        "# 2. Run the file run_generator.py\n"
        "# \n"
        "# More info: https://github.com/xavier150/Blender-For-UnrealEngine-Addons\n"
        "# --------------------------------------------- \n"
        "\n"
    )

    try:
        with open(file_path, 'r', encoding='utf-8', newline='\n') as f:
            original_content = f.read()
    except FileNotFoundError:
        original_content = ""  # Si le fichier n'existe pas, le contenu sera vide

    with open(file_path, 'w', encoding='utf-8', newline='\n') as f:
        f.write(header + original_content)

def lines_exist(file_path: Path, search_string: str) -> bool:
    with open(file_path, 'r+', encoding='utf-8', newline='\n') as f:
        content = f.read()

        # Remplacer "time" par "TESTUE" dans le contenu
        if search_string in content:
            return True

    return False

def replace_lines(file_path: Path, search_string: str, content_to_add: str):
    with open(file_path, 'r+', encoding='utf-8', newline='\n') as f:
        content = f.read()

        # Remplacer "time" par "TESTUE" dans le contenu
        if search_string in content:
            content = content.replace(search_string, content_to_add)
        else:
            print_edit_error(f"String {search_string} not found in {file_path}")

        # Write back the modified content
        f.seek(0)
        f.write(content)
        f.truncate()

def add_after_lines(file_path: Path, search_string: str, content_to_add: str):
    with open(file_path, 'r+', encoding='utf-8', newline='\n') as f:
        content = f.read()

        # Remplacer "time" par "TESTUE" dans le contenu
        if search_string in content:
            content = content.replace(search_string, search_string+content_to_add)
        else:
            print_edit_error(f"String {search_string} not found in {file_path}")

        # Write back the modified content
        f.seek(0)
        f.write(content)
        f.truncate()

def add_before_lines(file_path: Path, search_string: str, content_to_add: str):
    with open(file_path, 'r+', encoding='utf-8', newline='\n') as f:
        content = f.read()

        # Remplacer "time" par "TESTUE" dans le contenu
        if search_string in content:
            content = content.replace(search_string, content_to_add+search_string)
        else:
            print_edit_error(f"String {search_string} not found in {file_path}")

        # Write back the modified content
        f.seek(0)
        f.write(content)
        f.truncate()

def add_quaternion_import(file_path: Path):
    mathutils_content = '''from mathutils import Vector, Matrix'''
    new_mathutils_content = ''', Quaternion'''
    add_after_lines(file_path, mathutils_content, new_mathutils_content)