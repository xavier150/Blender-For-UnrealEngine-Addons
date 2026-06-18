# SPDX-FileCopyrightText: Xavier Loux (BleuRaven)
#
# SPDX-License-Identifier: GPL-3.0-or-later

# ----------------------------------------------
#  BBAM -> BleuRaven Blender Addon Manager
#  https://github.com/xavier150/BBAM
# ----------------------------------------------

from . import utils

def uninstall_addon_from_blender(
    pkg_id: str, 
    module: str
):
    """
    Uninstalls an addon from Blender, using the correct method based on Blender's version.

    Parameters:
        bpy (module): Blender's Python API module.
        pkg_id (str): Package ID for the extension (used in newer Blender versions).
        module (str): Name of the addon module to uninstall.
    """
    # For Blender version 4.2.0 and above, use `package_uninstall`
    import bpy
    if bpy.app.version >= (4, 2, 0):
        print(f"Uninstalling extension '{pkg_id}'...")
        bpy.ops.extensions.package_uninstall(repo_index=1, pkg_id=pkg_id)  # type: ignore
        bpy.ops.preferences.addon_remove(module=module)
    else:
        # For earlier versions, directly remove the addon using `addon_remove`
        print(f"Uninstalling add-on '{module}'...")
        try:
            # may produce error in blender 2.8x
            bpy.ops.preferences.addon_disable(module=module)
        except Exception as e:
            utils.print_red("An error occurred during disabling:", str(e))

def install_zip_addon_from_blender(
    zip_file: str, 
    module: str
):
    """
    Installs a ZIP addon file in Blender, using the correct method based on Blender's version.

    Parameters:
        bpy (module): Blender's Python API module.
        zip_file (str): Path to the ZIP file containing the addon.
        module (str): Name of the addon module to enable after installation.
    """
    import bpy
    if bpy.app.version >= (4, 2, 0):
        # For Blender version 4.2.0 and above, install as an extension
        print("Installing as extension...", zip_file)
        try:
            bpy.ops.extensions.package_install_files(repo="user_default", filepath=zip_file, enable_on_install=True)  # type: ignore
            print("Extension installation complete.")
        except Exception as e:
            utils.print_red("An error occurred during installation:", str(e))
    else:
        # For earlier versions, install and enable as an addon
        print("Installing as add-on...", zip_file)
        try:
            bpy.ops.preferences.addon_install(overwrite=True, filepath=zip_file)  # type: ignore
            bpy.ops.preferences.addon_enable(module=module)  # type: ignore
            print("Add-on installation complete.")
        except Exception as e:
            utils.print_red("An error occurred during installation:", str(e))