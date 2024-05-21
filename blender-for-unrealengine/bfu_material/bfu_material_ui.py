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
from . import bfu_material_utils
from .. import bfu_basics
from .. import bfu_utils
from .. import bfu_ui
from .. import bbpl
from .. import bfu_assets_manager



def draw_ui_object_collision(layout: bpy.types.UILayout):
    if bfu_ui.bfu_ui_utils.DisplayPropertyFilter("OBJECT", "MISC"):

        scene = bpy.context.scene
        scene.bfu_object_material_properties_expanded.draw(layout)
        if scene.bfu_object_material_properties_expanded.is_expend():

            addon_prefs = bfu_basics.GetAddonPrefs()
            obj = bpy.context.object
            if addon_prefs.useGeneratedScripts and obj is not None:
                if obj.bfu_export_type == "export_recursive":
                    if not obj.bfu_export_as_lod_mesh:
                        asset_class = bfu_assets_manager.bfu_asset_manager_utils.get_asset_class(obj)
                        if asset_class and asset_class.use_materials == True:
                            bfu_material_search_location = layout.column()
                            bbpl.blender_layout.layout_doc_button.add_doc_page_operator(bfu_material_search_location, text="About Materials", url="https://github.com/xavier150/Blender-For-UnrealEngine-Addons/wiki/Material")
                            bfu_material_search_location.prop(obj, 'bfu_material_search_location')
                            bfu_material_search_location.prop(obj, 'bfu_import_materials')
                            bfu_material_search_location.prop(obj, 'bfu_import_textures')
                            bfu_material_search_location.prop(obj, 'bfu_invert_normal_maps')
                            bfu_material_search_location.prop(obj, 'bfu_reorder_material_to_fbx_order')
                            

def draw_ui_scene_collision(layout: bpy.types.UILayout):
    pass