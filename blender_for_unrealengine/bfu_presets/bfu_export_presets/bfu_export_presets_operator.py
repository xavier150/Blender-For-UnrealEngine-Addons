# SPDX-FileCopyrightText: Xavier Loux (BleuRaven)
#
# SPDX-License-Identifier: GPL-3.0-or-later

# ----------------------------------------------
#  Blender For UnrealEngine
#  https://github.com/xavier150/Blender-For-UnrealEngine-Addons
# ----------------------------------------------

from typing import List

import bpy
from bl_operators.presets import AddPresetBase

from ... import bfu_export_nomenclature
from ... import bfu_export_filter
from ... import bfu_export_process


def get_export_global_preset_propertys() -> List[str]:
    preset_values: List[str] = []
    preset_values += bfu_export_nomenclature.bfu_export_nomenclature_props.get_preset_values()
    preset_values += bfu_export_filter.bfu_export_filter_props.get_preset_values()
    preset_values += bfu_export_process.bfu_export_process_props.get_preset_values()
    return preset_values

export_preset_subdir = 'blender-for-unrealengine/nomenclature-presets'

class BFU_MT_NomenclaturePresets(bpy.types.Menu):
    bl_label = 'Nomenclature Presets'
    preset_subdir = export_preset_subdir
    preset_operator = 'script.execute_preset'
    draw = bpy.types.Menu.draw_preset  # type: ignore


class BFU_OT_AddNomenclaturePreset(AddPresetBase, bpy.types.Operator):  # type: ignore[override]
    bl_idname = 'object.add_nomenclature_preset'
    bl_label = 'Add or remove a preset for Nomenclature'
    bl_description = 'Add or remove a preset for Nomenclature'
    preset_menu = 'BFU_MT_NomenclaturePresets'


    # Common variable used for all preset values
    preset_defines = [
                        'obj = bpy.context.object',
                        'col = bpy.context.collection',
                        'scene = bpy.context.scene'
                        ]

    # Properties to store in the preset
    preset_values = get_export_global_preset_propertys()

    # Directory to store the presets
    preset_subdir = export_preset_subdir



# -------------------------------------------------------------------
#   Register & Unregister
# -------------------------------------------------------------------

classes = (
    BFU_MT_NomenclaturePresets,
    BFU_OT_AddNomenclaturePreset,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)

