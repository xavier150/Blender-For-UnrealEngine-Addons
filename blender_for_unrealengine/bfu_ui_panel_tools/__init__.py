# SPDX-FileCopyrightText: 2018-2025 Xavier Loux (BleuRaven)
#
# SPDX-License-Identifier: GPL-3.0-or-later

# ----------------------------------------------
#  Blender For UnrealEngine
#  https://github.com/xavier150/Blender-For-UnrealEngine-Addons
# ----------------------------------------------


import bpy
from .. import bfu_debug_settings
from .. import bfu_camera
from .. import bfu_spline
from .. import bfu_collision
from .. import bfu_socket
from .. import bfu_uv_map
from .. import bfu_light_map
from .. import bfu_object
from .. import bfu_presets

class BFU_PT_BlenderForUnrealTool(bpy.types.Panel):
    # Tool panel

    bl_idname = "BFU_PT_BlenderForUnrealTool"
    bl_label = "Tools"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Unreal Engine"

    def draw(self, context: bpy.types.Context):

        layout = self.layout
        if layout is None:
            return
        
        bfu_debug_settings.start_draw_record()
        events = bfu_debug_settings.root_events
        events.new_event("Draw Tools")

        # Tools sections
        events.add_sub_event("Draw Object Tools")
        bfu_object.bfu_object_ui.draw_tools_ui(layout, context)
        events.stop_last_and_start_new_event("Draw Camera Tools")
        bfu_camera.bfu_camera_ui.draw_tools_ui(layout, context)
        events.stop_last_and_start_new_event("Draw Spline Tools")
        bfu_spline.bfu_spline_ui.draw_tools_ui(layout, context)

        events.stop_last_and_start_new_event("Draw Collision Tools")
        bfu_collision.bfu_collision_ui.draw_tools_ui(layout, context)
        events.stop_last_and_start_new_event("Draw Socket Tools")
        bfu_socket.bfu_socket_ui.draw_tools_ui(layout, context)

        events.stop_last_and_start_new_event("Draw UV Map Tools")
        bfu_uv_map.bfu_uv_map_ui.draw_tools_ui(layout, context)
        events.stop_last_and_start_new_event("Draw Light Map Tools")
        bfu_light_map.bfu_light_map_ui.draw_tools_ui(layout, context)
        events.stop_last_and_start_new_event("Draw Presets Tools")
        bfu_presets.bfu_presets_ui.draw_tools_ui(layout, context)
        events.stop_last_event()

        events.stop_last_event()
        bfu_debug_settings.stop_draw_record_and_print()

''

# -------------------------------------------------------------------
#   Register & Unregister
# -------------------------------------------------------------------

classes = (
    BFU_PT_BlenderForUnrealTool,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
