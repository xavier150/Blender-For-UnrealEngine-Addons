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
from . import bfu_lod_utils
from .. import bfu_basics
from .. import bfu_utils
from .. import bfu_ui
from .. import bbpl


def draw_ui_object(layout: bpy.types.UILayout, obj: bpy.types.Object):

    if obj is None:
        return
    
    scene = bpy.context.scene 
    addon_prefs = bfu_basics.GetAddonPrefs()

    if bfu_ui.bfu_ui_utils.DisplayPropertyFilter("OBJECT", "GENERAL"):            
        scene.bfu_lod_properties_expanded.draw(layout)
        if scene.bfu_lod_properties_expanded.is_expend():
            if obj.bfu_export_type == "export_recursive":
                if not bfu_utils.GetExportAsProxy(obj):
                    if addon_prefs.useGeneratedScripts:
                        # Unreal python no longer support Skeletal mesh LODS import.
                        if bfu_utils.GetAssetType(obj) in ["StaticMesh"]:
                            LodProp = layout.column()
                            LodProp.prop(obj, 'bfu_export_as_lod_mesh')

def draw_ui_scene(layout: bpy.types.UILayout):
    pass