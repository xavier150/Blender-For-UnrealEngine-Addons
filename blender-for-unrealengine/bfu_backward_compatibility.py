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

def update_old_variables():

    print("update old bfu variables...")

    # bpy.types.Object.ExportEnum -> bfu_export_type
    # bpy.types.Object.exportFolderName -> bfu_export_folder_name

    # bpy.types.Collection.exportFolderName -> bfu_export_folder_name


    for obj in bpy.data.objects:
        if "ExportEnum" in obj:
            if obj["ExportEnum"] == 1:
                obj.bfu_export_type = "auto"
            elif obj["ExportEnum"] == 2:
                obj.bfu_export_type = "export_recursive"
            elif obj["ExportEnum"] == 3:
                obj.bfu_export_type = "dont_export"

            del obj["ExportEnum"]
            print('"ExportEnum" update to "bfu_export_type" in ' + obj.name)

        if "exportFolderName" in obj:
            obj.bfu_export_folder_name = obj["exportFolderName"]
            del obj["exportFolderName"]
            print('"exportFolderName" update to "bfu_export_folder_name" in ' + obj.name)

    for col in bpy.data.collections:
        if "exportFolderName" in col:
            col.bfu_export_folder_name = col["exportFolderName"]
            del col["exportFolderName"]
            print('"exportFolderName" update to "bfu_export_folder_name" in ' + col.name)

@persistent
def bfu_load_handler(dummy):
    print("Load Handler:", bpy.data.filepath)
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
    print("load handler added!")
    
    bpy.app.timers.register(deferred_execution, first_interval=0.1)

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
    bpy.app.handlers.load_post.remove(bfu_load_handler)