# SPDX-FileCopyrightText: Xavier Loux (BleuRaven)
#
# SPDX-License-Identifier: GPL-3.0-or-later

# ----------------------------------------------
#  Blender For UnrealEngine
#  https://github.com/xavier150/Blender-For-UnrealEngine-Addons
# ----------------------------------------------

import bpy
from typing import List
from . import bfu_process_time_logs_types 


def get_process_time_logs() -> List[bfu_process_time_logs_types.BFU_OT_ExportProcessTimeLog]:
    if bpy.context is None:
        return []
    scene = bpy.context.scene
    return scene.bfu_export_process_time_logs  # type: ignore[attr-defined]

def start_time_log(process_info: str) -> bfu_process_time_logs_types.SafeTimeLogHandle:
    process_task_proxy = bfu_process_time_logs_types.SafeTimeLogHandle()
    process_task_proxy.start_timer(process_info)
    return process_task_proxy

def clear_process_time_logs():
    if bpy.context is None:
        return
    scene = bpy.context.scene
    scene.bfu_export_process_current_sub_step = 0  # type: ignore[attr-defined]
    scene.bfu_export_process_faster_time = 0  # type: ignore[attr-defined]
    scene.bfu_export_process_slower_time = 0  # type: ignore[attr-defined]
    scene.bfu_export_process_time_logs.clear()  # type: ignore[attr-defined]

def get_process_time_logs_details():
    export_log = ""
    for log in get_process_time_logs():
        export_log += f"- {log.get_process_detail()} \n"

    return export_log