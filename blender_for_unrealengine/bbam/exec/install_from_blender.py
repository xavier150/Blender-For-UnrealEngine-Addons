# SPDX-FileCopyrightText: Xavier Loux (BleuRaven)
#
# SPDX-License-Identifier: GPL-3.0-or-later

# ----------------------------------------------
#  BBAM -> BleuRaven Blender Addon Manager
#  https://github.com/xavier150/BBAM
# ----------------------------------------------

from pathlib import Path
import argparse
import sys
import importlib.util

# ---------------------------------------------------------------
#  This script is used to install the BBAM addon from Blender.
#  See 'example_file.py' for running this script from Blender
# ----------------------------------------------------------------

parser = argparse.ArgumentParser(description="Installer BBAM depuis Blender")
parser.add_argument("--current_only", type=str, help="Build only addon for the current Blender version", default="False")
args = parser.parse_args()
current_only: bool = args.current_only.lower() == 'true'

# get bbam __init__.py file avec pathlib
bbam_path = (Path(__file__).parent.parent / "__init__.py").resolve()
module_name = "bbam"

# Load and run bbam
spec = importlib.util.spec_from_file_location(module_name, str(bbam_path))
if spec is None or spec.loader is None:
    raise ImportError(f"Cannot load spec or loader for {module_name} from {bbam_path}")
module = importlib.util.module_from_spec(spec)  # type: ignore
sys.modules[module_name] = module
spec.loader.exec_module(module)

# VS Code Type Checking
import typing
if typing.TYPE_CHECKING:
    import bbam
    module: bbam  # type: ignore

module.install_from_blender(current_only=current_only)

