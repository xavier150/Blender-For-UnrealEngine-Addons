# ====================== BEGIN GPL LICENSE BLOCK ============================
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <http://www.gnu.org/licenses/>.
#  All rights reserved.
#
# ======================= END GPL LICENSE BLOCK =============================


import bpy
from bpy.app.handlers import persistent

def update_variable(data, old_vars, new_var, callback=None):
    for old_var in old_vars:
        if old_var in data:
            if callback:
                data[new_var] = callback(data[old_var])
            else:
                data[new_var] = data[old_var]
            del data[old_var]
            print(f'"{old_var}" updated to "{new_var}" in {data.name}')

def update_old_variables():
    print("Updating old bfu variables...")

    for obj in bpy.data.objects:
        update_variable(obj, ["ExportEnum"], "bfu_export_type", export_enum_callback)
        update_variable(obj, ["exportFolderName"], "bfu_export_folder_name")

    for col in bpy.data.collections:
        update_variable(col, ["exportFolderName"], "bfu_export_folder_name")



def export_enum_callback(value):
    mapping = {
        1: "auto",
        2: "export_recursive",
        3: "dont_export"
    }
    return mapping.get(value, "")


@persistent
def bfu_load_handler(dummy):
    update_old_variables()

def deferred_execution():
    update_old_variables()
    return None  # Important pour que le timer ne se répète pas

classes = (
)



def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.app.handlers.load_post.append(bfu_load_handler)
    
    bpy.app.timers.register(deferred_execution, first_interval=0.1)

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
    bpy.app.handlers.load_post.remove(bfu_load_handler)