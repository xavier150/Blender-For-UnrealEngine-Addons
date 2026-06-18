# SPDX-FileCopyrightText: Xavier Loux (BleuRaven)
#
# SPDX-License-Identifier: GPL-3.0-or-later

# ----------------------------------------------
#  Blender For UnrealEngine
#  https://github.com/xavier150/Blender-For-UnrealEngine-Addons
# ----------------------------------------------

from typing import List
from .. import bpl
from .. import bfu_export_logs

def print_exported_asset_detail(exported_asset_log: List[bfu_export_logs.bfu_asset_export_logs_types.ExportedAssetLog]):
    bpl.advprint.print_simple_title("Exported asset(s)")
    print("")
    lines = bfu_export_logs.bfu_asset_export_logs_utils.get_export_asset_logs_details(exported_asset_log, True).splitlines()
    for line in lines:
        print(line)
    print("")
    bpl.advprint.print_simple_title("Timed steps")
    print("")
    lines = bfu_export_logs.bfu_process_time_logs_utils.get_process_time_logs_details().splitlines()
    for line in lines:
        print(line)
    print("")
    bpl.advprint.print_separator()