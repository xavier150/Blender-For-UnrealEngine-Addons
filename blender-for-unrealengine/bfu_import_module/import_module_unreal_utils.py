# ====================== BEGIN GPL LICENSE BLOCK ============================
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program. If not, see <http://www.gnu.org/licenses/>.
#  All rights reserved.
#
# ======================= END GPL LICENSE BLOCK =============================

import string
from . import import_module_unreal_utils

try:
    import unreal
except ImportError:
    import unreal_engine as unreal

def load_asset(name):
    find_asset = unreal.find_asset(name, follow_redirectors=True)
    if find_asset is None:
        # Load asset if not find.
        find_asset = unreal.load_asset(name, follow_redirectors=True)
    return find_asset
     

def get_selected_level_actors() -> list[unreal.Actor]:
    """Returns a list of selected actors in the level."""
    return unreal.EditorLevelLibrary.get_selected_level_actors()

def get_unreal_version() -> tuple[int, int, int]:
    """Returns the Unreal Engine version as a tuple of (major, minor, patch)."""
    version_info = unreal.SystemLibrary.get_engine_version().split('-')[0]
    major, minor, patch = map(int, version_info.split('.'))
    return major, minor, patch

def is_unreal_version_greater_or_equal(target_major: int, target_minor: int = 0, target_patch: int = 0) -> bool:
    """Checks if the Unreal Engine version is greater than or equal to the target version."""
    major, minor, patch = get_unreal_version()
    return (
        major > target_major or 
        (major == target_major and minor > target_minor) or 
        (major == target_major and minor == target_minor and patch >= target_patch)
    )


def valid_unreal_asset_name(filename):
    """Returns a valid Unreal asset name by replacing invalid characters."""

    filename = filename.replace('.', '_')
    filename = filename.replace('(', '_')
    filename = filename.replace(')', '_')
    filename = filename.replace(' ', '_')
    valid_chars = "-_%s%s" % (string.ascii_letters, string.digits)
    filename = ''.join(c for c in filename if c in valid_chars)
    return filename

def show_simple_message(title: str, message: str) -> unreal.AppReturnType:
    """Displays a simple message dialog in Unreal Editor."""
    return unreal.EditorDialog.show_message(title, message, unreal.AppMsgType.OK)

def show_warning_message(title: str, message: str) -> unreal.AppReturnType:
    """Displays a warning message in Unreal Editor and prints it to the console."""
    print('--------------------------------------------------')
    print(message)
    return unreal.EditorDialog.show_message(title, message, unreal.AppMsgType.OK)

