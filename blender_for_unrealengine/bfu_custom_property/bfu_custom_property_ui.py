# SPDX-FileCopyrightText: Xavier Loux (BleuRaven)
#
# SPDX-License-Identifier: GPL-3.0-or-later

# ----------------------------------------------
#  Blender For UnrealEngine
#  https://github.com/xavier150/Blender-For-UnrealEngine-Addons
# ----------------------------------------------

import bpy
from .. import bfu_static_mesh
from .. import bfu_skeletal_mesh
from ..bfu_skeletal_mesh.bfu_export_procedure import BFU_FileTypeEnum

def draw_ui_custom_property(layout: bpy.types.UILayout, obj: bpy.types.Object):
    if bfu_skeletal_mesh.bfu_skeletal_mesh_utils.is_skeletal_mesh(obj):
        export_type: BFU_FileTypeEnum = bfu_skeletal_mesh.bfu_export_procedure.get_obj_export_file_type(obj)
    else:
        export_type: BFU_FileTypeEnum = bfu_static_mesh.bfu_export_procedure.get_obj_export_file_type(obj)

    if export_type.value == BFU_FileTypeEnum.FBX.value:
        layout.prop(obj, "bfu_fbx_export_with_custom_props")
        custom_props_layout = layout.column()
        custom_props_layout.enabled = obj.bfu_fbx_export_with_custom_props
        custom_props_layout.prop(obj, "bfu_do_not_import_curve_with_zero")
    