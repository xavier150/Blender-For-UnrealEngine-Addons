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
#  BBPL -> BleuRaven Blender Python Library
#  BleuRaven.fr
#  XavierLoux.com
# ----------------------------------------------

import bpy
import mathutils
from . import scene_utils
from . import utils


class NLA_Save:
    def __init__(self, nla_tracks):
        """
        Initializes the NLA_Save object.

        Args:
            nla_tracks (list): The NLA tracks to save.

        Returns:
            None
        """
        self.nla_tracks_save = None
        if nla_tracks is not None:
            self.save_tracks(nla_tracks)

    def save_tracks(self, nla_tracks):
        """
        Saves the NLA tracks.

        Args:
            nla_tracks (list): The NLA tracks to save.

        Returns:
            None
        """
        proxy_nla_tracks = []

        for nla_track in nla_tracks:
            proxy_nla_tracks.append(ProxyCopy_NLATrack(nla_track))
        self.nla_tracks_save = proxy_nla_tracks

    def apply_save_on_target(self, target):
        """
        Applies the saved NLA tracks to the target object.

        Args:
            target (bpy.types.Object): The target object to apply the saved NLA tracks.

        Returns:
            None
        """
        if target is None or target.animation_data is None:
            return

        for nla_track in self.nla_tracks_save:
            new_nla_track = target.animation_data.nla_tracks.new()
            nla_track.paste_data_on(new_nla_track)

class ProxyCopy_NLATrack:
    """
    Proxy class for copying bpy.types.NlaTrack.

    It is used to safely copy the bpy.types.NlaTrack struct.
    """

    def __init__(self, nla_track):
        """
        Initializes the ProxyCopy_NLATrack object.

        Args:
            nla_track (bpy.types.NlaTrack): The NlaTrack to copy.

        Returns:
            None
        """
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

    def paste_data_on(self, nla_track):
        """
        Pastes the saved data onto the target NlaTrack.

        Args:
            nla_track (bpy.types.NlaTrack): The target NlaTrack to paste the data on.

        Returns:
            None
        """
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
                    strip.paste_data_on(new_strip)


class ProxyCopy_NlaStrip:
    """
    Proxy class for copying bpy.types.NlaStrip.

    It is used to safely copy the bpy.types.NlaStrip struct.
    """

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
            self.fcurves.append(ProxyCopy_StripFCurve(fcurve))
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

    def paste_data_on(self, nla_strip: bpy.types.NlaStrip):
        # nla_strip.action = strip.action
        nla_strip.action_frame_end = self.action_frame_end
        nla_strip.action_frame_start = self.action_frame_start
        # nla_strip.active = self.active
        nla_strip.blend_in = self.blend_in
        nla_strip.blend_out = self.blend_out
        nla_strip.blend_type = self.blend_type
        nla_strip.extrapolation = self.extrapolation
        for fcurve in self.fcurves:
            fcurve.paste_data_on(nla_strip)
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


class ProxyCopy_StripFCurve():
    """
    Proxy class for copying bpy.types.NlaStripFCurves. (NLA Strip only)

    It is used to safely copy the bpy.types.NlaStripFCurves struct.
    """

    def __init__(self, fcurve: bpy.types.NlaStripFCurves):
        self.data_path = fcurve.data_path
        self.keyframe_points = []
        for keyframe_point in fcurve.keyframe_points:
            self.keyframe_points.append(ProxyCopy_Keyframe(keyframe_point))

    def paste_data_on(self, strips: bpy.types.NlaStrips):
        if self.data_path == "influence":
            # Create the curve with use_animated_influence
            strips.use_animated_influence = True 

            for key in self.keyframe_points:
                strips.influence = key.co[1]
                strips.keyframe_insert(data_path="influence", frame=key.co[0], keytype=key.type)



class ProxyCopy_FCurve():
    """
    Proxy class for copying bpy.types.FCurve. 

    It is used to safely copy the bpy.types.FCurve struct.
    """

    def __init__(self, fcurve: bpy.types.FCurve):
        self.data_path = fcurve.data_path
        self.keyframe_points = []
        for keyframe_point in fcurve.keyframe_points:
            self.keyframe_points.append(ProxyCopy_Keyframe(keyframe_point))

    def paste_data_on(self, fcurve: bpy.types.FCurve):
        fcurve.data_path = self.data_path
        for keyframe_point in self.keyframe_points:
            pass
            #TODO


