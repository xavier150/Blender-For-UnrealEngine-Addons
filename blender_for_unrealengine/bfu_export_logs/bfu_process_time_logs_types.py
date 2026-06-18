# SPDX-FileCopyrightText: Xavier Loux (BleuRaven)
#
# SPDX-License-Identifier: GPL-3.0-or-later

# ----------------------------------------------
#  Blender For UnrealEngine
#  https://github.com/xavier150/Blender-For-UnrealEngine-Addons
# ----------------------------------------------

import bpy
import time
from typing import TYPE_CHECKING, Optional
from .. import bpl


class BFU_OT_ExportProcessTimeLog(bpy.types.PropertyGroup):

    process_id: bpy.props.StringProperty()  # type: ignore
    process_info: bpy.props.StringProperty()  # type: ignore
    start_time: bpy.props.FloatProperty(default=0.0)  # type: ignore
    end_time: bpy.props.FloatProperty(default=0.0)  # type: ignore
    sub_step: bpy.props.IntProperty(default=0)  # type: ignore
    finished_success: bpy.props.BoolProperty(default=False)  # type: ignore

    if TYPE_CHECKING:
        process_id: str
        process_info: str
        start_time: float
        end_time: float
        sub_step: int
        finished_success: bool

    def start_timer(self, process_id: str, process_info: str) -> float:
        if bpy.context is None:
            return 0.0
        scene = bpy.context.scene

        self.process_id = process_id
        self.process_info = process_info
        self.sub_step = scene.bfu_export_process_current_sub_step  # type: ignore[attr-defined]
        self.start_time = time.perf_counter()

        # Increment the sub step counter
        scene.bfu_export_process_current_sub_step += 1  # type: ignore[attr-defined]
        
        return self.start_time

    def finish_timer(self) -> float:
        if bpy.context is None:
            return 0.0
        
        self.end_time = time.perf_counter()
        self.finished_success = True

        # Decrement the sub step counter
        scene = bpy.context.scene
        scene.bfu_export_process_current_sub_step -= 1  # type: ignore[attr-defined]

        elapsed_time = self.end_time - self.start_time
        if elapsed_time < scene.bfu_export_process_faster_time:
            scene.bfu_export_process_faster_time = elapsed_time
        elif elapsed_time > scene.bfu_export_process_slower_time:
            scene.bfu_export_process_slower_time = elapsed_time

        return elapsed_time


    def get_process_detail(self):
        if self.finished_success:
            result = "Success"
        else:
            result = bpl.color_set.red("Never finished")

        scene = bpy.context.scene
        elapsed = self.end_time - self.start_time
        faster: float = scene.bfu_export_process_faster_time # type: ignore[attr-defined]
        slower: float = scene.bfu_export_process_slower_time # type: ignore[attr-defined]

        # Colorize 20% faster times in green, 20% slower in red and other in yellow
        faster_max: float = ((slower - faster) * 0.2) + faster # 20% faster
        slower_min: float = slower - ((slower - faster) * 0.2)  # 20% slower
        
        if elapsed <= faster_max:
            str_time = bpl.color_set.green(bpl.utils.get_formatted_time(elapsed))
        elif elapsed >= slower_min:
            str_time = bpl.color_set.red(bpl.utils.get_formatted_time(elapsed))
        else:
            str_time = bpl.color_set.yellow(bpl.utils.get_formatted_time(elapsed))

        str_sub_steps = self.sub_step * "   |"
        return f"{str_sub_steps}{self.process_info}, {str_time}, {result}"

class SafeTimeLogHandle():
    # I need to store a proxy class
    # because BFU_OT_ExportProcessTimeLog ref is lost
    # when scene update and this produce a crash.

    def __init__(self):
        self.process_id: str = self.get_process_time_unique_id()
        self.should_print_log: bool = False
        

    def start_timer(self, timer_name: str) -> float:
        if bpy.context is None:
            return 0.0
        self.print_log(self.get_process_info(), "Start!")
        scene = bpy.context.scene
        process_task = scene.bfu_export_process_time_logs.add()  # type: ignore[attr-defined]
        if TYPE_CHECKING:
            process_task = BFU_OT_ExportProcessTimeLog()
        return process_task.start_timer(self.process_id, timer_name)

    def get_process_time_unique_id(self) -> str:
        if bpy.context is None:
            return ""
        scene = bpy.context.scene
        prefix = "pid_"
        index = str(len(scene.bfu_export_process_time_logs))  # type: ignore[attr-defined]
        return prefix + index

    def get_process_ref(self) -> Optional[BFU_OT_ExportProcessTimeLog]:
        if bpy.context is None:
            return None
        scene = bpy.context.scene
        for process_task in scene.bfu_export_process_time_logs:  # type: ignore[attr-defined]
            if TYPE_CHECKING:
                process_task = BFU_OT_ExportProcessTimeLog()
            if process_task.process_id == self.process_id:
                return process_task
        return None
        
    def get_process_info(self) -> str:
        process_ref = self.get_process_ref()
        if process_ref:
            return process_ref.process_info
        return ""

    def end_time_log(self):
        process_ref = self.get_process_ref()
        if process_ref:
            self.print_log(process_ref.process_info, "End!")
            process_ref.finish_timer()

    def print_log(self, *args: str):
        if self.should_print_log:
            print(*args)


class SafeTimeGroup():
    def __init__(self) -> None:
        self.log_handles: List[SafeTimeLogHandle] = []

    def start_timer(self, timer_name: str) -> SafeTimeLogHandle:
        process_task_proxy = SafeTimeLogHandle()
        process_task_proxy.start_timer(timer_name)
        self.log_handles.append(process_task_proxy)
        return process_task_proxy

    def end_last_timer(self) -> None:
        if self.log_handles:
            self.log_handles[-1].end_time_log()

classes = (
    BFU_OT_ExportProcessTimeLog,
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)  # type: ignore

    bpy.types.Scene.bfu_export_process_current_sub_step = bpy.props.IntProperty(  # type: ignore
        name="Current Sub Step",
        default=0,
    )
    bpy.types.Scene.bfu_export_process_faster_time = bpy.props.FloatProperty(  # type: ignore
        name="Faster Time",
        default=0.0,
        description="Faster time.",
    )
    bpy.types.Scene.bfu_export_process_slower_time = bpy.props.FloatProperty(  # type: ignore
        name="Slower Time",
        default=0.0,
        description="Slower time.",
    )
    bpy.types.Scene.bfu_export_process_time_logs = bpy.props.CollectionProperty(    # type: ignore
        type=BFU_OT_ExportProcessTimeLog)


def unregister():
    del bpy.types.Scene.bfu_export_process_time_logs  # type: ignore
    del bpy.types.Scene.bfu_export_process_slower_time  # type: ignore
    del bpy.types.Scene.bfu_export_process_faster_time  # type: ignore
    del bpy.types.Scene.bfu_export_process_current_sub_step  # type: ignore


    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)  # type: ignore
