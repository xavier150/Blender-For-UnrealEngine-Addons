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

# ----------------------------------------------
#  BBPL -> BleuRaven Blender Python Library
#  BleuRaven.fr
#  XavierLoux.com
# ----------------------------------------------

import bpy

class BBPL_UI_ExpendSection(bpy.types.PropertyGroup):

    expend: bpy.props.BoolProperty(
        name="Use",
        description="Click to expand / collapse",
        default=False
    )
    
    def getName(self):
        prop_rna = self.id_data.bl_rna.properties[self.id_properties_ensure().name]
        return prop_rna.name

    def draw(self, layout: bpy.types.UILayout):
        tria_icon = "TRIA_DOWN" if self.expend else "TRIA_RIGHT"
        description = "Click to collapse" if self.expend else "Click to expand"
        layout.row().prop(self, "expend", icon=tria_icon, icon_only=True, text=self.getName(), emboss=False, toggle=True, expand=True)
        if self.expend:
            pass

    def is_expend(self):
        return self.expend


