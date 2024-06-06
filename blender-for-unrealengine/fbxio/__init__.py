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
