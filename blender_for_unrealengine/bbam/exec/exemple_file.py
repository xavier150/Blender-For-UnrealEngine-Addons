# SPDX-FileCopyrightText: Xavier Loux (BleuRaven)
#
# SPDX-License-Identifier: GPL-3.0-or-later

# ----------------------------------------------
#  BBAM -> BleuRaven Blender Addon Manager
#  https://github.com/xavier150/BBAM
# ----------------------------------------------

# Run this script in Blender to generate and install the addon.
# Ensure the paths in `addon_directories` point to the correct addon directories.
# For more details, visit the GitHub repository: https://github.com/xavier150/BBAM

from pathlib import Path
import sys
import platform
import importlib.util

# ----------------------------------------------
# Configuration
current_only: bool = False # Set to True to install only the current addon

# Windows
windows_GitHubBlenderAddon_path_win: str = r"Z:/GitHub Repos/Blender Addons"
windows_MMVSOther_Path_win: str = r"M:/MMVS_ProjectFiles/Other"

# Linux
linux_GitHubBlenderAddon_path: str = r"/mnt/ProjectWorkingFiles/GitHub Repos/Blender Addons"
linux_MMVSOther_Path: str = r"/media/bleuraven/Macro Micro VR Service/MMVS_ProjectFiles/Other"

# Detect the current operating system
current_system = platform.system()

if current_system == "Windows":
    GitHubBlenderAddon_path = windows_GitHubBlenderAddon_path_win
    MMVSOther_Path = windows_MMVSOther_Path_win
elif current_system == "Linux":
    GitHubBlenderAddon_path = linux_GitHubBlenderAddon_path
    MMVSOther_Path = linux_MMVSOther_Path
else:
    raise OSError(f"Unsupported operating system: {current_system}")

# List of addon directories as relative paths
addon_directories = [
    # Uncomment and adjust paths as needed
    (GitHubBlenderAddon_path, r"Blender-For-UnrealEngine-Addons/blender-for-unrealengine"),
    #(GitHubBlenderAddon_path, r"Modular-Auto-Rig/modular-auto-rig"),
    #(GitHubBlenderAddon_path, r"BleuRaven_Anim_Tools/bleuraven_anim_tools"),
    #(GitHubBlenderAddon_path, r"Graph-Curve-Filter/graph_curve_filter"),
    #(GitHubBlenderAddon_path, r"Adv-Euler-Filter/adv_euler_filter"),
    #(GitHubBlenderAddon_path, r"Copy-Visual-Position/copy_visual_position"),
    #(MMVSOther_Path, r"BlenderForMMVS/blender-for-mmvs"),
    #(MMVSOther_Path, r"MMVS_Addon_Skeletal_Mesh_Generate/mmvs-addon-skeletal-mesh-generate"),
]
# ----------------------------------------------

def install_addon(
    base_path: str,
    relative_path: str
):
    # Install or reinstall the addon
    addon_path = Path(base_path) / relative_path
    script_path = addon_path / "bbam" / "exec" / "install_from_blender.py"
    
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

for base_path, relative_path in addon_directories:
    install_addon(base_path, relative_path)

