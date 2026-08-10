# SPDX-FileCopyrightText: Xavier Loux (BleuRaven)
#
# SPDX-License-Identifier: GPL-3.0-or-later

# ----------------------------------------------
#  Blender For UnrealEngine
#  https://github.com/xavier150/Blender-For-UnrealEngine-Addons
# ----------------------------------------------


import bpy
from .. import bfu_utils
from .. import bfu_ui
from .. import bbpl
from .. import bfu_assets_manager
from .. import bfu_export_control
from .. import bfu_base_object


def draw_general_ui_object(layout: bpy.types.UILayout, context: bpy.types.Context, obj: bpy.types.Object):

    scene = bpy.context.scene 

    # Hide filters
    if not bfu_utils.draw_proxy_propertys(obj):
        layout.label(text="To set the object as exportable, do it in the linked source file.")
        return
    if bfu_ui.bfu_ui_utils.DisplayPropertyFilter("OBJECT", "GENERAL"):
        accordion = bbpl.blender_layout.layout_accordion.get_accordion(scene, "bfu_object_properties_expanded")
        if accordion:
            _, panel = accordion.draw(layout)
            if panel:
                AssetType = panel.row()
                AssetType.prop(obj, 'name', text="", icon='OBJECT_DATA')
                # Show asset type
                asset_class = bfu_assets_manager.bfu_asset_manager_utils.get_primary_supported_asset_class(obj)
                asset_type = bfu_assets_manager.bfu_asset_manager_utils.get_asset_type(obj)
                AssetType.label(text='('+asset_type.get_friendly_name()+')')

                export_type = panel.column()
                export_type.prop(obj, 'bfu_export_type')

                if asset_class:
                    asset_class.draw_ui_export_procedure(export_type, context, obj)

                if bfu_export_control.bfu_export_control_utils.is_export_self(obj):

                    folderNameProperty = panel.column()
                    folderNameProperty.prop(obj, 'bfu_export_folder_name', icon='FILE_FOLDER')

                    ProxyProp = panel.column()
                    if not bfu_utils.draw_proxy_propertys(obj):
                        ProxyProp.label(text="The Armature was detected as a proxy.")
                        proxy_child = bfu_utils.get_export_proxy_child(obj)
                        if proxy_child:
                            ProxyProp.label(text="Proxy child: " + proxy_child.name)
                        else:
                            ProxyProp.label(text="Proxy child not found")

                    if bfu_utils.draw_proxy_propertys(obj):
                        # exportCustomName
                        exportCustomName = panel.row()
                        exportCustomName.prop(obj, "bfu_use_custom_export_name")
                        use_custom_name = bfu_base_object.bfu_base_obj_props.get_object_use_custom_export_name(obj)
                        exportCustomNameText = exportCustomName.column()
                        exportCustomNameText.prop(obj, "bfu_custom_export_name")
                        exportCustomNameText.enabled = use_custom_name
