# SPDX-FileCopyrightText: Xavier Loux (BleuRaven)
#
# SPDX-License-Identifier: GPL-3.0-or-later

# ----------------------------------------------
#  Blender For UnrealEngine
#  https://github.com/xavier150/Blender-For-UnrealEngine-Addons
# ----------------------------------------------


from typing import List

import bpy


def get_preset_values() -> List[str]:
    preset_values: List[str] = [
        'obj.bfu_fbx_export_with_custom_props',
        'obj.bfu_do_not_import_curve_with_zero'
        ]
    return preset_values

def get_object_fbx_export_with_custom_props(obj: bpy.types.Object) -> bool:
    return obj.bfu_fbx_export_with_custom_props  # type: ignore

def get_object_do_not_import_curve_with_zero(obj: bpy.types.Object) -> bool:
    return obj.bfu_do_not_import_curve_with_zero  # type: ignore

# -------------------------------------------------------------------
#   Register & Unregister
# -------------------------------------------------------------------

classes = (
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.Object.bfu_fbx_export_with_custom_props = bpy.props.BoolProperty( # type: ignore
        name=bpy.app.translations.pgettext("Export Custom Properties", "interface.export_with_custom_props_name"),
        description=bpy.app.translations.pgettext("Process export with custom properties (Can be used for Metadata).", "tooltips.export_with_custom_props_desc"),
        override={'LIBRARY_OVERRIDABLE'},
        default=False,
        )
    
    #UFbxAnimSequenceImportData::bDoNotImportCurveWithZero
    bpy.types.Object.bfu_do_not_import_curve_with_zero = bpy.props.BoolProperty( # type: ignore
        name="Do not import curves with only 0 values",
        description="When importing custom attribute or morphtarget as curve, do not import if it doesn’t have any value other than zero. This is to avoid adding extra curves to evaluate",
        override={'LIBRARY_OVERRIDABLE'},
        default=True,
        )
    

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)

    del bpy.types.Object.bfu_do_not_import_curve_with_zero # type: ignore
    del bpy.types.Object.bfu_fbx_export_with_custom_props # type: ignore
