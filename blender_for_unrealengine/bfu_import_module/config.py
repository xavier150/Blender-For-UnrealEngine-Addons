# SPDX-FileCopyrightText: Xavier Loux (BleuRaven)
#
# SPDX-License-Identifier: GPL-3.0-or-later

# ----------------------------------------------
#  Blender For UnrealEngine
#  https://github.com/xavier150/Blender-For-UnrealEngine-Addons
# ----------------------------------------------

select_assets_after_import: bool = True
save_assets_after_import: bool = True

# DEBUG
automated_import_tasks: bool = True # "True" by default. You can use "False" for debug.
# automated_import_tasks when False will show up the import task option popup.
# This will in the most of cases override the optionss set in the import script. So use that for debug is a bad idea.
print_debug_steps: bool = True # "False" by default. You can use "True" for debug.
force_use_interchange = False # "False" by default. Interchange is recommended since Unreal Engine 5.5 but it was added before