# SPDX-FileCopyrightText: Xavier Loux (BleuRaven)
#
# SPDX-License-Identifier: GPL-3.0-or-later

# ----------------------------------------------
#  Blender For UnrealEngine
#  https://github.com/xavier150/Blender-For-UnrealEngine-Addons
# ----------------------------------------------

import bpy
from ...bfu_check_types import bfu_checker

class BFU_Checker_MarkerOverlay(bfu_checker):

    def __init__(self):
        super().__init__()
        self.check_name = "Marker Overlay"

    # Check that there is no overlap with the markers in the scene timeline
    def run_scene_check(self, scene: bpy.types.Scene):
        used_frames: List[int] = []
        for marker in scene.timeline_markers:
            if marker.frame in used_frames:
                my_po_error = self.add_potential_error()
                my_po_error.type = 2
                my_po_error.text = (
                    f'In the scene timeline, the frame "{marker.frame}" contains overlapping markers.'
                    '\nTo avoid camera conflicts in the generation of the sequencer, '
                    'you must use a maximum of one marker per frame.'
                )
            else:
                used_frames.append(marker.frame)
