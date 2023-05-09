# ====================== BEGIN GPL LICENSE BLOCK ============================
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.	 See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.	 If not, see <http://www.gnu.org/licenses/>.
#  All rights reserved.
#
# ======================= END GPL LICENSE BLOCK =============================

# ----------------------------------------------
#  This addons allows to easily export several objects at the same time in .fbx
#  for use in unreal engine 4 by removing the usual constraints
#  while respecting UE4 naming conventions and a clean tree structure.
#  It also contains a small toolkit for collisions and sockets
#  xavierloux.com
# ----------------------------------------------

from .. import bbpl
import bpy


class NLA_Save():
    def __init__(self, nla_tracks):
        self.nla_tracks_save = None
        if nla_tracks is not None:
            self.SaveTracks(nla_tracks)

    def SaveTracks(self, nla_tracks):
        proxy_nla_tracks = []

        for nla_track in nla_tracks:
            proxy_nla_tracks.append(ProxyCopy_NLATrack(nla_track))
        self.nla_tracks_save = proxy_nla_tracks

    def ApplySaveOnTarget(self, target):

        if target is None:
            return
        if target.animation_data is None:
            return

        for nla_track in self.nla_tracks_save:
            pass
            new_nla_track = target.animation_data.nla_tracks.new()
            nla_track.PasteDataOn(new_nla_track)


class ProxyCopy_NLATrack():
    # Copy the NlaTrack(bpy_struct)
    # It used to do a safe for copy the struct.

    def __init__(self, nla_track: bpy.types.NlaTrack):
        if nla_track:
            self.active = nla_track.active
            self.is_solo = nla_track.is_solo
            self.lock = nla_track.lock
            self.mute = nla_track.mute
            self.name = nla_track.name
            self.select = nla_track.select
            self.strips = []
            for strip in nla_track.strips:
                self.strips.append(ProxyCopy_NlaStrip(strip))

    def PasteDataOn(self, nla_track: bpy.types.NlaTrack):
        if nla_track:
            # nla_track.active = self.active
            nla_track.is_solo = self.is_solo
            nla_track.lock = self.lock
            nla_track.mute = self.mute
            nla_track.name = self.name
            nla_track.select = self.select
            for strip in self.strips:
                if strip.action:
                    new_strip = nla_track.strips.new(strip.name, int(strip.frame_start), strip.action)
                    strip.PasteDataOn(new_strip)


