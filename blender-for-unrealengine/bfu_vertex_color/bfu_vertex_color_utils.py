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



class VertexColorExportData:
    def __init__(self, obj, parent=None):
        self.obj = obj
        self.parent = parent
        self.export_type = "IGNORE"
        self.name = ""
        self.color = (1.0, 1.0, 1.0)
        self.index = -1

        if self.GetPropertyOwner():
            if self.GetPropertyOwner().bfu_vertex_color_import_option == "IGNORE":
                self.export_type = "IGNORE"

            elif self.GetPropertyOwner().bfu_vertex_color_import_option == "OVERRIDE":
                self.color = self.GetPropertyOwner().bfu_vertex_color_override_color
                self.export_type = "OVERRIDE"

            elif self.GetPropertyOwner().bfu_vertex_color_import_option == "REPLACE":
                index = self.GetChosenVertexIndex()
                # print(index)
                if index != -1:
                    self.index = index
                    self.name = self.GetChosenVertexName()
                    self.export_type = "REPLACE"

    def GetPropertyOwner(self):
        # Return the object to use for the property or return self if none
        if self.parent:
            return self.parent
        return self.obj

    def GetChosenVertexIndex(self):

        obj = self.obj
        if obj.type != "MESH":
            return -1

        bfu_vertex_color_to_use = self.GetPropertyOwner().bfu_vertex_color_to_use
        bfu_vertex_color_index_to_use = self.GetPropertyOwner().bfu_vertex_color_index_to_use

        if obj:
            if obj.data:
                vertex_colors = utils.get_vertex_colors(obj)
                if len(vertex_colors) > 0:

                    if bfu_vertex_color_to_use == "FirstIndex":
                        return 0

                    if bfu_vertex_color_to_use == "LastIndex":
                        return len(vertex_colors)-1

                    if bfu_vertex_color_to_use == "ActiveIndex":
                        return utils.get_vertex_colors_render_color_index(obj)

                    if bfu_vertex_color_to_use == "CustomIndex":
                        if bfu_vertex_color_index_to_use < len(vertex_colors):
                            return bfu_vertex_color_index_to_use
        return -1

    def GetChosenVertexName(self):

        index = self.GetChosenVertexIndex()
        if index == -1:
            return "None"

        obj = self.obj
        if obj:
            if obj.type == "MESH":
                if obj.data:
                    vertex_colors = utils.get_vertex_colors(obj)
                    if obj.bfu_vertex_color_index_to_use < len(vertex_colors):
                        return vertex_colors[index].name

        return "None"

    def GetVertexByIndex(self, index):
        self.obj
