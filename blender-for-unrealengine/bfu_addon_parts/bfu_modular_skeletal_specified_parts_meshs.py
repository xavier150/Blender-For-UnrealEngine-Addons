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

class BFU_UL_ModularSkeletalSpecifiedPartsMeshItem(BBPL_UI_TemplateItem):
    pass

class BFU_UL_ModularSkeletalSpecifiedPartsMeshItemDraw(BBPL_UI_TemplateItemDraw):
    pass

    
class BFU_ModularSkeletalSpecifiedPartsMeshs(BBPL_UI_TemplateList):
    template_collection: bpy.props.CollectionProperty(type=BFU_UL_ModularSkeletalSpecifiedPartsMeshItem)
    template_collection_uilist_class: bpy.props.StringProperty(default = "BFU_UL_ModularSkeletalSpecifiedPartsMeshItemDraw")


class BFU_ModularSkeletalSpecifiedPartsMeshs2(BBPL_UI_TemplateList):
    template_collection: bpy.props.CollectionProperty(type=BFU_UL_ModularSkeletalSpecifiedPartsMeshItem)
    template_collection_uilist_class: bpy.props.StringProperty(default = "BFU_UL_ModularSkeletalSpecifiedPartsMeshItemDraw")


classes = (
    BFU_UL_ModularSkeletalSpecifiedPartsMeshItem,
    BFU_UL_ModularSkeletalSpecifiedPartsMeshItemDraw,

    BFU_ModularSkeletalSpecifiedPartsMeshs,
    BFU_ModularSkeletalSpecifiedPartsMeshs2,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.Object.bfu_modular_skeletal_specified_parts_meshs_template = bpy.props.PointerProperty(type=BFU_ModularSkeletalSpecifiedPartsMeshs)
    bpy.types.Object.bfu_modular_skeletal_specified_parts_meshs_template2 = bpy.props.PointerProperty(type=BFU_ModularSkeletalSpecifiedPartsMeshs2)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)