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


class NLA_Save():
    def __init__(self, nla_tracks):
        self.nla_tracks_save = None
        if nla_tracks is not None:
            self.SaveTracks(nla_tracks)

    def SaveTracks(self, nla_tracks):
        proxy_nla_tracks = []

        for nla_track in nla_tracks:
            proxy_nla_tracks.append(self.Proxy_NLA_Track(nla_track))
        self.nla_tracks_save = proxy_nla_tracks

    def ApplySaveOnTarget(self, target):
        if target is None:
            return
        if target.animation_data is None:
            return
        for nla_track in self.nla_tracks_save:
            new_nla_track = target.animation_data.nla_tracks.new()
            # new_nla_track.active = nla_track.active
            new_nla_track.is_solo = nla_track.is_solo
            new_nla_track.lock = nla_track.lock
            new_nla_track.mute = nla_track.mute
            new_nla_track.name = nla_track.name
            new_nla_track.select = nla_track.select
            for strip in nla_track.strips:
                if strip.action:
                    new_strip = new_nla_track.strips.new(strip.name, int(strip.frame_start), strip.action)
                    # new_strip.action = strip.action
                    new_strip.action_frame_end = strip.action_frame_end
                    new_strip.action_frame_start = strip.action_frame_start
                    # new_strip.active = strip.active
                    new_strip.blend_in = strip.blend_in
                    new_strip.blend_out = strip.blend_out
                    new_strip.blend_type = strip.blend_type
                    new_strip.extrapolation = strip.extrapolation
                    # new_strip.fcurves = strip.fcurves
                    new_strip.frame_end = strip.frame_end
                    # new_strip.frame_start = strip.frame_start
                    new_strip.use_animated_influence = strip.use_animated_influence
                    new_strip.influence = strip.influence
                    print(new_strip.influence)
                    print(new_strip.influence)
                    print(new_strip.influence)
                    print(new_strip.influence)
                    print(new_strip.influence)
                    print(new_strip.influence)
                    print(new_strip.influence)
                    # new_strip.modifiers = strip.modifiers #TO DO
                    new_strip.mute = strip.mute
                    # new_strip.name = strip.name
                    new_strip.repeat = strip.repeat
                    new_strip.scale = strip.scale
                    new_strip.select = strip.select
                    new_strip.strip_time = strip.strip_time
                    # new_strip.strips = strip.strips #TO DO
                    for i, fcurve in enumerate(strip.fcurves):
                        if fcurve:
                            new_fcurve = new_strip.fcurves.find(fcurve.data_path)
                            if new_fcurve:
                                new_fcurve.array_index = fcurve.array_index
                                new_fcurve.color = fcurve.color
                                new_fcurve.color_mode = fcurve.color_mode
                                # new_fcurve.data_path = fcurve.data_path
                                # new_fcurve.driver = fcurve.driver  #TO DO
                                new_fcurve.extrapolation = fcurve.extrapolation
                                new_fcurve.group = fcurve.group
                                new_fcurve.hide = fcurve.hide
                                # new_fcurve.is_empty = fcurve.is_empty
                                # new_fcurve.is_valid = fcurve.is_valid
                                # new_fcurve.keyframe_points = fcurve.keyframe_points
                                new_fcurve.lock = fcurve.lock
                                # new_fcurve.modifiers = fcurve.modifiers #TO DO
                                new_fcurve.mute = fcurve.mute
                                # new_fcurve.sampled_points = fcurve.sampled_points
                                new_fcurve.select = fcurve.select
                                for keyframe_point in fcurve.keyframe_points:
                                    new_fcurve.keyframe_points.insert(keyframe_point.co[0], keyframe_point.co[1])

    class Proxy_NLA_Track():
        def __init__(self, nla_track):
            if nla_track:
                self.active = nla_track.active
                self.is_solo = nla_track.is_solo
                self.lock = nla_track.lock
                self.mute = nla_track.mute
                self.name = nla_track.name
                self.select = nla_track.select
                self.strips = []
                for strip in nla_track.strips:
                    self.strips.append(self.Proxy_NLA_Track_Strip(strip))

        class Proxy_NLA_Track_Strip():
            def __init__(self, strip):
                self.action = strip.action
                self.action_frame_end = strip.action_frame_end
                self.action_frame_start = strip.action_frame_start
                self.active = strip.active
                self.blend_in = strip.blend_in
                self.blend_out = strip.blend_out
                self.blend_type = strip.blend_type
                self.extrapolation = strip.extrapolation
                self.fcurves = strip.fcurves  # TO DO
                self.frame_end = strip.frame_end
                self.frame_start = strip.frame_start
                self.use_animated_influence = strip.use_animated_influence
                self.influence = strip.influence
                self.modifiers = strip.modifiers  # TO DO
                self.mute = strip.mute
                self.name = strip.name
                self.repeat = strip.repeat
                self.scale = strip.scale
                self.select = strip.select
                self.strip_time = strip.strip_time
                # self.strips = strip.strips #TO DO


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
                    obj.animation_data.nla_tracks.remove(obj.animation_data.nla_tracks[0])

                # Add Current nla_tracks

                if self.nla_tracks_save is not None:
                    self.nla_tracks_save.ApplySaveOnTarget(obj)

        if SaveItTweakmode:
            bbpl.basics.EnterTweakmode()
