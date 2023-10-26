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
from .. import bbpl
from ..bbpl.blender_layout.layout_template_list.types import (
        BBPL_UI_TemplateItem,
        BBPL_UI_TemplateItemDraw,
        BBPL_UI_TemplateList,
        )


class BFU_UL_ModularSkeletalSpecifiedPartsTargetMeshItem(BBPL_UI_TemplateItem):
    mesh: bpy.props.PointerProperty(
        name="LOD4",
        description="Target objet for level of detail 04",
        override={'LIBRARY_OVERRIDABLE'},
        type=bpy.types.Object
    )

class BFU_UL_ModularSkeletalSpecifiedPartsTargetMeshItemDraw(BBPL_UI_TemplateItemDraw):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):

        prop_line = layout

        indexText = layout.row()
        indexText.alignment = 'LEFT'
        indexText.scale_x = 1
        indexText.label(text=str(index))

        prop_use = prop_line.row()
        prop_use.alignment = 'LEFT'
        prop_use.prop(item, "use", text="")

        #icon = bbpl.ui_utils.getIconByGroupTheme(item.theme)
        icon = "NONE"

        prop_data = prop_line.row()
        prop_data.alignment = 'EXPAND'
        prop_data.prop(item, "mesh", text="")
        prop_data.enabled = item.use

    
class BFU_ModularSkeletalSpecifiedPartsTargetMeshs(BBPL_UI_TemplateList):
    template_collection: bpy.props.CollectionProperty(type=BFU_UL_ModularSkeletalSpecifiedPartsTargetMeshItem)
    template_collection_uilist_class: bpy.props.StringProperty(default = "BFU_UL_ModularSkeletalSpecifiedPartsTargetMeshItemDraw")




class BFU_UL_ModularSkeletalSpecifiedPartsMeshItem(BBPL_UI_TemplateItem):
    use: bpy.props.BoolProperty(
        name="Use",
        default=True
        )

    name: bpy.props.StringProperty(
        name="Bone groups name",
        description="Your bone group",
        default="MyGroup",
        )
    
    target_meshs: bpy.props.PointerProperty(
       type=BFU_ModularSkeletalSpecifiedPartsTargetMeshs
       )

class BFU_UL_ModularSkeletalSpecifiedPartsMeshItemDraw(BBPL_UI_TemplateItemDraw):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):

        prop_line = layout

        indexText = layout.row()
        indexText.alignment = 'LEFT'
        indexText.scale_x = 1
        indexText.label(text=str(index))

        prop_use = prop_line.row()
        prop_use.alignment = 'LEFT'
        prop_use.prop(item, "use", text="")

        #icon = bbpl.ui_utils.getIconByGroupTheme(item.theme)
        icon = "NONE"

        prop_data = prop_line.row()
        prop_data.alignment = 'EXPAND'
        prop_data.prop(item, "name", text="")
        prop_data.enabled = item.use

    
class BFU_ModularSkeletalSpecifiedPartsMeshs(BBPL_UI_TemplateList):
    template_collection: bpy.props.CollectionProperty(type=BFU_UL_ModularSkeletalSpecifiedPartsMeshItem)
    template_collection_uilist_class: bpy.props.StringProperty(default = "BFU_UL_ModularSkeletalSpecifiedPartsMeshItemDraw")
    def draw(self, layout: bpy.types.UILayout):
        super().draw(layout)
        active = self.get_active_item()
        if active:
            layout.label(text="Active -> "+active.name)
            active.target_meshs.draw(layout)
        


classes = (
    BFU_UL_ModularSkeletalSpecifiedPartsTargetMeshItem,
    BFU_UL_ModularSkeletalSpecifiedPartsTargetMeshItemDraw,
    BFU_ModularSkeletalSpecifiedPartsTargetMeshs,
    BFU_UL_ModularSkeletalSpecifiedPartsMeshItem,
    BFU_UL_ModularSkeletalSpecifiedPartsMeshItemDraw,
    BFU_ModularSkeletalSpecifiedPartsMeshs,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.Object.bfu_modular_skeletal_specified_parts_meshs_template = bpy.props.PointerProperty(type=BFU_ModularSkeletalSpecifiedPartsMeshs)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)