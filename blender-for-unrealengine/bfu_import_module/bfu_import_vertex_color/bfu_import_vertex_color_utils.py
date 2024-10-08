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

from .. import import_module_unreal_utils
from .. import import_module_tasks_class

try:
    import unreal
except ImportError:
    import unreal_engine as unreal

def get_vertex_override_color(asset_additional_data):
    if asset_additional_data is None:
        return None

    if "vertex_override_color" in asset_additional_data:
        vertex_override_color = unreal.LinearColor(
            asset_additional_data["vertex_override_color"][0],
            asset_additional_data["vertex_override_color"][1],
            asset_additional_data["vertex_override_color"][2]
            )
        return vertex_override_color

def get_vertex_color_import_option(asset_additional_data, use_igcmp = True):
    if asset_additional_data is None:
        return None
    
    if use_igcmp:
        # Set values inside unreal.InterchangeGenericCommonMeshesProperties
        vertex_color_import_option = unreal.InterchangeVertexColorImportOption.IVCIO_REPLACE  # Default
        if "vertex_color_import_option" in asset_additional_data:
            if asset_additional_data["vertex_color_import_option"] == "IGNORE":
                vertex_color_import_option = unreal.InterchangeVertexColorImportOption.IVCIO_IGNORE
            elif asset_additional_data["vertex_color_import_option"] == "OVERRIDE":
                vertex_color_import_option = unreal.InterchangeVertexColorImportOption.IVCIO_OVERRIDE
            elif asset_additional_data["vertex_color_import_option"] == "REPLACE":
                vertex_color_import_option = unreal.InterchangeVertexColorImportOption.IVCIO_REPLACE
        return vertex_color_import_option

    else:
        # Set values inside unreal.FbxStaticMeshImportData
        vertex_color_import_option = unreal.VertexColorImportOption.REPLACE  # Default
        if "vertex_color_import_option" in asset_additional_data:
            if asset_additional_data["vertex_color_import_option"] == "IGNORE":
                vertex_color_import_option = unreal.VertexColorImportOption.IGNORE
            elif asset_additional_data["vertex_color_import_option"] == "OVERRIDE":
                vertex_color_import_option = unreal.VertexColorImportOption.OVERRIDE
            elif asset_additional_data["vertex_color_import_option"] == "REPLACE":
                vertex_color_import_option = unreal.VertexColorImportOption.REPLACE
        return vertex_color_import_option

def apply_import_settings(itask: import_module_tasks_class.ImportTaks, asset_type, asset_additional_data):
    vertex_override_color = get_vertex_override_color(asset_additional_data)
    vertex_color_import_option = get_vertex_color_import_option(asset_additional_data, itask.use_interchange)

    if itask.use_interchange:
        # Set values inside unreal.InterchangeGenericCommonMeshesProperties
        itask.GetIGAP_CommonMeshs().set_editor_property('vertex_color_import_option', vertex_color_import_option)
        itask.GetIGAP_CommonMeshs().set_editor_property('vertex_override_color', vertex_override_color.to_rgbe())
    else:
        # Set values inside unreal.FbxStaticMeshImportData

        if asset_type == "StaticMesh":
            if vertex_color_import_option:
                itask.GetStaticMeshImportData().set_editor_property('vertex_color_import_option', vertex_color_import_option)

            if vertex_override_color:
                itask.GetStaticMeshImportData().set_editor_property('vertex_override_color', vertex_override_color.to_rgbe())
        if asset_type == "SkeletalMesh":
            if vertex_color_import_option:
                itask.GetSkeletalMeshImportData().set_editor_property('vertex_color_import_option', vertex_color_import_option)

            if vertex_override_color:
                itask.GetSkeletalMeshImportData().set_editor_property('vertex_override_color', vertex_override_color.to_rgbe())



def apply_asset_settings(itask, asset, asset_additional_data):
    if asset is None:
        return

    vertex_override_color = get_vertex_override_color(asset_additional_data)
    vertex_color_import_option = get_vertex_color_import_option(asset_additional_data, itask.use_interchange)

    if itask.use_interchange:
        common_meshes_properties = asset.get_editor_property('asset_import_data').get_pipelines()[0].get_editor_property('common_meshes_properties')
        if vertex_override_color:
            common_meshes_properties.set_editor_property('vertex_override_color', vertex_override_color.to_rgbe())

        if vertex_color_import_option:
            common_meshes_properties.set_editor_property('vertex_color_import_option', vertex_color_import_option)

    else:
        asset_import_data = asset.get_editor_property('asset_import_data')
        if vertex_override_color:
            asset_import_data.set_editor_property('vertex_override_color', vertex_override_color.to_rgbe())

        if vertex_color_import_option:
            asset_import_data.set_editor_property('vertex_color_import_option', vertex_color_import_option)