class ProxyCopy_Keyframe():
    """
    Proxy class for copying bpy.types.Keyframe. (NLA Strip only)

    It is used to safely copy the bpy.types.Keyframe struct.
    """

    def __init__(self, keyframe: bpy.types.Keyframe):
        self.co = keyframe.co
        self.type = keyframe.type

    def paste_data_on(self, keyframe: bpy.types.Keyframe):
        keyframe.co = self.co
        keyframe.type = self.type



def copy_attributes(a, b):
    keys = dir(a)
    for key in keys:
        if not key.startswith("_") \
        and not key.startswith("error_") \
        and key != "group" \
        and key != "strips" \
        and key != "is_valid" \
        and key != "rna_type" \
        and key != "bl_rna":
            try:
                setattr(b, key, getattr(a, key))
            except AttributeError:
                pass


def copy_drivers(src, dst):
    # Copy drivers
    if src.animation_data:
        for d1 in src.animation_data.drivers:
            d2 = dst.driver_add(d1.data_path)
            copy_attributes(d1, d2)
            copy_attributes(d1.driver, d2.driver)

            # Remove default modifiers, variables, etc.
            for m in d2.modifiers:
                d2.modifiers.remove(m)
            for v in d2.driver.variables:
                d2.driver.variables.remove(v)

            # Copy modifiers
            for m1 in d1.modifiers:
                m2 = d2.modifiers.new(type=m1.type)
                copy_attributes(m1, m2)

            # Copy variables
            for v1 in d1.driver.variables:
                v2 = d2.driver.variables.new()
                copy_attributes(v1, v2)
                for i in range(len(v1.targets)):
                    copy_attributes(v1.targets[i], v2.targets[i])
                    # Switch self reference targets to new self
                    if v2.targets[i].id == src:
                        v2.targets[i].id = dst

            # Copy key frames
            try:
                for i in range(len(d1.keyframe_points)):
                    d2.keyframe_points.add()
                    k1 = d1.keyframe_points[i]
                    k2 = d2.keyframe_points[i]
                    copy_attributes(k1, k2)
            except TypeError:
                pass


class AnimationManagment():
    """
    Helper class for managing animation data in Blender.
    """

    def __init__(self):
        self.use_animation_data = False
        self.action = None
        self.action_extrapolation = "HOLD"
        self.action_blend_type = "REPLACE"
        self.action_influence = 1.0
        self.nla_tracks_save = None

    def save_animation_data(self, obj):
        """
        Saves the animation data from the object.

        Args:
            obj (bpy.types.Object): The object to save the animation data from.
        """
        if obj.animation_data is not None:
            self.action = obj.animation_data.action
            self.action_extrapolation = obj.animation_data.action_extrapolation
            self.action_blend_type = obj.animation_data.action_blend_type
            self.action_influence = obj.animation_data.action_influence
            self.nla_tracks_save = NLA_Save(obj.animation_data.nla_tracks)
            self.use_animation_data = True
        else:
            self.use_animation_data = False

    def clear_animation_data(self, obj):
        """
        Clears the animation data from the object.

        Args:
            obj (bpy.types.Object): The object to clear the animation data from.
        """
        obj.animation_data_clear()

    def set_animation_data(self, obj, copy_nla=False):
        """
        Sets the animation data on the object.

        Args:
            obj (bpy.types.Object): The object to set the animation data on.
            copy_nla (bool, optional): Whether to copy the Non-Linear Animation (NLA) tracks. Defaults to False.
        """

        save_it_tweakmode = scene_utils.is_tweak_mode()
        scene_utils.exit_tweak_mode()
        print("Set animation data on:", obj)
        if self.use_animation_data:
            obj.animation_data_create()

        if obj.animation_data is not None:
            obj.animation_data.action = self.action
            obj.animation_data.action_extrapolation = self.action_extrapolation
            obj.animation_data.action_blend_type = self.action_blend_type
            obj.animation_data.action_influence = self.action_influence

            if copy_nla:
                # Clear nla_tracks
                nla_tracks = obj.animation_data.nla_tracks[:]
                for nla_track in nla_tracks:
                    obj.animation_data.nla_tracks.remove(nla_track)

                # Add current nla_tracks
                if self.nla_tracks_save is not None:
                    self.nla_tracks_save.apply_save_on_target(obj)

        if save_it_tweakmode:
            scene_utils.enter_tweak_mode()

def reset_armature_pose(obj):
    """
    Resets the pose of an armature object.

    Args:
        obj (bpy.types.Object): The armature object.

    Returns:
        None
    """
    for b in obj.pose.bones:
        b.rotation_quaternion = mathutils.Quaternion()
        b.rotation_euler = mathutils.Vector((0, 0, 0))
        b.scale = mathutils.Vector((1, 1, 1))
        b.location = mathutils.Vector((0, 0, 0))


