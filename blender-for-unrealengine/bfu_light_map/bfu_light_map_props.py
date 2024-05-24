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


import bpy
from . import bfu_light_map_utils
from .. import bfu_basics
from .. import bfu_utils
from .. import bfu_ui
from .. import bbpl




class BFU_OT_ComputLightMap(bpy.types.Operator):
    bl_label = "Calculate surface area"
    bl_idname = "object.computlightmap"
    bl_description = "Click to calculate the surface of the object"

    def execute(self, context):
        obj = context.object
        obj.computedStaticMeshLightMapRes = bfu_utils.GetExportRealSurfaceArea(obj)
        self.report(
            {'INFO'},
            "Light map area updated to " + str(round(obj.computedStaticMeshLightMapRes)) + ". " +
            "Compunted Light map: " + str(bfu_light_map_utils.GetCompuntedLightMap(obj)))
        return {'FINISHED'}

class BFU_OT_ComputAllLightMap(bpy.types.Operator):
    bl_label = "Calculate all surface area"
    bl_idname = "object.computalllightmap"
    bl_description = (
        "Click to calculate the surface of the all object in the scene"
        )

    def execute(self, context):
        updated = bfu_utils.UpdateAreaLightMapList()
        self.report({'INFO'}, "The light maps of " + str(updated) + " object(s) have been updated.")
        return {'FINISHED'}


# -------------------------------------------------------------------
#   Register & Unregister
# -------------------------------------------------------------------

classes = (
    BFU_OT_ComputLightMap,
    BFU_OT_ComputAllLightMap
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)




def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
