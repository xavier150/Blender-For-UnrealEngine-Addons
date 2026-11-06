from pathlib import Path
from typing import List, Tuple, Dict

from . import bpl
from . import config
from .config import BlenderVersionDetails

class BlenderVersionList:
    def __init__(self):
        self.blender_versions: Dict[Tuple[int, int, int], BlenderVersionDetails] = {}

    def add_blender_version(self, version: BlenderVersionDetails) -> None:
        self.blender_versions[version.version] = version

    def add_blender_versions(self, versions: List[BlenderVersionDetails]) -> None:
        for version in versions:
            self.add_blender_version(version)

    def check_blender_path(self, bool_print_success: bool = True) -> None:
        # Check if the blender path exist
        non_existent_paths: List[Path] = []
        for details in self.blender_versions.values():
            if details.path.exists():
                if bool_print_success:
                    print(bpl.color_set.green(f"Blender {details.version} found at {details.path}"))
            else:
                non_existent_paths.append(details.path)
                print(bpl.color_set.red(f"Blender {details.version} not found at {details.path}"))
        if len(non_existent_paths) > 0:
            print("\nYou can change the default paths in 'bfu_builder/config.py' file.")
            print("Default installation paths on Windows, adjust it for Linux or MacOS.")
            print("You can also download the missing Blender version from here:")
            print(config.blender_download_page)
            print("")
