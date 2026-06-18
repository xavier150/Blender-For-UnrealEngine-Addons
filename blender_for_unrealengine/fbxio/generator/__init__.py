# SPDX-FileCopyrightText: Xavier Loux (BleuRaven)
#
# SPDX-License-Identifier: GPL-3.0-or-later

# ----------------------------------------------
#  BPL -> BleuRaven Python Library
#  https://github.com/xavier150/BPL
# ----------------------------------------------

import importlib
from . import generator
from . import edit_files
from . import edit_fbx_utils
from . import edit_export_fbx_bin

if "generator" in locals():
	importlib.reload(generator)
if "edit_files" in locals():
	importlib.reload(edit_files)
if "edit_fbx_utils" in locals():
	importlib.reload(edit_fbx_utils)
if "edit_export_fbx_bin" in locals():
	importlib.reload(edit_export_fbx_bin)
