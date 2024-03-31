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


def draw_ui_object_collision(layout: bpy.types.UILayout):
    if bfu_ui.bfu_ui_utils.DisplayPropertyFilter("OBJECT", "MISC"):

        scene = bpy.context.scene
        scene.bfu_object_material_properties_expanded.draw(layout)
        if scene.bfu_object_material_properties_expanded.is_expend():

            addon_prefs = bfu_basics.GetAddonPrefs()
            obj = bpy.context.object
            if addon_prefs.useGeneratedScripts and obj is not None:
                if obj.bfu_export_type == "export_recursive":

                    # bfu_material_search_location
                    if not obj.bfu_export_as_lod_mesh:
                        if (bfu_utils.GetAssetType(obj) == "StaticMesh" or
                                bfu_utils.GetAssetType(obj) == "SkeletalMesh" or
                                bfu_utils.GetAssetType(obj) == "Alembic"):
                            bfu_material_search_location = layout.row()
                            bfu_material_search_location.prop(
                                obj, 'bfu_material_search_location')
                                
def draw_ui_scene_collision(layout: bpy.types.UILayout):
    pass