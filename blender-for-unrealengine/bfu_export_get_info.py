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
import time
import math

if "bpy" in locals():
    import importlib
    if "bfu_write_text" in locals():
        importlib.reload(bfu_write_text)
    if "bfu_basics" in locals():
        importlib.reload(bfu_basics)
    if "bfu_utils" in locals():
        importlib.reload(bfu_utils)

from . import bfu_write_text
from . import bfu_basics
from .bfu_basics import *
from . import bfu_utils
from .bfu_utils import *
from enum import Enum

class VertexColorExportData:
    def __init__(self, obj):
        self.obj = obj
        self.export_type = "IGNORE"
        self.name = ""
        self.color = (1.0, 1.0, 1.0)
        self.index = -1
        if self.obj:
            if obj.VertexColorImportOption == "IGNORE":
                self.export_type = "IGNORE"

            if obj.VertexColorImportOption == "OVERRIDE":
                self.color = obj.VertexOverrideColor
                self.export_type = "OVERRIDE"

            if obj.VertexColorImportOption == "REPLACE":
                index = self.GetChosenVertexIndex()
                if index != -1:
                    self.index = index
                    self.name = self.GetChosenVertexName()
                    self.export_type = "REPLACE"
                
    def GetChosenVertexIndex(self):
        obj = self.obj
        if obj:
            if obj.data:
                if len(obj.data.vertex_colors) > 0:
                    if obj.VertexColorToUse == "FirstIndex":
                        return 1
                    
                    if obj.VertexColorToUse == "LastIndex":
                        return -1
                    
                    if obj.VertexColorToUse == "ActiveIndex":
                        for index, vertex_color in enumerate(obj.data.vertex_colors):
                            if vertex_color.active_render == True:
                                return index
                    
                    if obj.VertexColorToUse == "CustomIndex":
                        if obj.VertexColorIndexToUse < len(obj.data.vertex_colors):
                            return obj.VertexColorIndexToUse
        return -1

    def GetChosenVertexName(self):
        index = self.GetChosenVertexIndex()
        if index == -1:
            return "None"
        
        obj = self.obj
        if obj: 
            if obj.data:
                if obj.VertexColorIndexToUse < len(obj.data.vertex_colors):
                    return obj.data.vertex_colors[index].name

        return "None"

    def GetVertexByIndex(self, index):
        self.obj
        
