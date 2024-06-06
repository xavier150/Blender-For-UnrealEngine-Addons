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
elif blender_version >= (4_0, 0):
    from . import io_scene_fbx_4_0 as current_fbxio 
elif blender_version >= (3_6, 0):
    from . import io_scene_fbx_3_6 as current_fbxio 
elif blender_version >= (3_5, 0):
    from . import io_scene_fbx_3_5 as current_fbxio 
elif blender_version >= (3_4, 0):
    from . import io_scene_fbx_3_4 as current_fbxio 
elif blender_version >= (3_3, 0):
    from . import io_scene_fbx_3_3 as current_fbxio 
elif blender_version >= (3_2, 0):
    from . import io_scene_fbx_3_2 as current_fbxio 
elif blender_version >= (3_1, 0):
    from . import io_scene_fbx_3_1 as current_fbxio 
elif blender_version >= (2_93, 0):
    from . import io_scene_fbx_2_93 as current_fbxio 
elif blender_version >= (2_83, 0):
    from . import io_scene_fbx_2_83 as current_fbxio 

if "current_fbxio" in locals():
    importlib.reload(current_fbxio)
