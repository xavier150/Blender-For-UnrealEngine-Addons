from pathlib import Path
from typing import List, Tuple, Optional


windows_blender_install_path: Path = Path("C:/Program Files/Blender Foundation")
linux_blender_install_path: Path = Path("/media/bleuraven/Game Engines/BlenderBuilds")

io_scene_fbx_prefix = "io_scene_fbx_"

export_fbx_files: List[str] = [
    'data_types.py',
    'encode_bin.py',
    'export_fbx_bin.py',
    'fbx_utils.py',
]

export_fbx_files_with_threading: List[str] = [
    'data_types.py',
    'encode_bin.py',
    'export_fbx_bin.py',
    'fbx_utils_threading.py',
    'fbx_utils.py',
]

all_export_fbx_files: List[str] = [
    'data_types.py',
    'encode_bin.py',
    'export_fbx_bin.py',
    'fbx_utils_threading.py',
    'fbx_utils.py',
    'fbx2json.py',
    'import_fbx.py',
    'json2fbx.py',
    'parse_fbx.py',
]

all_export_fbx_files_with_init: List[str] = [
    '__init__.py',
    'data_types.py',
    'encode_bin.py',
    'export_fbx_bin.py',
    'fbx_utils_threading.py',
    'fbx_utils.py',
    'fbx2json.py',
    'import_fbx.py',
    'json2fbx.py',
    'parse_fbx.py',
]

class GeneratorConfig():

    def __init__(self, version: Tuple[int, int, int], folder: str, files: List[str], new_io_fbx: Optional[str] = None):
        self.version: Tuple[int, int, int] = version
        self.version: Tuple[int, int, int] = version
        self.folder: str = folder
        self.files: List[str] = files
        if new_io_fbx:
            self.io_fbx: str = new_io_fbx
        else:
            self.io_fbx: str = r"scripts/addons/io_scene_fbx"

# generated var needs to be ordered from new to older.
generator_configs: List[GeneratorConfig] = []

# For the moment I will continue to use Blender 5.0 FBXIO for next versions. 
# I will remove the custom FBXIO in future and ask people to use the standard FBX or the glTF that furure proof.
generator_configs.append(GeneratorConfig((5, 0, 0), r"Blender 5.0/5.0", export_fbx_files_with_threading, r"scripts/addons_core/io_scene_fbx/"))
generator_configs.append(GeneratorConfig((4, 5, 0), r"Blender 4.5/4.5", export_fbx_files_with_threading, r"scripts/addons_core/io_scene_fbx/")) # Blender 4.5.5
generator_configs.append(GeneratorConfig((4, 4, 0), r"Blender 4.4/4.4", export_fbx_files_with_threading, r"scripts/addons_core/io_scene_fbx/")) 
generator_configs.append(GeneratorConfig((4, 3, 0), r"Blender 4.3/4.3", export_fbx_files_with_threading, r"scripts/addons_core/io_scene_fbx/")) # Blender 4.3.2
generator_configs.append(GeneratorConfig((4, 2, 0), r"Blender 4.2/4.2", export_fbx_files_with_threading, r"scripts/addons_core/io_scene_fbx/")) # Blender 4.2.9
generator_configs.append(GeneratorConfig((4, 1, 0), r"Blender 4.1/4.1", export_fbx_files_with_threading))
generator_configs.append(GeneratorConfig((4, 0, 0), r"Blender 4.0/4.0", export_fbx_files))
generator_configs.append(GeneratorConfig((3, 6, 0), r"Blender 3.6/3.6", export_fbx_files))
generator_configs.append(GeneratorConfig((3, 5, 0), r"Blender 3.5/3.5", export_fbx_files))
generator_configs.append(GeneratorConfig((3, 4, 0), r"Blender 3.4/3.4", export_fbx_files))
generator_configs.append(GeneratorConfig((3, 3, 0), r"Blender 3.3/3.3", export_fbx_files))
generator_configs.append(GeneratorConfig((3, 2, 0), r"Blender 3.2/3.2", export_fbx_files))
generator_configs.append(GeneratorConfig((3, 1, 0), r"Blender 3.1/3.1", export_fbx_files))
generator_configs.append(GeneratorConfig((2, 93, 0), r"Blender 2.93/2.93", export_fbx_files))
generator_configs.append(GeneratorConfig((2, 83, 0), r"Blender 2.83/2.83", export_fbx_files))
