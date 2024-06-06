# --------------------------------------------- 
# This file is a modified copy of Blender io_scene_fbx from Blender for the addon Blender-For-UnrealEngine.
# Do not modify directly this file!
# If you want to make modifications, you need: 
# 1. Do the changes in generator.py and edit_files.py
# 2. Run the file run_generator.py
# 
# More info: https://github.com/xavier150/Blender-For-UnrealEngine-Addons
# --------------------------------------------- 

import bpy
import importlib
blender_version = bpy.app.version

if blender_version >= (4_1, 0):
    from . import io_scene_fbx_4_1 as current_fbxio 

if "current_fbxio" in locals():
    importlib.reload(current_fbxio)
