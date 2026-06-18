from typing import List, Tuple
from pathlib import Path
import platform

windows_blender_install_path: Path = Path("C:/Program Files/Blender Foundation")
linux_blender_install_path: Path = Path("/media/bleuraven/engines/BlenderBuilds/BlenderLinuxBuilds/HandDownload")

class BlenderVersionDetails:
    def __init__(self, version: Tuple[int, int, int]):
        self.version: Tuple[int, int, int] = version
        self.path:Path = Path()

        # Disable TBB malloc replacement to avoid issues with Blender 4.2+ More details: https://projects.blender.org/blender/blender/issues/126109
        self.fix_allocation_functions_replacement: bool = False


blender_version_and_path: List[BlenderVersionDetails] = []

def add_blender_version(version: Tuple[int, int, int], path: Path) -> BlenderVersionDetails:

    details = BlenderVersionDetails(version)
    details.path = path
    blender_version_and_path.append(details)
    details.fix_allocation_functions_replacement = version == (4, 2, 0)
    return details

# Detect OS and use appropriate paths
is_windows = platform.system() == "Windows"
is_linux = platform.system() == "Linux"

if is_linux:
    # Linux paths
    add_blender_version((5, 1, 2), Path(linux_blender_install_path / "blender-5.1.2-linux-x64/blender"))
    add_blender_version((5, 0, 1), Path(linux_blender_install_path / "blender-5.0.1-linux-x64/blender"))
    add_blender_version((4, 5, 1), Path(linux_blender_install_path / "blender-4.5.1-linux-x64/blender"))
    add_blender_version((4, 4, 3), Path(linux_blender_install_path / "blender-4.4.3-linux-x64/blender"))
    add_blender_version((4, 3, 2), Path(linux_blender_install_path / "blender-4.3.2-linux-x64/blender"))
    add_blender_version((4, 2, 9), Path(linux_blender_install_path / "blender-4.2.9-linux-x64/blender"))
    add_blender_version((4, 1, 1), Path(linux_blender_install_path / "blender-4.1.1-linux-x64/blender"))
    add_blender_version((4, 0, 2), Path(linux_blender_install_path / "blender-4.0.2-linux-x64/blender"))
    add_blender_version((3, 6, 9), Path(linux_blender_install_path / "blender-3.6.9-linux-x64/blender"))
    add_blender_version((3, 5, 1), Path(linux_blender_install_path / "blender-3.5.1-linux-x64/blender"))
    add_blender_version((3, 4, 1), Path(linux_blender_install_path / "blender-3.4.1-linux-x64/blender"))
    add_blender_version((3, 3, 9), Path(linux_blender_install_path / "blender-3.3.9-linux-x64/blender"))
    add_blender_version((3, 2, 2), Path(linux_blender_install_path / "blender-3.2.2-linux-x64/blender"))
    add_blender_version((3, 1, 2), Path(linux_blender_install_path / "blender-3.1.2-linux-x64/blender"))
    add_blender_version((3, 0, 1), Path(linux_blender_install_path / "blender-3.0.1-linux-x64/blender"))
    add_blender_version((2, 93, 9), Path(linux_blender_install_path / "blender-2.93.9-linux-x64/blender"))
    add_blender_version((2, 92, 0), Path(linux_blender_install_path / "blender-2.92.0-linux64/blender"))
    add_blender_version((2, 91, 2), Path(linux_blender_install_path / "blender-2.91.2-linux64/blender"))
    add_blender_version((2, 90, 1), Path(linux_blender_install_path / "blender-2.90.1-linux64/blender"))
    add_blender_version((2, 83, 9), Path(linux_blender_install_path / "blender-2.83.9-linux64/blender"))
    add_blender_version((2, 82, 0), Path(linux_blender_install_path / "blender-2.82a-linux64/blender"))
    add_blender_version((2, 81, 0), Path(linux_blender_install_path / "blender-2.81a-linux-glibc217-x86_64/blender"))
    add_blender_version((2, 80, 0), Path(linux_blender_install_path / "blender-2.80rc3-linux-glibc217-x86_64/blender"))
elif is_windows:
    # Windows paths
    add_blender_version((5, 1, 0), Path(windows_blender_install_path / "Blender 5.1/blender.exe"))
    add_blender_version((5, 0, 1), Path(windows_blender_install_path / "Blender 5.0/blender.exe"))
    add_blender_version((4, 5, 0), Path(windows_blender_install_path / "Blender 4.5/blender.exe"))
    add_blender_version((4, 4, 0), Path(windows_blender_install_path / "Blender 4.4/blender.exe"))
    add_blender_version((4, 3, 0), Path(windows_blender_install_path / "Blender 4.3/blender.exe"))
    add_blender_version((4, 2, 0), Path(windows_blender_install_path / "Blender 4.2/blender.exe"))
    add_blender_version((4, 1, 0), Path(windows_blender_install_path / "Blender 4.1/blender.exe"))
    add_blender_version((4, 0, 0), Path(windows_blender_install_path / "Blender 4.0/blender.exe"))
    add_blender_version((3, 6, 0), Path(windows_blender_install_path / "Blender 3.6/blender.exe"))
    add_blender_version((3, 5, 0), Path(windows_blender_install_path / "Blender 3.5/blender.exe"))
    add_blender_version((3, 4, 0), Path(windows_blender_install_path / "Blender 3.4/blender.exe"))
    add_blender_version((3, 3, 0), Path(windows_blender_install_path / "Blender 3.3/blender.exe"))
    add_blender_version((3, 2, 0), Path(windows_blender_install_path / "Blender 3.2/blender.exe"))
    add_blender_version((3, 1, 0), Path(windows_blender_install_path / "Blender 3.1/blender.exe"))
    add_blender_version((3, 0, 0), Path(windows_blender_install_path / "Blender 3.0/blender.exe"))
    add_blender_version((2, 93, 0), Path(windows_blender_install_path / "Blender 2.93/blender.exe"))
    add_blender_version((2, 92, 0), Path(windows_blender_install_path / "Blender 2.92/blender.exe"))
    add_blender_version((2, 91, 0), Path(windows_blender_install_path / "Blender 2.91/blender.exe"))
    add_blender_version((2, 90, 0), Path(windows_blender_install_path / "Blender 2.90/blender.exe"))
    add_blender_version((2, 83, 0), Path(windows_blender_install_path / "Blender 2.83/blender.exe"))
    add_blender_version((2, 82, 0), Path(windows_blender_install_path / "Blender 2.82/blender.exe"))
    add_blender_version((2, 81, 0), Path(windows_blender_install_path / "Blender 2.81/blender.exe"))
    add_blender_version((2, 80, 0), Path(windows_blender_install_path / "Blender 2.80/blender.exe"))

blender_download_page = "https://download.blender.org/release/"