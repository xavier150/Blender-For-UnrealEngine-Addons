# SPDX-FileCopyrightText: Xavier Loux (BleuRaven)
#
# SPDX-License-Identifier: GPL-3.0-or-later

# ----------------------------------------------
#  Blender For UnrealEngine
#  https://github.com/xavier150/Blender-For-UnrealEngine-Addons
# ----------------------------------------------

import unreal


def set_sequence_preview_skeletal_mesh(asset: unreal.AnimSequence, origin_skeletal_mesh):
    if origin_skeletal_mesh:
        if asset:
            # @TODO preview_pose_asset doesn’t retarget right now. Need wait update in Unreal Engine Python API.
            asset.get_editor_property('preview_pose_asset')
            pass
            