# ====================== BEGIN GPL LICENSE BLOCK ============================
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.	 See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.	 If not, see <http://www.gnu.org/licenses/>.
#  All rights reserved.
#
# ======================= END GPL LICENSE BLOCK =============================

# ----------------------------------------------
#  BPS -> BleuRaven Python Script
#  BleuRaven.fr
#  XavierLoux.com
# ----------------------------------------------


def get_mirror_arrays():
    def add_mirror(source_suffixes, mirror_suffixes, source, mirror):
        source_suffixes.append(source)
        mirror_suffixes.append(mirror)
        source_suffixes.append(mirror)
        mirror_suffixes.append(source)


    source_suffixes = []
    mirror_suffixes = []
    
    add_mirror(source_suffixes, mirror_suffixes, "_L", "_R")
    add_mirror(source_suffixes, mirror_suffixes, "_l", "_r")
    add_mirror(source_suffixes, mirror_suffixes, ".L", ".R")
    add_mirror(source_suffixes, mirror_suffixes, ".l", ".r")
    add_mirror(source_suffixes, mirror_suffixes, "_Left", "_Right")
    add_mirror(source_suffixes, mirror_suffixes, "_left", "_right")
    add_mirror(source_suffixes, mirror_suffixes, ".Left", ".Right")
    add_mirror(source_suffixes, mirror_suffixes, ".left", ".right")
    
    return source_suffixes, mirror_suffixes


def contain_laterality_suffix(string):
    source_suffixes, mirror_suffixes = get_mirror_arrays()
    return any(string.endswith(suffix) for suffix in source_suffixes + mirror_suffixes)
    
def remove_laterality_suffix(string):
    source_suffixes, mirror_suffixes = get_mirror_arrays()
    all_suffixes = source_suffixes + mirror_suffixes
    for suffix in all_suffixes:
        if string.endswith(suffix):
            return string[:-len(suffix)]
    return string

def get_laterality_suffix(string):
    source_suffixes, mirror_suffixes = get_mirror_arrays()
    all_suffixes = source_suffixes + mirror_suffixes
    for suffix in all_suffixes:
        if string.endswith(suffix):
            return suffix