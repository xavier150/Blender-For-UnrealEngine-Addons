# SPDX-FileCopyrightText: Xavier Loux (BleuRaven)
#
# SPDX-License-Identifier: GPL-3.0-or-later

# ----------------------------------------------
#  Blender For UnrealEngine
#  https://github.com/xavier150/Blender-For-UnrealEngine-Addons
# ----------------------------------------------


from typing import Any, Set
import bpy
from . import bfu_light_map_utils


class BFU_OT_ComputLightMap(bpy.types.Operator):
    bl_label = "Calculate surface area"
    bl_idname = "object.comput_lightmap"
    bl_description = "Click to calculate the surface of the object"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context: bpy.types.Context) -> Set[Any]:
        obj = context.object
        if obj:
            new_surface_area: float = bfu_light_map_utils.get_export_real_surface_area(obj)
            obj.bfu_computed_static_mesh_light_map_res = new_surface_area  # type: ignore
            self.report(
                {'INFO'},
                "Light map area updated to " + str(round(new_surface_area)) + ". " +
                "Compunted Light map: " + str(bfu_light_map_utils.get_compunted_light_map(obj)))
        return {'FINISHED'}

class BFU_OT_ComputAllLightMap(bpy.types.Operator):
    bl_label = "Calculate all surface area"
    bl_idname = "object.comput_all_lightmap"
    bl_description = (
        "Click to calculate the surface of the all object in the scene"
        )
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context: bpy.types.Context) -> Set[Any]:
        scene = context.scene
        if scene:
            updated = bfu_light_map_utils.update_area_light_map_list(scene)
            self.report({'INFO'}, "The light maps of " + str(updated) + " object(s) have been updated.")
            return {'FINISHED'}
        else:
            self.report({'WARNING'}, "No objects found to update.")
            return {'CANCELLED'}


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

