# SPDX-FileCopyrightText: 2024-2025 Xavier Loux (BleuRaven)
#
# SPDX-License-Identifier: GPL-3.0-or-later

# ----------------------------------------------
#  BBAM -> BleuRaven Blender Addon Manager
#  https://github.com/xavier150/BBAM
# ----------------------------------------------

import bpy
import time
from typing import List, Tuple, Union
from .bbam_addon_config.bbam_addon_config_type import BBAM_GenerateMethod

class BBAM_TimedTask:

    def __init__(self, task_index: int, step_count: int, task_text: str) -> None:
        self.task_index = task_index
        self.step_count = step_count
        self.task_text = task_text
        self.start_time = time.time()
        self.end_time = 0.0
        print(f"-> Step {self.task_index}/{self.step_count}: {self.task_text}...")

    def end_task(self) -> float:
        """
        Ends the timed task and returns the elapsed time in seconds.
        """
        self.end_time = time.time()
        elapsed_time = self.end_time - self.start_time
        elapsed_time_str = f"\033[93m{get_time_string(elapsed_time)}\033[0m"

        print(f"Completed in {elapsed_time_str}")
        print("")
        return elapsed_time

    def get_elapsed_time(self) -> float:
        if self.end_time > 0:
            return self.end_time - self.start_time
        else:
            return time.time() - self.start_time
    
class BBAM_TimedTaskManager:

    def __init__(self) -> None:
        self.tasks: List[BBAM_TimedTask] = []
        self.step_count = 0

    def get_all_elapsed_times(self) -> List[float]:
        """
        Returns a list of elapsed times for all tasks.
        """
        return [task.get_elapsed_time() for task in self.tasks]

    def set_step_count(self, count: int):
        self.step_count = count

    def start_new_task(self, task_index: int, task_text: str) -> BBAM_TimedTask:
        task = BBAM_TimedTask(task_index, self.step_count, task_text)
        self.tasks.append(task)
        return task

    # End current task and start a new one
    def end_current_task_and_start_new(self, task_index: int, task_text: str) -> BBAM_TimedTask:
        if self.tasks:
            self.tasks[-1].end_task()
        return self.start_new_task(task_index, task_text)
    
    def end_current_task(self) -> float:
        if self.tasks:
            last_task = self.tasks[-1]
            if last_task.task_index == self.step_count:
                totaled_time = sum(task.get_elapsed_time() for task in self.tasks)
                totaled_time_str = f"\033[93m{get_time_string(totaled_time)}\033[0m"
                print(f"Total time for all tasks: {totaled_time_str}")
                return totaled_time
            else:
                return last_task.end_task()

        return 0.0
    
def get_time_string(seconds: float) -> str:
    if seconds < 1.0:
        return f"{seconds * 1000:.2f}ms"
    else:
        return f"{seconds:.2f}s"


def print_red(*values: Union[str, int, float]) -> None:
    print("\033[91m", *values, "\033[0m")

# @TODO Deprecated, remove in future versions
def get_str_version(data: List[int]) -> str:
    """
    Converts a list of version components into a version string.

    Parameters:
        data (list): A list of integers representing the version, e.g., [1, 2, 3].

    Returns:
        str: A string representation of the version, e.g., "1.2.3".
    """
    return f'{data[0]}.{data[1]}.{data[2]}'


def get_should_install_for_curren_version(auto_install_range_data: Tuple[List[int], Union[List[int], str]]):
    min_version = auto_install_range_data[0]
    max_version = auto_install_range_data[1]
    blender_version = bpy.app.version

    if max_version == "LATEST":
        return tuple(min_version) <= blender_version
    else:
        return tuple(min_version) <= blender_version <= tuple(max_version)
    
    return False

def get_generate_using_extension_command(generate_method: BBAM_GenerateMethod, blender_version_min: List[int]) -> bool:
    if generate_method == BBAM_GenerateMethod.AUTO_DETECT:
        return blender_version_min >= [4, 2, 0]
    else:
        return (generate_method == BBAM_GenerateMethod.EXTENTION_COMMAND)