import importlib
from . import generator
from . import edit_files

if "generator" in locals():
	importlib.reload(generator)
if "edit_files" in locals():
	importlib.reload(edit_files)
