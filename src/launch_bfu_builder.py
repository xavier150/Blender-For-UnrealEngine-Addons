import platform
import subprocess
from pathlib import Path

# Get script path and its directory
script_path = Path(__file__).resolve()
script_directory = script_path.parent.parent

if platform.system() == "Windows":
    script_to_call = script_directory / "run_bfu_builder.py"
    python_cmd = "python"
else:
    script_to_call = script_directory / "run_bfu_builder.py"
    # For Linux it use source ~/venv/bin/activate
    python_cmd = Path.home() / "venvs/blender_for_unrealengine/bin/python"

# Prepare arguments as strings
args = [
    str(script_to_call),
]
subprocess.run([python_cmd] + args)