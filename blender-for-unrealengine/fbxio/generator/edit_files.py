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
    print(f"Added header to {file_path}")