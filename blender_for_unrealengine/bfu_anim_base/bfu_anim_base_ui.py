# SPDX-FileCopyrightText: Xavier Loux (BleuRaven)
#
# SPDX-License-Identifier: GPL-3.0-or-later

# ----------------------------------------------
#  Blender For UnrealEngine
#  https://github.com/xavier150/Blender-For-UnrealEngine-Addons
# ----------------------------------------------


import bpy
from .. import bfu_ui
from .. import bbpl
from .. import bfu_alembic_animation
from .. import bfu_export_control
from .. import bfu_asset_preview
from ..bfu_assets_manager.bfu_asset_manager_type import AssetToSearch

def draw_ui_object(layout: bpy.types.UILayout, context: bpy.types.Context, obj: bpy.types.Object):
    
    scene = bpy.context.scene 

    # Hide filters
    if bfu_export_control.bfu_export_control_utils.is_not_export_recursive(obj):
        return
    
    if bfu_ui.bfu_ui_utils.DisplayPropertyFilter("OBJECT", "ANIM"):
        accordion = bbpl.blender_layout.layout_accordion.get_accordion(scene, "bfu_animation_advanced_properties_expanded")
        if accordion:
            _, panel = accordion.draw(layout)
            if panel:
                # Animation fbx properties
                if bfu_alembic_animation.bfu_alembic_animation_utils.is_not_alembic_animation(obj):
                    propsFbx = panel.row()
                    propsFbx.prop(obj, 'bfu_sample_anim_for_export')
                    propsFbx.prop(obj, 'bfu_simplify_anim_for_export')

                props_scale_animation = panel.column()
                props_scale_animation.prop(obj, "bfu_disable_free_scale_animation")

                props_animation_mesh = panel.column()
                props_animation_mesh.prop(obj, "bfu_export_animation_without_mesh")

                props_animation_materials = panel.column()
                props_animation_materials.prop(obj, "bfu_export_animation_without_materials")
                props_animation_materials.enabled = not obj.bfu_export_animation_without_mesh

                props_animation_textures = panel.column()
                props_animation_textures.prop(obj, "bfu_export_animation_without_textures")
                props_animation_textures.enabled = not obj.bfu_export_animation_without_materials and not obj.bfu_export_animation_without_mesh

        layout.label(text='Note: The Action with only one frame is exported like Pose.')
        bfu_asset_preview.bfu_asset_preview_ui.draw_asset_preview_bar(layout, context, asset_to_search=AssetToSearch.ANIMATION_ONLY)