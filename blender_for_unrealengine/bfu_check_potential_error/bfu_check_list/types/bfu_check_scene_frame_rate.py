# SPDX-FileCopyrightText: Xavier Loux (BleuRaven)
#
# SPDX-License-Identifier: GPL-3.0-or-later

# ----------------------------------------------
#  Blender For UnrealEngine
#  https://github.com/xavier150/Blender-For-UnrealEngine-Addons
# ----------------------------------------------

import bpy
from ...bfu_check_types import bfu_checker

class BFU_Checker_SceneFrameRate(bfu_checker):

    def __init__(self):
        super().__init__()
        self.check_name = "Scene Frame Rate"

    def run_scene_check(self, scene: bpy.types.Scene):
        # Check Scene Frame Rate.
        denominator = scene.render.fps_base
        numerator = scene.render.fps

        # Ensure denominator and numerator are at least 1 and int 32
        new_denominator = max(round(denominator), 1)
        new_numerator = max(round(numerator), 1)

        if denominator != new_denominator or numerator != new_numerator:
            message = (
                'Frame rate denominator and numerator must be an int32 over zero.\n'
                'Float denominator and numerator is not supported in Unreal Engine Sequencer.\n'
                f'- Denominator: {denominator} -> {new_denominator}\n'
                f'- Numerator: {numerator} -> {new_numerator}'
            )

            my_po_error = self.add_potential_error()
            my_po_error.name = scene.name
            my_po_error.type = 2
            my_po_error.text = message
            my_po_error.docs_octicon = 'scene-frame-rate'
