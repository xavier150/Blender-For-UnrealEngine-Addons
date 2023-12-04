import bpy
import importlib

from . import bfu_modular_skeletal_specified_parts_meshs
from . import bfu_export_procedure
from . import bfu_object_ui_and_props
from . import bfu_tool_ui_and_props
from . import bfu_export_ui_and_props
from . import bfu_export_correct_and_improv_panel
from . import bfu_debug_ui_and_props_panel
from . import bfu_camera_data


if "bfu_modular_skeletal_specified_parts_meshs" in locals():
    importlib.reload(bfu_modular_skeletal_specified_parts_meshs)
if "bfu_export_procedure" in locals():
    importlib.reload(bfu_export_procedure)
if "bfu_object_ui_and_props" in locals():
    importlib.reload(bfu_object_ui_and_props)
if "bfu_tool_ui_and_props" in locals():
    importlib.reload(bfu_tool_ui_and_props)
if "bfu_export_ui_and_props" in locals():
    importlib.reload(bfu_export_ui_and_props)
if "bfu_export_correct_and_improv_panel" in locals():
    importlib.reload(bfu_export_correct_and_improv_panel)
if "bfu_debug_ui_and_props_panel" in locals():
    importlib.reload(bfu_debug_ui_and_props_panel)
if "bfu_camera_data" in locals():
    importlib.reload(bfu_camera_data)

classes = (
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    bfu_modular_skeletal_specified_parts_meshs.register()
    bfu_export_procedure.register()
    bfu_object_ui_and_props.register()
    bfu_tool_ui_and_props.register()
    bfu_export_ui_and_props.register()
    bfu_export_correct_and_improv_panel.register()
    bfu_debug_ui_and_props_panel.register()

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)

    bfu_modular_skeletal_specified_parts_meshs.unregister()
    bfu_export_procedure.unregister()
    bfu_object_ui_and_props.unregister()
    bfu_tool_ui_and_props.unregister()
    bfu_export_ui_and_props.unregister()
    bfu_export_correct_and_improv_panel.unregister()
    bfu_debug_ui_and_props_panel.unregister()