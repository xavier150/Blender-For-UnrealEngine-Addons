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

import string

try:  # TO DO: Found a better way to check that.
    import unreal
except ImportError:
    import unreal_engine as unreal

def get_unreal_version():
    version_info = unreal.SystemLibrary.get_engine_version().split('-')[0]
    version_numbers = version_info.split('.')
    major = int(version_numbers[0])
    minor = int(version_numbers[1])
    patch = int(version_numbers[2])
    return major, minor, patch

def is_unreal_version_greater_or_equal(target_major, target_minor=0, target_patch=0):
    major, minor, patch = get_unreal_version()
    
    if major > target_major or (major == target_major and minor >= target_minor) or (major == target_major and minor == target_minor and patch >= target_patch):
        return True
    else:
        return False

def ValidUnrealAssetsName(filename):
    # Normalizes string, removes non-alpha characters
    # Asset name in Unreal use

    filename = filename.replace('.', '_')
    filename = filename.replace('(', '_')
    filename = filename.replace(')', '_')
    filename = filename.replace(' ', '_')
    valid_chars = "-_%s%s" % (string.ascii_letters, string.digits)
    filename = ''.join(c for c in filename if c in valid_chars)
    return filename

def show_simple_message(title, message):
    return unreal.EditorDialog.show_message(title, message, unreal.AppMsgType.OK)

def show_warning_message(title, message):
    print('--------------------------------------------------')
    print(message)
    return unreal.EditorDialog.show_message(title, message, unreal.AppMsgType.OK)