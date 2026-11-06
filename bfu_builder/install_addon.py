# Script that run in Blender to generate and install the addon Blender-For-UnrealEngine.

import importlib.util
import sys
from pathlib import Path

# ----------------------------------------------
# Configuration
# Récupérer le chemin addon_path avec l'argument nommé --addon_path
addon_source_path = None

# Chercher --addon_path dans les arguments
for i, arg in enumerate(sys.argv):
    if arg == '--addon_path' and i + 1 < len(sys.argv):
        path = Path(sys.argv[i + 1])
        if path.exists() and path.is_dir():
            addon_source_path = path
            print(f"Found --addon_path argument: {addon_source_path}")
            break

if addon_source_path is None:
    raise ValueError("--addon_path argument not found")

# ----------------------------------------------
def install_addon(addon_path: Path):
    print(f"Installing addon from {addon_path}")
    script_path = addon_path / "bbam" / "exec" / "install_from_blender.py" # Path to the install script
    
    # Prepare arguments for the script
    old_argv = sys.argv.copy()
    sys.argv = [str(script_path), "--current_only", str(True)] # Only build for the current Blender version

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