class ProxyCopy_NlaStrip():
    # Copy the NlaStrip(bpy_struct)
    # It used to do a safe for copy the struct.

    def __init__(self, nla_strip: bpy.types.NlaStrip):
        self.action = nla_strip.action
        self.action_frame_end = nla_strip.action_frame_end
        self.action_frame_start = nla_strip.action_frame_start
        self.active = nla_strip.active
        self.blend_in = nla_strip.blend_in
        self.blend_out = nla_strip.blend_out
        self.blend_type = nla_strip.blend_type
        self.extrapolation = nla_strip.extrapolation
        self.fcurves = []
        # Since 3.5 interact to a NlaStripFCurves not linked to an object produce Blender Crash.
        for fcurve in nla_strip.fcurves:
            self.fcurves.append(ProxyCopy_FCurve(fcurve))
        self.frame_end = nla_strip.frame_end
        if bpy.app.version >= (3, 3, 0):
            self.frame_end_ui = nla_strip.frame_end_ui
        self.frame_start = nla_strip.frame_start
        if bpy.app.version >= (3, 3, 0):
            self.frame_start_ui = nla_strip.frame_start_ui
        self.influence = nla_strip.influence
        self.modifiers = nla_strip.modifiers  # TO DO
        self.mute = nla_strip.mute
        self.name = nla_strip.name
        self.repeat = nla_strip.repeat
        self.scale = nla_strip.scale
        self.select = nla_strip.select
        self.strip_time = nla_strip.strip_time
        # self.strips = strip.strips #TO DO
        self.type = nla_strip.type
        self.use_animated_influence = nla_strip.use_animated_influence
        if bpy.app.version >= (3, 0, 0):
            self.use_animated_time = nla_strip.use_animated_time
            self.use_animated_time_cyclic = nla_strip.use_animated_time_cyclic
            self.use_auto_blend = nla_strip.use_auto_blend
            self.use_reverse = nla_strip.use_reverse
            self.use_sync_length = nla_strip.use_sync_length

    def PasteDataOn(self, nla_strip: bpy.types.NlaStrip):
        # nla_strip.action = strip.action
        nla_strip.action_frame_end = self.action_frame_end
        nla_strip.action_frame_start = self.action_frame_start
        # nla_strip.active = self.active
        nla_strip.blend_in = self.blend_in
        nla_strip.blend_out = self.blend_out
        nla_strip.blend_type = self.blend_type
        nla_strip.extrapolation = self.extrapolation
        for i, fcurve in enumerate(self.fcurves):
            new_fcurve = nla_strip.fcurves.find(fcurve.data_path)  # Can't create so use find
            fcurve.PasteDataOn(new_fcurve)
        nla_strip.frame_end = self.frame_end
        if bpy.app.version >= (3, 3, 0):
            nla_strip.frame_end_ui = self.frame_end_ui
        nla_strip.frame_start = self.frame_start
        if bpy.app.version >= (3, 3, 0):
            nla_strip.frame_start_ui = self.frame_start_ui
        nla_strip.influence = self.influence
        # nla_strip.modifiers = self.modifiers #TO DO
        nla_strip.mute = self.mute
        # nla_strip.name = self.name
        nla_strip.repeat = self.repeat
        nla_strip.scale = self.scale
        nla_strip.select = self.select
        nla_strip.strip_time = self.strip_time
        # nla_strip.strips = self.strips #TO DO
        # nla_strip.type = self.type  # Read only
        nla_strip.use_animated_influence = self.use_animated_influence
        if bpy.app.version >= (3, 0, 0):
            nla_strip.use_animated_time = self.use_animated_time
            nla_strip.use_animated_time_cyclic = self.use_animated_time_cyclic
            nla_strip.use_auto_blend = self.use_auto_blend
            nla_strip.use_reverse = self.use_reverse
            nla_strip.use_sync_length = self.use_sync_length


class ProxyCopy_FCurve():
    # Copy the FCurve(bpy_struct)
    # It used to do a safe for copy the struct.

    def __init__(self, fcurve: bpy.types.FCurve):
        self.data_path = fcurve.data_path

    def PasteDataOn(self, fcurve: bpy.types.FCurve):
        pass


class AnimationManagment():
    def __init__(self):
        self.use_animation_data = False
        self.action = None
        self.action_extrapolation = "HOLD"  # Default value
        self.action_blend_type = "REPLACE"  # Default value
        self.action_influence = 1.0  # Default value

    def SaveAnimationData(self, obj):
        if obj.animation_data is not None:
            self.action = obj.animation_data.action
            self.action_extrapolation = obj.animation_data.action_extrapolation
            self.action_blend_type = obj.animation_data.action_blend_type
            self.action_influence = obj.animation_data.action_influence
            self.nla_tracks_save = NLA_Save(obj.animation_data.nla_tracks)
            self.use_animation_data = True
        else:
            self.use_animation_data = False

    def ClearAnimationData(self, obj):
        obj.animation_data_clear()

    def SetAnimationData(self, obj, copy_nla=False):

        SaveItTweakmode = bbpl.basics.IsTweakmode()
        bbpl.basics.ExitTweakmode()
        print("Set animation data on: ", obj)
        if self.use_animation_data:
            obj.animation_data_create()

        if obj.animation_data is not None:

            obj.animation_data.action = self.action
            obj.animation_data.action_extrapolation = self.action_extrapolation
            obj.animation_data.action_blend_type = self.action_blend_type
            obj.animation_data.action_influence = self.action_influence

            if copy_nla:
                # Clear nla_tracks
                nla_tracks_len = len(obj.animation_data.nla_tracks)
                for x in range(nla_tracks_len):
                    pass
                    obj.animation_data.nla_tracks.remove(obj.animation_data.nla_tracks[0])

                # Add Current nla_tracks
                if self.nla_tracks_save is not None:
                    pass
                    self.nla_tracks_save.ApplySaveOnTarget(obj)

        if SaveItTweakmode:
            bbpl.basics.EnterTweakmode()
