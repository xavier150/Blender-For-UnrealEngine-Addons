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
from . import bfu_vertex_color_utils
from .. import bfu_basics
from .. import bfu_utils
from .. import bfu_ui
from .. import bbpl



def draw_ui_object_collision(layout: bpy.types.UILayout):
    if bfu_ui.bfu_ui_utils.DisplayPropertyFilter("OBJECT", "MISC"):

        scene = bpy.context.scene
        scene.bfu_object_vertex_color_properties_expanded.draw(layout)
        if scene.bfu_object_vertex_color_properties_expanded.is_expend():

            addon_prefs = bfu_basics.GetAddonPrefs()
            obj = bpy.context.object
            if addon_prefs.useGeneratedScripts and obj is not None:
                if obj.bfu_export_type == "export_recursive":
                    if not obj.bfu_export_as_lod_mesh:

                        # Vertex color
                        StaticMeshVertexColorImportOption = layout.column()
                        StaticMeshVertexColorImportOption.prop(obj, 'bfu_vertex_color_import_option')
                        if obj.bfu_vertex_color_import_option == "OVERRIDE":
                            StaticMeshVertexColorImportOptionColor = StaticMeshVertexColorImportOption.row()
                            StaticMeshVertexColorImportOptionColor.prop(obj, 'bfu_vertex_color_override_color')
                        if obj.bfu_vertex_color_import_option == "REPLACE":
                            StaticMeshVertexColorImportOptionIndex = StaticMeshVertexColorImportOption.row()
                            StaticMeshVertexColorImportOptionIndex.prop(obj, 'bfu_vertex_color_to_use')
                            if obj.bfu_vertex_color_to_use == "CustomIndex":
                                StaticMeshVertexColorImportOptionIndexCustom = StaticMeshVertexColorImportOption.row()
                                StaticMeshVertexColorImportOptionIndexCustom.prop(obj, 'bfu_vertex_color_index_to_use')

                            StaticMeshVertexColorFeedback = StaticMeshVertexColorImportOption.row()
                            if obj.type == "MESH":
                                vced = bfu_vertex_color_utils.VertexColorExportData(obj)
                                if vced.export_type == "REPLACE":
                                    my_text = 'Vertex color nammed "' + vced.name + '" will be used.'
                                    StaticMeshVertexColorFeedback.label(text=my_text, icon='INFO')
                                else:
                                    my_text = 'No vertex color found at this index.'
                                    StaticMeshVertexColorFeedback.label(text=my_text, icon='ERROR')
                            else:
                                my_text = 'Vertex color property will be apply on the childrens.'
                                StaticMeshVertexColorFeedback.label(text=my_text, icon='INFO')
                            

def draw_ui_scene_collision(layout: bpy.types.UILayout):
    pass