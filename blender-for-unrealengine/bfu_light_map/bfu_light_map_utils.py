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
import fnmatch
from .. import bps
from .. import bbpl
from .. import bfu_basics
from .. import bfu_utils
from .. import bfu_unreal_utils
from .. import bfu_export_logs
from .. import bfu_assets_manager
from .. import bfu_static_mesh


def GetExportRealSurfaceArea(obj):

    local_view_areas = bbpl.scene_utils.move_to_global_view()
    bbpl.utils.safe_mode_set('OBJECT')

    SavedSelect = bbpl.utils.UserSelectSave()
    SavedSelect.save_current_select()
    bfu_utils.SelectParentAndDesiredChilds(obj)

    bpy.ops.object.duplicate()
    bpy.ops.object.duplicates_make_real(
        use_base_parent=True,
        use_hierarchy=True
        )

    bfu_utils.ApplyNeededModifierToSelect()
    bpy.ops.object.parent_clear(type='CLEAR_KEEP_TRANSFORM')
    for selectObj in bpy.context.selected_objects:
        # Remove unable to convert mesh
        if selectObj.type == "EMPTY" or selectObj.type == "CURVE":
            bfu_utils.CleanDeleteObjects([selectObj])

    for selectObj in bpy.context.selected_objects:
        # Remove collision box
        if bfu_utils.CheckIsCollision(selectObj):
            bfu_utils.CleanDeleteObjects([selectObj])

    if bpy.context.view_layer.objects.active is None:
        # When the active id a empty
        bpy.context.view_layer.objects.active = bpy.context.selected_objects[0]
    bpy.ops.object.convert(target='MESH')

    active = bpy.context.view_layer.objects.active

    bfu_utils.CleanJoinSelect()
    active = bpy.context.view_layer.objects.active
    area = bfu_basics.GetSurfaceArea(active)
    bfu_utils.CleanDeleteObjects(bpy.context.selected_objects)
    SavedSelect.reset_select_by_ref()
    bbpl.scene_utils.move_to_local_view(local_view_areas)
    return area

def GetCompuntedLightMap(obj):
    if obj.bfu_static_mesh_light_map_mode == "Default":
        return -1

    if obj.bfu_static_mesh_light_map_mode == "CustomMap":
        return obj.bfu_static_mesh_custom_light_map_res

    if obj.bfu_static_mesh_light_map_mode == "SurfaceArea":
        # Get the area
        area = obj.computedStaticMeshLightMapRes
        area **= 0.5  # Adapte for light map

        if obj.bfu_use_static_mesh_light_map_world_scale:
            # Turn area at world scale
            x = max(obj.scale.x, obj.scale.x*-1)
            y = max(obj.scale.y, obj.scale.y*-1)
            z = max(obj.scale.z, obj.scale.z*-1)
            objScale = (x + y + z)/3
            area *= objScale

        # Computed light map equal light map scale for a plane vvv
        area *= bfu_utils.get_scene_unit_scale()
        area *= obj.bfu_static_mesh_light_map_surface_scale/2
        if obj.bfu_static_mesh_light_map_round_power_of_two:

            return bps.math.nearest_power_of_two(int(round(area)))
        return int(round(area))

def UpdateAreaLightMapList(objects_to_update=None):
    # Updates area LightMap

    if objects_to_update is not None:
        objs = objects_to_update
    else:
        objs = []
        export_recu_objs = bfu_utils.GetAllobjectsByExportType("export_recursive")
        for export_recu_obj in export_recu_objs:

            if bfu_static_mesh.bfu_static_mesh_utils.is_static_mesh(export_recu_obj):
                objs.append(export_recu_obj)

    UpdatedRes = 0

    counter = bps.utils.CounterTimer()
    for obj in objs:
        obj.computedStaticMeshLightMapRes = GetExportRealSurfaceArea(obj)
        UpdatedRes += 1
        bfu_utils.UpdateProgress("Update LightMap",(UpdatedRes/len(objs)),counter.get_time())
    return UpdatedRes