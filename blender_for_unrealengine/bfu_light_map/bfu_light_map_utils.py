# SPDX-FileCopyrightText: Xavier Loux (BleuRaven)
#
# SPDX-License-Identifier: GPL-3.0-or-later

# ----------------------------------------------
#  Blender For UnrealEngine
#  https://github.com/xavier150/Blender-For-UnrealEngine-Addons
# ----------------------------------------------

import bpy
from typing import Dict, TYPE_CHECKING, Any, Optional, List
from .. import bpl
from .. import bbpl
from .. import bfu_basics
from .. import bfu_utils
from .. import bfu_static_mesh
from .. import bfu_export_control
from .. import bfu_export
from .. import bfu_collision
from .. bfu_assets_manager.bfu_asset_manager_type import AssetType
from . import bfu_light_map_props
from .bfu_light_map_props import BFU_StaticMeshLightMapMode



def GetExportRealSurfaceArea(obj: bpy.types.Object) -> float:

    bbpl.scene_utils.move_to_global_view()
    bbpl.utils.safe_mode_set('OBJECT')

    SavedSelect = bbpl.save_data.select_save.UserSelectSave()
    SavedSelect.save_current_select()
    bfu_utils.SelectParentAndDesiredChilds(obj)

    bpy.ops.object.duplicate()
    bpy.ops.object.duplicates_make_real(
        use_base_parent=True,
        use_hierarchy=True
        )
    
    view_layer = bpy.context.view_layer
    if view_layer is None:
        return 0.0

    bfu_export.bfu_export_utils.apply_select_needed_modifiers_for_export()
    bpy.ops.object.parent_clear(type='CLEAR_KEEP_TRANSFORM')
    for selectObj in bpy.context.selected_objects:
        # Remove unable to convert mesh
        if selectObj.type == "EMPTY" or selectObj.type == "CURVE":
            bfu_utils.clean_delete_objects([selectObj])

    for selectObj in bpy.context.selected_objects:
        # Remove collision box
        if bfu_collision.bfu_collision_utils.is_a_collision(selectObj):
            bfu_utils.clean_delete_objects([selectObj])

    if view_layer.objects.active is None:
        # When the active id a empty
        view_layer.objects.active = bpy.context.selected_objects[0]
    bpy.ops.object.convert(target='MESH')

    active = view_layer.objects.active

    bfu_utils.CleanJoinSelect()
    active = view_layer.objects.active
    area = bfu_basics.get_surface_area(active)
    bfu_utils.clean_delete_objects(bpy.context.selected_objects)
    SavedSelect.reset_select()
    bbpl.scene_utils.move_to_local_view()
    return area

def GetCompuntedLightMap(obj: bpy.types.Object) -> int:
    if bfu_light_map_props.get_object_static_mesh_light_map_mode(obj).value == BFU_StaticMeshLightMapMode.DEFAULT.value:
        return -1

    elif bfu_light_map_props.get_object_static_mesh_light_map_mode(obj).value == BFU_StaticMeshLightMapMode.CUSTOM_MAP.value:
        return bfu_light_map_props.get_object_static_mesh_custom_light_map_res(obj)

    elif bfu_light_map_props.get_object_static_mesh_light_map_mode(obj).value == BFU_StaticMeshLightMapMode.SURFACE_AREA.value:
        # Get the area
        area =  bfu_light_map_props.get_object_computed_static_mesh_light_map_res(obj)
        area **= 0.5  # Adapte for light map

        if bfu_light_map_props.get_object_use_static_mesh_light_map_world_scale(obj):
            # Turn area at world scale
            x = max(obj.scale.x, obj.scale.x*-1)
            y = max(obj.scale.y, obj.scale.y*-1)
            z = max(obj.scale.z, obj.scale.z*-1)
            objScale = (x + y + z)/3
            area *= objScale

        # Computed light map equal light map scale for a plane vvv
        area *= bfu_utils.get_scene_unit_scale()
        area *= bfu_light_map_props.get_object_static_mesh_light_map_surface_scale(obj)/2
        if bfu_light_map_props.get_object_static_mesh_light_map_round_power_of_two(obj):
            return bpl.math.nearest_power_of_two(int(round(area)))
        return int(round(area))
    
    else:
        return -1

def update_area_light_map_list(scene: bpy.types.Scene, objects_to_update: Optional[List[bpy.types.Object]] = None):
    # Updates area LightMap

    if objects_to_update is not None:
        objs = objects_to_update
    else:
        objs: List[bpy.types.Object] = []
        export_recu_objs = bfu_export_control.bfu_export_control_utils.get_all_export_recursive_objects(scene)
        for export_recu_obj in export_recu_objs:

            if bfu_static_mesh.bfu_static_mesh_utils.is_static_mesh(export_recu_obj):
                objs.append(export_recu_obj)

    UpdatedRes = 0

    counter = bpl.utils.CounterTimer()
    for obj in objs:
        bfu_light_map_props.get_object_computed_static_mesh_light_map_res(obj)
        UpdatedRes += 1
        bfu_utils.update_progress("Update LightMap",(UpdatedRes/len(objs)),counter.get_time())
    return UpdatedRes

def GetUseCustomLightMapResolution(obj: bpy.types.Object) -> bool:
    if bfu_light_map_props.get_object_static_mesh_light_map_mode(obj).value == BFU_StaticMeshLightMapMode.DEFAULT.value:
        return False
    return True

def get_light_map_asset_data(obj: bpy.types.Object, asset_type: AssetType) -> Dict[str, Any]:
    asset_data: Dict[str, Any] = {}
    return asset_data

def get_light_map_additional_data(obj: bpy.types.Object, asset_type: AssetType) -> Dict[str, Any]:
    asset_data: Dict[str, Any] = {}
    if asset_type in [AssetType.STATIC_MESH]:
        if obj:

            if TYPE_CHECKING:
                class FakeObject(bpy.types.Object):
                    bfu_generate_light_map_uvs: bool = False
                obj = FakeObject()

            asset_data["generate_light_map_uvs"] = obj.bfu_generate_light_map_uvs

            asset_data["use_custom_light_map_resolution"] = GetUseCustomLightMapResolution(obj)
            asset_data["light_map_resolution"] = GetCompuntedLightMap(obj)

    return asset_data