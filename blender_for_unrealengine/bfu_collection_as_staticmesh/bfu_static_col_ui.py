# SPDX-FileCopyrightText: Xavier Loux (BleuRaven)
#
# SPDX-License-Identifier: GPL-3.0-or-later

# ----------------------------------------------
#  Blender For UnrealEngine
#  https://github.com/xavier150/Blender-For-UnrealEngine-Addons
# ----------------------------------------------


import bpy


from . import bfu_export_procedure
from .. import bfu_ui
from .. import bfu_asset_preview
from ..bfu_assets_manager.bfu_asset_manager_type import AssetToSearch
from .. import bbpl
from . import bfu_static_col_props


def draw_ui_scene(layout: bpy.types.UILayout, context: bpy.types.Context):

    scene = bpy.context.scene
    if scene is None:
        return 

    if bfu_ui.bfu_ui_utils.DisplayPropertyFilter("SCENE", "GENERAL"):

        accordion = bbpl.blender_layout.layout_accordion.get_accordion(scene, "bfu_collection_properties_expanded")
        if accordion:
            _, panel = accordion.draw(layout)
            if panel:
                collectionListProperty = panel.column()
                collectionListProperty.template_list(
                    # type and unique id
                    "BFU_UL_StaticCollectionExportTarget", "",
                    # pointer to the CollectionProperty
                    scene, "bfu_static_collection_asset_list",
                    # pointer to the active identifier
                    scene, "bfu_active_static_collection_asset_list",
                    maxrows=5,
                    rows=5
                )
                collectionListProperty.operator(
                    "object.updatecollectionlist",
                    icon='RECOVER_LAST')

                active_index = bfu_static_col_props.get_scene_active_static_collection_asset_list(scene)
                asset_list = bfu_static_col_props.get_scene_static_collection_asset_list(scene)
                if active_index < len(asset_list):
                    col_name = asset_list[active_index].name
                    if col_name in bpy.data.collections:
                        col = bpy.data.collections[col_name]
                        col_prop = panel
                        col_prop.prop(col, 'bfu_export_folder_name', icon='FILE_FOLDER')
                        bfu_export_procedure.draw_col_export_procedure(panel, col)

                panel.label(text='Note: The collection are exported like StaticMesh.')

        bfu_asset_preview.bfu_asset_preview_ui.draw_asset_preview_bar(layout, context, asset_to_search=AssetToSearch.COLLECTION_ONLY)