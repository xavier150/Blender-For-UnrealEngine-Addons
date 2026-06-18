# SPDX-FileCopyrightText: Xavier Loux (BleuRaven)
#
# SPDX-License-Identifier: GPL-3.0-or-later

# ----------------------------------------------
#  BPL -> BleuRaven Python Library
#  https://github.com/xavier150/BPL
# ----------------------------------------------

from typing import List, Tuple

def get_mirror_arrays() -> Tuple[List[str], List[str]]:
    def add_mirror(source_suffixes: List[str], mirror_suffixes: List[str], source: str, mirror: str):
        source_suffixes.append(source)
        mirror_suffixes.append(mirror)
        source_suffixes.append(mirror)
        mirror_suffixes.append(source)


    source_suffixes: List[str] = []
    mirror_suffixes: List[str] = []
    
    add_mirror(source_suffixes, mirror_suffixes, "_L", "_R")
    add_mirror(source_suffixes, mirror_suffixes, "_l", "_r")
    add_mirror(source_suffixes, mirror_suffixes, ".L", ".R")
    add_mirror(source_suffixes, mirror_suffixes, ".l", ".r")
    add_mirror(source_suffixes, mirror_suffixes, "_Left", "_Right")
    add_mirror(source_suffixes, mirror_suffixes, "_left", "_right")
    add_mirror(source_suffixes, mirror_suffixes, ".Left", ".Right")
    add_mirror(source_suffixes, mirror_suffixes, ".left", ".right")
    
    return source_suffixes, mirror_suffixes


def contains_laterality_suffix(string: str) -> bool:
    source_suffixes, mirror_suffixes = get_mirror_arrays()
    return any(string.endswith(suffix) for suffix in source_suffixes + mirror_suffixes)

def remove_laterality_suffix(string: str) -> str:
    source_suffixes, mirror_suffixes = get_mirror_arrays()
    all_suffixes = source_suffixes + mirror_suffixes
    for suffix in all_suffixes:
        if string.endswith(suffix):
            return string[:-len(suffix)]
    return string

def get_laterality_suffix(string: str) -> str:
    source_suffixes, mirror_suffixes = get_mirror_arrays()
    all_suffixes = source_suffixes + mirror_suffixes
    for suffix in all_suffixes:
        if string.endswith(suffix):
            return suffix
    return ""