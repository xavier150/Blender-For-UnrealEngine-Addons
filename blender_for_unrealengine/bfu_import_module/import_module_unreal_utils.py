# SPDX-FileCopyrightText: Xavier Loux (BleuRaven)
#
# SPDX-License-Identifier: GPL-3.0-or-later

# ----------------------------------------------
#  Blender For UnrealEngine
#  https://github.com/xavier150/Blender-For-UnrealEngine-Addons
# ----------------------------------------------

import string
import re
from typing import List, Tuple, TYPE_CHECKING, Optional
import unreal

def get_package_path_from_any_string(asset_string: str) -> str:
    """
    Convert any asset reference string (including full object references with /Script/...)
    into a clean package path suitable for EditorAssetLibrary functions.
    """
    
    # Match format like /Script/Engine.SkeletalMesh'/Game/Path/Asset.Asset'
    match = re.match(r"^/Script/.+?'(/Game/.+?)'\s*$", asset_string)
    if match:
        asset_path = match.group(1)
    else:
        asset_path = asset_string

    # Handle /Game/Path/Asset.Asset -> /Game/Path/Asset
    if asset_path.count(".") == 1:
        asset_path = asset_path.split(".")[0]

    return asset_path


def load_asset(name: str) -> Optional[unreal.Object]:
    # Convert ObjectPath to PackageName
    package_name = get_package_path_from_any_string(name)
    asset_exist = unreal.EditorAssetLibrary.does_asset_exist(package_name)
    if asset_exist:
        find_asset = unreal.find_asset(name, follow_redirectors=True)
        if find_asset is None:
            # Load asset if not find.
            # Sometimes assets exist but not found because unloaded.
            find_asset = unreal.load_asset(name, follow_redirectors=True)
        return find_asset
    return None

def renamed_asset_name(asset: unreal.Object, new_name: str) -> None:
    # Rename only the asset name and keep the path.
    if TYPE_CHECKING:
        asset_path: str = "<asset_path>"
    else:
        asset_path: str = asset.get_path_name()
    path, _ = asset_path.rsplit('/', 1)
    new_path: str = path + "/" + new_name + "." + new_name
    print(f"Renaming asset {asset_path} to {new_path}")
    unreal.EditorAssetLibrary.rename_asset(asset_path, new_path)

def get_selected_level_actors() -> List[unreal.Actor]:
    """Returns a list of selected actors in the level."""
    return unreal.EditorLevelLibrary.get_selected_level_actors()

def get_unreal_version() -> Tuple[int, int, int]:
    """Returns the Unreal Engine version as a tuple of (major, minor, patch)."""
    version_info = unreal.SystemLibrary.get_engine_version().split('-')[0]
    major, minor, patch = map(int, version_info.split('.'))
    return (major, minor, patch)

def clean_filename_for_unreal(filename: str) -> str:
    """
    Returns a valid Unreal asset name by replacing invalid characters.
    Normalizes string, removes non-alpha characters
    """

    filename = filename.replace('.', '_')
    filename = filename.replace('(', '_')
    filename = filename.replace(')', '_')
    filename = filename.replace(' ', '_')
    valid_chars = "-_%s%s" % (string.ascii_letters, string.digits)
    filename = ''.join(c for c in filename if c in valid_chars)
    return filename

def show_simple_message(title: str, message: str) -> Optional[unreal.AppReturnType]:
    """Displays a simple message dialog in Unreal Editor."""
    if hasattr(unreal, 'EditorDialog'):
        return unreal.EditorDialog.show_message(unreal.Text(title), unreal.Text(message), unreal.AppMsgType.OK) # type: ignore
    else:
        print('--------------------------------------------------')
        print(message)

def show_warning_message(title: str, message: str) -> Optional[unreal.AppReturnType]:
    """Displays a warning message in Unreal Editor and prints it to the console."""
    if hasattr(unreal, 'EditorDialog'):
        unreal.EditorDialog.show_message(unreal.Text(title), unreal.Text(message), unreal.AppMsgType.OK) # type: ignore
    else:
        print('--------------------------------------------------')
        print(message)

def editor_scripting_utilities_active() -> bool:
    if get_unreal_version() >= (4,20, 0):
        if hasattr(unreal, 'EditorAssetLibrary'):
            return True
    return False

def alembic_importer_active() -> bool:
    return hasattr(unreal, 'AbcImportSettings')

def sequencer_scripting_active() -> bool:
    return hasattr(unreal.MovieSceneSequence, 'set_display_rate')
