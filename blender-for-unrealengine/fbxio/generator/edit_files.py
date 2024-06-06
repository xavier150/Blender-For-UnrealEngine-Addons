def print_edit_error(text):
    print(f"\033[91m{text}\033[0m")

def add_header_to_file(file_path):
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
    with open(file_path, 'r+', encoding='utf-8') as f:
        content = f.read()
        f.seek(0, 0)
        f.write(header + content)
    ##print(f"Added header to {file_path}")

def lines_exist(file_path, search_string):
    with open(file_path, 'r+', encoding='utf-8') as f:
        content = f.read()

        # Remplacer "time" par "TESTUE" dans le contenu
        if search_string in content:
            return True

    return False

def replace_lines(file_path, search_string, content_to_add):
    with open(file_path, 'r+', encoding='utf-8') as f:
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

def add_after_lines(file_path, search_string, content_to_add):
    with open(file_path, 'r+', encoding='utf-8') as f:
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

def add_before_lines(file_path, search_string, content_to_add):
    with open(file_path, 'r+', encoding='utf-8') as f:
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

def add_quaternion_import(file_path):
    mathutils_content = '''from mathutils import Vector, Matrix'''
    new_mathutils_content = ''', Quaternion'''
    add_after_lines(file_path, mathutils_content, new_mathutils_content)