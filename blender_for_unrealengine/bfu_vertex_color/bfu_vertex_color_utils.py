# SPDX-FileCopyrightText: Xavier Loux (BleuRaven)
#
# SPDX-License-Identifier: GPL-3.0-or-later

# ----------------------------------------------
#  Blender For UnrealEngine
#  https://github.com/xavier150/Blender-For-UnrealEngine-Addons
# ----------------------------------------------


import bpy
from typing import Dict, Any, Optional, Tuple
from . import bfu_vertex_color_utils
from .. import bbpl
from .. import bfu_utils
from .. import bfu_assets_manager
from .. bfu_assets_manager.bfu_asset_manager_type import AssetType
from . import bfu_vertex_color_props
from .bfu_vertex_color_props import BFU_VertexColorImportOptionEnum

previous_target_index_name: str = "BFU_PreviousTargetIndex"

class VertexColorExportData:
    def __init__(self, obj: bpy.types.Object, parent: Optional[bpy.types.Object] = None):
        self.obj = obj
        self.parent = parent
        self.export_type = "IGNORE"
        self.name = ""
        self.color: Tuple[float, float, float] = (1.0, 1.0, 1.0) # R, G, B
        self.index = -1

        owner = self.get_property_owner()
        if owner:
            if bfu_vertex_color_props.get_object_vertex_color_import_option(owner).value == BFU_VertexColorImportOptionEnum.IGNORE.value:
                self.export_type = "IGNORE"

            elif bfu_vertex_color_props.get_object_vertex_color_import_option(owner).value == BFU_VertexColorImportOptionEnum.OVERRIDE.value:
                self.color = bfu_vertex_color_props.get_object_vertex_color_override_color(owner)
                self.export_type = "OVERRIDE"

            elif bfu_vertex_color_props.get_object_vertex_color_import_option(owner).value == BFU_VertexColorImportOptionEnum.REPLACE.value:
                index = self.getC_chosen_vertex_index()
                if index != -1:
                    self.index = index
                    self.name = self.get_chosen_vertex_name()
                    self.export_type = "REPLACE"
            else:
                print("export type", self.export_type, "not found!")


    def get_property_owner(self):
        # Return the object to use for the property or return self if none
        if self.parent:
            return self.parent
        return self.obj

    def getC_chosen_vertex_index(self) -> int:
        obj = self.obj

        if obj.type != "MESH":
            if obj.type == "ARMATURE":
                return 0
            else:
                return -1

        owner = self.get_property_owner()
        if owner:
            bfu_vertex_color_to_use = bfu_vertex_color_props.get_object_vertex_color_to_use(owner).value
            bfu_vertex_color_index_to_use = bfu_vertex_color_props.get_object_vertex_color_index_to_use(owner)
            if obj:
                if obj.data:
                    vertex_colors = bbpl.utils.get_vertex_colors(obj)
                    if len(vertex_colors) > 0:

                        if bfu_vertex_color_to_use == "FirstIndex":
                            return 0

                        if bfu_vertex_color_to_use == "LastIndex":
                            return len(vertex_colors)-1

                        if bfu_vertex_color_to_use == "ActiveIndex":
                            target_index = bbpl.utils.get_vertex_colors_render_color_index(obj)
                            if target_index:
                                return target_index

                        if bfu_vertex_color_to_use == "CustomIndex":
                            if bfu_vertex_color_index_to_use < len(vertex_colors):
                                return bfu_vertex_color_index_to_use
        return -1

    def get_chosen_vertex_name(self)-> str:

        index = self.getC_chosen_vertex_index()
        if index == -1:
            return "None"

        obj = self.obj
        if obj:
            if obj.type == "MESH":
                if obj.data:
                    vertex_colors = bbpl.utils.get_vertex_colors(obj)
                    if bfu_vertex_color_props.get_object_vertex_color_index_to_use(obj) < len(vertex_colors):
                        return vertex_colors[index].name

        return "None"



# Vertex Color
def SetVertexColorForUnrealExport(parent: bpy.types.Object):

    objs = bfu_utils.get_export_desired_childs(parent)
    objs.append(parent)

    for obj in objs:
        if isinstance(obj.data, bpy.types.Mesh):
            vced = bfu_vertex_color_utils.VertexColorExportData(obj, parent)
            if vced.export_type == "REPLACE":

                if bpy.app.version >= (3, 2, 0):
                    vertex_colors = obj.data.color_attributes # type: ignore
                    # Save the previous target
                    obj.data[previous_target_index_name] = bfu_vertex_color_props.get_object_vertex_color_to_use(obj).value

                    # Set the vertex color for export
                    vertex_colors.active_index = vced.index
                else:
                    vertex_colors = obj.data.vertex_colors # type: ignore

                    # Save the previous target
                    obj.data[previous_target_index_name] = bfu_vertex_color_props.get_object_vertex_color_to_use(obj).value

                    # Set the vertex color for export
                    vertex_colors.active_index = vced.index


def clear_vertex_color_for_unreal_export(parent: bpy.types.Object):

    objs = bfu_utils.get_export_desired_childs(parent)
    objs.append(parent)
    for obj in objs:
        if isinstance(obj.data, bpy.types.Mesh):
            if previous_target_index_name in obj.data:
                del obj.data[previous_target_index_name]

def get_export_colors_type(obj: bpy.types.Object) -> str:
    if bfu_vertex_color_props.get_object_vertex_color_import_option(obj).value in [BFU_VertexColorImportOptionEnum.REPLACE.value, BFU_VertexColorImportOptionEnum.OVERRIDE.value]:
        return bfu_vertex_color_props.get_object_vertex_color_type(obj)
    return "NONE"

def get_vertex_color_asset_data(obj: bpy.types.Object, asset_type: AssetType) -> Dict[str, Any]:
    asset_data: Dict[str, Any] = {}
    return asset_data

def get_vertex_color_additional_data(obj: bpy.types.Object, asset_type: AssetType) -> Dict[str, Any]:
    asset_data: Dict[str, Any] = {}
    if obj:
        asset_class = bfu_assets_manager.bfu_asset_manager_utils.get_primary_supported_asset_class(obj)
        if asset_class:
            if asset_class.get_asset_type(obj) in [AssetType.STATIC_MESH, AssetType.SKELETAL_MESH]:
                vced = VertexColorExportData(obj)
                asset_data["vertex_color_import_option"] = vced.export_type
                vertex_override_color = (
                    vced.color[0],  # R
                    vced.color[1],  # G
                    vced.color[2]  # B
                )  # Color to Json
                asset_data["vertex_override_color"] = vertex_override_color

    return asset_data