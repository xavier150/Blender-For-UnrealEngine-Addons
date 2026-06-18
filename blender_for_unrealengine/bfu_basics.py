# SPDX-FileCopyrightText: Xavier Loux (BleuRaven)
#
# SPDX-License-Identifier: GPL-3.0-or-later

# ----------------------------------------------
#  Blender For UnrealEngine
#  https://github.com/xavier150/Blender-For-UnrealEngine-Addons
# ----------------------------------------------

import string
from pathlib import Path
import bpy
import shutil
import bmesh

def RemoveFolderTree(folder: str) -> None:
    dirpath = Path(folder)
    if dirpath.exists() and dirpath.is_dir():
        shutil.rmtree(dirpath, ignore_errors=True)

def get_root_bone_parent(bone: bpy.types.Bone) -> bpy.types.Bone:
    if bone.parent is not None:  # type: ignore
        return get_root_bone_parent(bone.parent)
    return bone

def get_first_deform_bone_parent(bone: bpy.types.Bone) -> bpy.types.Bone:
    if bone.parent is not None:  # type: ignore
        if bone.use_deform is True:
            return bone
        else:
            return get_first_deform_bone_parent(bone.parent)
    return bone

def SetCollectionUse(collection: bpy.types.Collection) -> None:
    # Set if collection is hide and selectable
    collection.hide_viewport = False
    collection.hide_select = False
    if bpy.context.view_layer:
        layer_collection = bpy.context.view_layer.layer_collection
        if collection.name in layer_collection.children:
            layer_collection.children[collection.name].hide_viewport = False
        else:
            print(collection.name, " not found in view_layer.layer_collection")


def verifi_dirs(directory: Path) -> bool:
    # Check and create a folder if it does not exist
    if not directory.exists():
        directory.mkdir()
        return True
    return False


def valid_folder_name(directory: str) -> str:
    # https://gist.github.com/seanh/93666
    # Normalizes string, removes non-alpha characters
    # File name use

    illegal_chars = r':*?"<>|'
    directory = ''.join(c for c in directory if c not in illegal_chars)

    return directory


def valid_file_name(filename: str) -> str:
    # https://gist.github.com/seanh/93666
    # Normalizes string, removes non-alpha characters
    # File name use

    illegal_chars = r'\/:*?"<>|'
    valid_chars = "-_.() %s%s" % (string.ascii_letters, string.digits)

    filename = ''.join(c for c in filename if c not in illegal_chars)
    filename = ''.join(c for c in filename if c in valid_chars)

    return filename

def get_surface_area(obj: bpy.types.Object) -> float:
    if isinstance(obj.data, bpy.types.Mesh):
        bm = bmesh.new()
        bm.from_mesh(obj.data)
        area = sum(f.calc_area() for f in bm.faces)
        bm.free()
        return area
    return -1.0