import bpy
import importlib
blender_version = bpy.app.version

if blender_version >= (4_1, 0):
    from . import io_scene_fbx_4_1 as current_fbxio 

if "current_fbxio" in locals():
    importlib.reload(current_fbxio)
