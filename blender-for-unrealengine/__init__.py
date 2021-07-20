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

'''
This addons allows to easily export several objects, animation, cameras, [...] at the same time for use in game engines
like Unreal Engine of Unity by removing the usual constraints while respecting engine naming conventions
and a clean tree structure.
It also contains a small toolkit for collisions and sockets.

Asset = Object to export in game engine.
Sub object are object in assets like collision or sockets.

Addon for Blender by Xavier Loux (BleuRaven)
xavierloux.com
xavierloux.loux@gmail.com
'''

import os
import bpy
import fnmatch
import time
import addon_utils

from . import bfu_addon_pref
from . import bfu_ui
from .export import bfu_export_asset
from . import bfu_write_text
from . import bfu_basics
from . import bfu_utils

if "bpy" in locals():
    import importlib
    if "bfu_addon_pref" in locals():
        importlib.reload(bfu_addon_pref)
    if "bfu_ui" in locals():
        importlib.reload(bfu_ui)
    if "bfu_export_asset" in locals():
        importlib.reload(bfu_export_asset)
    if "bfu_write_text" in locals():
        importlib.reload(bfu_write_text)
    if "bfu_basics" in locals():
        importlib.reload(bfu_basics)
    if "bfu_utils" in locals():
        importlib.reload(bfu_utils)

bl_info = {
    'name': 'Blender for UnrealEngine',
    'description': "This add-ons allows to easily export several "
    "objects at the same time for use in unreal engine 4.",
    'author': 'Loux Xavier (BleuRaven)',
    'version': (0, 2, 3),  # Rev 0.2.3
    'blender': (2, 80, 0),
    'location': 'View3D > UI > Unreal Engine 4',
    'warning': '',
    "wiki_url": "https://github.com/xavier150/Blender-For-UnrealEngine-Addons/wiki",
    'tracker_url': 'https://github.com/xavier150/Blender-For-UnrealEngine-Addons/issues',
    'support': 'COMMUNITY',
    'category': 'Import-Export'}


class BFU_OT_UnrealPotentialError(bpy.types.PropertyGroup):
    type: bpy.props.IntProperty(default=0)  # 0:Info, 1:Warning, 2:Error
    object: bpy.props.PointerProperty(type=bpy.types.Object)
    ###
    selectObjectButton: bpy.props.BoolProperty(default=True)
    selectVertexButton: bpy.props.BoolProperty(default=False)
    selectPoseBoneButton: bpy.props.BoolProperty(default=False)
    ###
    selectOption: bpy.props.StringProperty(default="None")  # 0:VertexWithZeroWeight
    itemName: bpy.props.StringProperty(default="None")
    text: bpy.props.StringProperty(default="Unknown")
    correctRef: bpy.props.StringProperty(default="None")
    correctlabel: bpy.props.StringProperty(default="Fix it !")
    correctDesc: bpy.props.StringProperty(default="Correct target error")
    docsOcticon: bpy.props.StringProperty(default="None")


class BFU_CachedAction(bpy.types.PropertyGroup):
    name: bpy.props.StringProperty()


classes = (

)


def register():
    from bpy.utils import register_class
    bpy.types.Scene.bfu_cache_obj_name = bpy.props.StringProperty()
    bpy.types.Scene.bfu_export_auto_cached = bpy.props.BoolProperty(default=False)

    bpy.utils.register_class(BFU_CachedAction)
    bpy.types.Scene.bfu_export_auto_cached_actions = bpy.props.CollectionProperty(type=BFU_CachedAction)
    bpy.types.Scene.bfu_export_auto_cached_actions_len = bpy.props.IntProperty()

    bpy.types.Scene.bfu_object_properties_expanded = bpy.props.BoolProperty()
    bpy.types.Scene.bfu_object_import_properties_expanded = bpy.props.BoolProperty()
    bpy.types.Scene.bfu_object_lod_properties_expanded = bpy.props.BoolProperty()
    bpy.types.Scene.bfu_object_collision_properties_expanded = bpy.props.BoolProperty()
    bpy.types.Scene.bfu_object_material_properties_expanded = bpy.props.BoolProperty()
    bpy.types.Scene.bfu_object_vertex_color_properties_expanded = bpy.props.BoolProperty()
    bpy.types.Scene.bfu_object_light_map_properties_expanded = bpy.props.BoolProperty()
    bpy.types.Scene.bfu_anim_properties_expanded = bpy.props.BoolProperty()
    bpy.types.Scene.bfu_anim_advanced_properties_expanded = bpy.props.BoolProperty()
    bpy.types.Scene.bfu_skeleton_properties_expanded = bpy.props.BoolProperty()
    bpy.types.Scene.bfu_collection_properties_expanded = bpy.props.BoolProperty()
    bpy.types.Scene.bfu_object_advanced_properties_expanded = bpy.props.BoolProperty()
    bpy.types.Scene.bfu_export_type_expanded = bpy.props.BoolProperty()
    bpy.types.Scene.bfu_collision_socket_expanded = bpy.props.BoolProperty()
    bpy.types.Scene.bfu_lightmap_expanded = bpy.props.BoolProperty()
    bpy.types.Scene.bfu_nomenclature_properties_expanded = bpy.props.BoolProperty()
    bpy.types.Scene.bfu_export_filter_properties_expanded = bpy.props.BoolProperty()
    bpy.types.Scene.bfu_export_process_properties_expanded = bpy.props.BoolProperty()
    bpy.types.Scene.bfu_script_tool_expanded = bpy.props.BoolProperty()

    bpy.types.Scene.bfu_active_object_tab = bpy.props.EnumProperty(
        items=(
            ('PROP', 'Object', 'Object Tab'),
            ('ANIM', 'Animations', 'Animations Tab'),
            ('SCENE', 'Scene', 'Scene anf global Tab')
            ))

    bpy.utils.register_class(BFU_OT_UnrealPotentialError)
    bpy.types.Scene.potentialErrorList = bpy.props.CollectionProperty(type=BFU_OT_UnrealPotentialError)

    for cls in classes:
        register_class(cls)

    bfu_addon_pref.register()
    bfu_ui.register()


def unregister():
    from bpy.utils import unregister_class

    del bpy.types.Scene.bfu_export_auto_cached
    del bpy.types.Scene.bfu_export_auto_cached_actions
    del bpy.types.Scene.bfu_export_auto_cached_actions_len
    bpy.utils.unregister_class(BFU_CachedAction)

    del bpy.types.Scene.bfu_object_properties_expanded
    del bpy.types.Scene.bfu_object_import_properties_expanded
    del bpy.types.Scene.bfu_anim_properties_expanded
    del bpy.types.Scene.bfu_anim_advanced_properties_expanded
    del bpy.types.Scene.bfu_collection_properties_expanded
    del bpy.types.Scene.bfu_object_advanced_properties_expanded
    del bpy.types.Scene.bfu_collision_socket_expanded
    del bpy.types.Scene.bfu_lightmap_expanded
    del bpy.types.Scene.bfu_nomenclature_properties_expanded
    del bpy.types.Scene.bfu_export_filter_properties_expanded
    del bpy.types.Scene.bfu_export_process_properties_expanded
    del bpy.types.Scene.bfu_script_tool_expanded

    del bpy.types.Scene.bfu_active_object_tab

    bpy.utils.unregister_class(BFU_OT_UnrealPotentialError)
    del bpy.types.Scene.potentialErrorList

    for cls in classes:
        unregister_class(cls)

    bfu_addon_pref.unregister()
    bfu_ui.unregister()
