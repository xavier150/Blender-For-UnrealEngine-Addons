# SPDX-FileCopyrightText: Xavier Loux (BleuRaven)
#
# SPDX-License-Identifier: GPL-3.0-or-later

# ----------------------------------------------
#  Blender For UnrealEngine
#  https://github.com/xavier150/Blender-For-UnrealEngine-Addons
# ----------------------------------------------

import time
from typing import List
from . import bpl

# WARNING /!\ Keep all on False for production.
SHOW_SPLINE_DEBUG_PANEL = False
PRINT_DRAW_DEBUG_TIMES = False
DISABLE_ASSET_SEARCH_CACHING = False  # For debug, disable the asset search caching system.

# ------------------------

class debug_event():
    def __init__(self, name: str):
        self.name = name
        self.start_time = time.perf_counter()
        self.stop_time = None
        self.sub_events: List[debug_event] = []
        self.separator = "."
        self.avoid_zero_delay_print = False

    def stop(self):
        self.stop_time = time.perf_counter()

    def print_state(self, parent_name: str = ""):
        if parent_name == "":
            print_name = f"{self.name}"
        else:
            print_name = f"{parent_name}{self.separator}{self.name}"

        if self.stop_time is None:
            print(f"'{print_name}' never finished!")
        else:
            elapsed_time = self.stop_time - self.start_time
            if (not self.avoid_zero_delay_print) or elapsed_time > 0.0:
                str_ms_time = bpl.color_set.yellow(f"{elapsed_time * 1000:.4f} ms")
                print(f"'{print_name}' took {str_ms_time}")

            for sub_event in self.sub_events:
                sub_event.print_state(print_name)


current_record: List[debug_event] = []


def start_draw_record() -> None:
    if PRINT_DRAW_DEBUG_TIMES:
        current_record.clear()

def stop_draw_record_and_print() -> None:
    if PRINT_DRAW_DEBUG_TIMES:
        count = len(current_record)
        print("------------------------------------")
        print(f"Recorded: {count} events")
        for record in current_record:
            record.print_state()
        current_record.clear()


class event_helper():
    def __init__(self):
        self.current_events: List[debug_event] = []

    def new_event(self, name: str) -> debug_event:
        if not PRINT_DRAW_DEBUG_TIMES:
            return debug_event("")
        
        event = debug_event(name)
        current_record.append(event)
        self.current_events.append(event)
        return event

    def stop_last_event(self):
        if not PRINT_DRAW_DEBUG_TIMES:
            return

        if self.current_events:
            last_event = self.current_events[-1]
            last_event.stop()
            self.current_events.remove(last_event)

    def stop_last_and_start_new_event(self, name: str) -> debug_event:
        if not PRINT_DRAW_DEBUG_TIMES:
            return debug_event("")

        self.stop_last_event()
        return self.add_sub_event(name)

    def add_sub_event(self, name: str) -> debug_event:
        if not PRINT_DRAW_DEBUG_TIMES:
            return debug_event("")

        if self.current_events:
            last_event = self.current_events[-1]
            event = debug_event(name)
            self.current_events.append(event)
            last_event.sub_events.append(event)
            return event
        return self.new_event(name)
    
root_events = event_helper()