# SPDX-FileCopyrightText: Xavier Loux (BleuRaven)
#
# SPDX-License-Identifier: GPL-3.0-or-later

# ----------------------------------------------
#  Blender For UnrealEngine
#  https://github.com/xavier150/Blender-For-UnrealEngine-Addons
# ----------------------------------------------

# Run this script in Blender to generate and install the addon Blender-For-UnrealEngine.
# Ensure the paths in `addon_directories` point to the correct addon directories.
# For more details: https://github.com/xavier150/Blender-For-UnrealEngine-Addons/wiki/Download-And-Installation-From-Dev-Branch

from pathlib import Path
import sys
import importlib.util

# ----------------------------------------------
# Configuration
current_only: bool = True # Set to build the addon for the current blender version.
addon_source_path: Path = Path("/home/bleuraven/Downloads/Blender-For-UnrealEngine-Addons-Dev/blender-for-unrealengine")

# ----------------------------------------------
def install_addon(addon_path: Path):
    script_path = addon_path / "bbam" / "exec" / "install_from_blender.py" # Path to the install script
    
    # Prepare arguments for the script
    old_argv = sys.argv.copy()
    sys.argv = [str(script_path), "--current_only", str(current_only)]

    # Run module
    try:
        spec = importlib.util.spec_from_file_location("install_from_blender", str(script_path))
        if spec is None or spec.loader is None:
            raise ImportError(f"Could not load spec or loader for {script_path}")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
    except Exception as e:
        raise ImportError(f"Failed to execute module from {script_path}: {e}")
    
    # Restore original sys.argv
    sys.argv = old_argv

install_addon(addon_source_path)