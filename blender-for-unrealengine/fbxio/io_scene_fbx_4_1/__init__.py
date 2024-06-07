# --------------------------------------------- 
# This file is a modified copy of Blender io_scene_fbx from Blender for the addon Blender-For-UnrealEngine.
# Do not modify directly this file!
# If you want to make modifications, you need: 
# 1. Do the changes in generator.py and edit_files.py
# 2. Run the file run_generator.py
# 
# More info: https://github.com/xavier150/Blender-For-UnrealEngine-Addons
# --------------------------------------------- 

from . import data_types
from . import encode_bin
from . import export_fbx_bin
from . import fbx_utils_threading
from . import fbx_utils

if "bpy" in locals():
	import importlib
	if "data_types" in locals():
		importlib.reload(data_types)
	if "encode_bin" in locals():
		importlib.reload(encode_bin)
	if "export_fbx_bin" in locals():
		importlib.reload(export_fbx_bin)
	if "fbx_utils_threading" in locals():
		importlib.reload(fbx_utils_threading)
# import_fbx and fbx_utils should not be reload or the export will produce StructRNA errors. 
#	if "fbx_utils" in locals():
#		importlib.reload(fbx_utils)