class ProxyCopy_Constraint:
    """
    Proxy class for copying Blender PoseBoneConstraints.

    It is used to safely copy Blender PoseBoneConstraints.
    """

    def __init__(self, constraint):
        """
        Initializes the ProxyCopy_Constraint object.

        Args:
            constraint (bpy.types.Constraint): The constraint to copy.

        Returns:
            None
        """
        if constraint:
            self.type = constraint.type
            self.name = constraint.name
            self.target = constraint.target
            self.subtarget = constraint.subtarget
            self.influence = constraint.influence
            self.mute = constraint.mute
            self.target_space = constraint.target_space
            self.owner_space = constraint.owner_space
            # Add more constraint parameters here as needed

            if self.type == 'CHILD_OF':
                self.inverse_matrix = constraint.inverse_matrix.copy() 


    def paste_data_on(self, target_constraint):
        """
        Pastes the saved data onto the target constraint.

        Args:
            target_constraint (bpy.types.Constraint): The target constraint to apply the data to.

        Returns:
            None
        """
        if target_constraint:
            #target_constraint.type = self.type
            target_constraint.name = self.name
            target_constraint.target = self.target
            target_constraint.subtarget = self.subtarget
            target_constraint.influence = self.influence
            target_constraint.mute = self.mute
            target_constraint.target_space = self.target_space
            target_constraint.owner_space = self.owner_space
            # Copy more constraint parameters here as needed

            if self.type == 'CHILD_OF':
                target_constraint.inverse_matrix = self.inverse_matrix 


class BoneConstraintManagment():
    """
    Helper class for managing Bone Constraint data in Blender.
    """

    def __init__(self):
        self.saved_constraints = []

    def save_bone_constraints_data(self, armature, bone_name):
        """
        Saves the constraints data from an armature bone.

        Args:
            armature: The armature object where the bone is located.
            bone_name: The name of the bone you want to save constraints for.
        """
        # Get the bone object from the armature
        bone = armature.pose.bones.get(bone_name)

        if bone:
            # Clear the saved_constraints list to start fresh
            self.saved_constraints.clear()

            # Get the list of constraints on the bone and save them
            for constraint in bone.constraints:
                self.saved_constraints.append(ProxyCopy_Constraint(constraint))

            #print(f"Constraints for bone {bone_name} saved successfully.")
        else:
            print(f"Bone {bone_name} not found in the armature.")


    def set_bone_constraints_data(self, armature, bone_name, replace=True):
        """
        Sets the constraints data on the bone of an armature.

        Args:
            armature: The armature object where the bone is located.
            bone_name: The name of the bone on which you want to set constraints.
            replace: If True, replace existing constraints; if False, keep them and add saved constraints.
        """
        # Get the bone object from the armature
        bone = armature.pose.bones.get(bone_name)

        if bone:
            if replace:
                # Remove all existing constraints on the bone
                for old_constraint in bone.constraints:
                    bone.constraints.remove(old_constraint)

            # Add the saved constraints to the bone
            for constraint_data in self.saved_constraints:
                new_constraint = bone.constraints.new(type=constraint_data.type)
                constraint_data.paste_data_on(new_constraint)

            print(f"Constraints for bone {bone_name} set successfully.")
        else:
            print(f"Bone {bone_name} not found in the armature.")

class RigConstraintManagment():
    """
    Helper class for managing Rig Constraint data in Blender.
    """

    def __init__(self):
        self.saved_bones_constraints = {}

    def save_rig_constraints_data(self, armature, bone_names):
        """
        Saves the constraints data from an armature bone.

        Args:
            armature: The armature object where the bone is located.
            bone_names: The names of the bones you want to save constraints for.
        """
        self.saved_bones_constraints.clear()

        for bone_name in bone_names:
            bone = armature.pose.bones.get(bone_name)
            constraints = BoneConstraintManagment()
            constraints.save_bone_constraints_data(armature, bone_name)

            if bone:
                self.saved_bones_constraints[bone_name] = constraints

                #print(f"Constraints for bone {bone_name} saved successfully.")
            else:
                print(f"Bone {bone_name} not found in the armature.")


    def set_rig_constraints_data(self, armature, replace=True):
        """
        Sets the constraints data on the bones of an armature.

        Args:
            armature: The armature object where the bones are located.
            replace: If True, replace existing constraints; if False, keep them and add saved constraints.
        """
        for bone_name, constraints in self.saved_bones_constraints.items():
            constraints.set_bone_constraints_data(armature, bone_name, replace)
