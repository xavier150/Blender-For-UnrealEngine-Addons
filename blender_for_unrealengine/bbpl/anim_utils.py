# SPDX-FileCopyrightText: Xavier Loux (BleuRaven)
#
# SPDX-License-Identifier: GPL-3.0-or-later

# ----------------------------------------------
#  BBPL -> BleuRaven Blender Python Library
#  https://github.com/xavier150/BBPL
# ----------------------------------------------

import bpy
import mathutils
from typing import List, Optional, Union
from . import scene_utils


class NLA_Save:
    def __init__(self, nla_tracks: bpy.types.NlaTracks):
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

    def save_tracks(self, nla_tracks: bpy.types.NlaTracks):
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

    def apply_save_on_target(self, target: bpy.types.Object):
        """
        Applies the saved NLA tracks to the target object.

        Args:
            target (bpy.types.Object): The target object to apply the saved NLA tracks.

        Returns:
            None
        """
        if target is None or target.animation_data is None:
            return

        for nla_track in self.nla_tracks_save: # type: ignore
            new_nla_track = target.animation_data.nla_tracks.new()
            nla_track.paste_data_on(new_nla_track)

class ProxyCopy_NLATrack:
    """
    Proxy class for copying bpy.types.NlaTrack.

    It is used to safely copy the bpy.types.NlaTrack struct.
    """

    def __init__(self, nla_track: bpy.types.NlaTrack):
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
            self.strips: List[ProxyCopy_NlaStrip] = []
            for strip in nla_track.strips:
                self.strips.append(ProxyCopy_NlaStrip(strip))

    def paste_data_on(self, nla_track: bpy.types.NlaTrack):
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
        self.action: Optional[bpy.types.Action] = nla_strip.action
        self.action_frame_end: float = nla_strip.action_frame_end
        self.action_frame_start: float = nla_strip.action_frame_start
        self.active: Optional[bool] = nla_strip.active
        self.blend_in: float = nla_strip.blend_in
        self.blend_out: float = nla_strip.blend_out
        self.blend_type: str = nla_strip.blend_type
        self.extrapolation: str = nla_strip.extrapolation
        self.fcurves: List[ProxyCopy_StripFCurve] = []
        # Since 3.5 interact to a NlaStripFCurves not linked to an object produce Blender Crash.
        for fcurve in nla_strip.fcurves:
            self.fcurves.append(ProxyCopy_StripFCurve(fcurve))
        self.frame_end: float = nla_strip.frame_end
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

        # influence and animated influence need to be set before all.
        nla_strip.influence = 0.5
        
        # I don't know why but when I set use_animated_influence or influence 
        # it automatically adds a key in the curve...
        # This is why I override and not do a simple paste
        nla_strip.use_animated_influence = self.use_animated_influence
        for fcurve in self.fcurves:
            fcurve.paste_data_on(nla_strip, override=True)

        # Auto Blend need to be set before the Blend values.
        if bpy.app.version >= (3, 0, 0):
            nla_strip.use_auto_blend = self.use_auto_blend
        nla_strip.blend_in = self.blend_in
        nla_strip.blend_out = self.blend_out
        nla_strip.blend_type = self.blend_type  # type: ignore

        # Strip Time
        if bpy.app.version >= (3, 0, 0):
            nla_strip.use_animated_time = self.use_animated_time
        nla_strip.strip_time = self.strip_time

        # Playback
        if bpy.app.version >= (3, 0, 0):
            nla_strip.use_animated_time_cyclic = self.use_animated_time_cyclic
            nla_strip.use_reverse = self.use_reverse

        # Action Clip
        if bpy.app.version >= (3, 0, 0):
            nla_strip.use_sync_length = self.use_sync_length
        # nla_strip.action = strip.action
        nla_strip.action_frame_end = self.action_frame_end
        nla_strip.action_frame_start = self.action_frame_start
        nla_strip.repeat = self.repeat
        nla_strip.scale = self.scale

        # nla_strip.active = self.active
        nla_strip.extrapolation = self.extrapolation  # type: ignore
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

        nla_strip.select = self.select

        # nla_strip.strips = self.strips #TO DO
        # nla_strip.type = self.type  # Read only


class ProxyCopy_StripFCurve():
    """
    Proxy class for copying bpy.types.NlaStripFCurves. (NLA Strip only)

    It is used to safely copy the bpy.types.NlaStripFCurves struct.
    """

    def __init__(self, fcurve: bpy.types.FCurve):
        self.data_path = fcurve.data_path
        self.keyframe_points: List[ProxyCopy_Keyframe] = []
        for keyframe_point in fcurve.keyframe_points:
            self.keyframe_points.append(ProxyCopy_Keyframe(keyframe_point))

    def print_stored_keys(self):
        for key in self.keyframe_points:
            key.print_stored_key()


    def paste_data_on(self, strips: bpy.types.NlaStrip, override=False):
        #Found the corrected curve
        for fcurve in strips.fcurves:
            if self.data_path == "influence" and fcurve.data_path == "influence":
                if override == True:
                    fcurve.keyframe_points.clear()
                # Create the curve with use_animated_influence
                for key in self.keyframe_points:
                    new_key = fcurve.keyframe_points.insert(frame=key.co[0], value=key.co[1], keyframe_type=key.type)
                    key.paste_data_on(new_key)


class ProxyCopy_FCurve():
    """
    Proxy class for copying bpy.types.FCurve. 

    It is used to safely copy the bpy.types.FCurve struct.
    """

    def __init__(self, fcurve: bpy.types.FCurve):
        self.data_path = fcurve.data_path
        self.keyframe_points: List[ProxyCopy_Keyframe] = []
        for keyframe_point in fcurve.keyframe_points:
            self.keyframe_points.append(ProxyCopy_Keyframe(keyframe_point))

    def paste_data_on(self, fcurve: bpy.types.FCurve):
        fcurve.data_path = self.data_path
        for key in self.keyframe_points:
            new_key = fcurve.keyframe_points.insert(frame=key.co[0], value=key.co[1], keyframe_type=key.type)
            key.paste_data_on(new_key)


class ProxyCopy_Keyframe():
    """
    Proxy class for copying bpy.types.Keyframe.

    It is used to safely copy the bpy.types.Keyframe struct.
    """

    def __init__(self, keyframe: bpy.types.Keyframe):
        self.co = keyframe.co.copy()
        self.type = keyframe.type
        self.interpolation = keyframe.interpolation
        self.handle_left = keyframe.handle_left.copy()
        self.handle_left_type = keyframe.handle_left_type
        self.handle_right = keyframe.handle_right.copy()
        self.handle_right_type = keyframe.handle_right_type
        self.select_control_point = keyframe.select_control_point
        self.select_left_handle = keyframe.select_left_handle
        self.select_right_handle = keyframe.select_right_handle
        

    def print_stored_key(self):
        print(self.co, self.type, self.interpolation)

    def paste_data_on(self, keyframe: bpy.types.Keyframe):
        keyframe.co = self.co
        keyframe.type = self.type
        keyframe.interpolation = self.interpolation
        keyframe.handle_left = self.handle_left
        keyframe.handle_left_type = self.handle_left_type
        keyframe.handle_right = self.handle_right
        keyframe.handle_right_type = self.handle_right_type
        keyframe.select_control_point = self.select_control_point
        keyframe.select_left_handle = self.select_left_handle
        keyframe.select_right_handle = self.select_right_handle




def copy_attributes(a, b, priority_vars = [], ignore_list = [], print_fails = True):
    def copyattr(source, target, attr_name):
        try:
            setattr(target, attr_name, getattr(source, attr_name))
        except AttributeError as e:
            if print_fails:
                print(f"Error copying attribute '{attr_name}' from {str(source)} to from {str(target)}")
                print(f": {e}")
    
    # Filter only attributes (not functions)
    keys = [key for key in dir(a) if not callable(getattr(a, key))]

    for priority_var in priority_vars:
        if priority_var not in ignore_list:
            if priority_var in keys:
                copyattr(a, b, priority_var)

    for key in keys:
        if key not in ignore_list:
            if not key.startswith("_") \
            and not key.startswith("error_") \
            and key != "rna_type" \
            and key != "bl_rna":
                copyattr(a, b, key)

def copy_fcurve_attr(a :bpy.types.FCurve, b :bpy.types.FCurve, print_fails = True):
    if not isinstance(a, bpy.types.FCurve) or not isinstance(b, bpy.types.FCurve):
        raise TypeError(f"Expected 'bpy.types.FCurve', but got {type(a).__name__} and {type(b).__name__}")
    priority_vars = []
    ignore_list = [
        "driver",
        "is_empty",
        "keyframe_points",
        "modifiers",
        "sampled_points",
        "group",
    ]

    copy_attributes(a, b, priority_vars, ignore_list, print_fails)

def copy_modifier_attr(a :bpy.types.FModifier, b :bpy.types.FModifier, print_fails = True):
    if not isinstance(a, bpy.types.FModifier) or not isinstance(b, bpy.types.FModifier):
        raise TypeError(f"Expected 'bpy.types.FModifier', but got {type(a).__name__} and {type(b).__name__}")
    priority_vars = []
    ignore_list = [
        'type',
        "is_valid",
    ]
    copy_attributes(a, b, priority_vars, ignore_list, print_fails)

def copy_driver_attr(a: bpy.types.Driver, b: bpy.types.Driver, print_fails = True):
    if not isinstance(a, bpy.types.Driver) or not isinstance(b, bpy.types.Driver):
        raise TypeError(f"Expected 'bpy.types.Driver', but got {type(a).__name__} and {type(b).__name__}")
    priority_vars = []
    ignore_list = [
        "is_simple_expression",
        "variables",
    ]
    copy_attributes(a, b, priority_vars, ignore_list, print_fails)

def copy_drivertarget_attr(a: bpy.types.DriverTarget, b: bpy.types.DriverTarget, print_fails = True):

    if not isinstance(a, bpy.types.DriverTarget) or not isinstance(b, bpy.types.DriverTarget):
        raise TypeError(f"Expected 'bpy.types.DriverTarget', but got {type(a).__name__} and {type(b).__name__}")

    # The value id_type must be set first! 
    # In some case id_type may read only depending DriverVariable.type

    priority_vars = [
        'id_type',
    ]
    ignore_list = [
        'is_fallback_used',
    ]
    copy_attributes(a, b, priority_vars, ignore_list, print_fails)

def copy_drivervariable_attr(a: bpy.types.DriverVariable, b: bpy.types.DriverVariable, print_fails = True):
    if not isinstance(a, bpy.types.DriverVariable) or not isinstance(b, bpy.types.DriverVariable):
        raise TypeError(f"Expected 'bpy.types.DriverVariable', but got {type(a).__name__} and {type(b).__name__}")
    priority_vars = []
    ignore_list = [
        "is_name_valid",
        "targets",
        "id_type",
    ]
    copy_attributes(a, b, priority_vars, ignore_list, print_fails)

def copy_drivers(src: bpy.types.Object, dst: bpy.types.Object):
    print_fails = False

    def try_add_array_driver(target_data: bpy.types.ID, data_path: str, index: int) -> Optional[Union[bpy.types.FCurve, List[bpy.types.FCurve]]]:
        try:
            return dst.driver_add(data_path, index)
        except Exception as e:
            if print_fails:
                print(f"Failed to add array driver for {data_path} on {dst.name}: {e}")
            return None


    def try_add_driver(target_data: bpy.types.ID, data_path: str) -> Optional[Union[bpy.types.FCurve, List[bpy.types.FCurve]]]:
        try:
            return dst.driver_add(data_path)
        except Exception as e:
            if print_fails:
                print(f"Failed to add driver for {data_path} on {dst.name}: {e}")
            return None

    # Copy drivers
    if src.animation_data:
        for d1 in src.animation_data.drivers:
            source_data_path = d1.data_path
            prop = src.path_resolve(source_data_path, False)
            if isinstance(prop, bpy.types.bpy_prop_array):
                # Array Drivers
                d2 = try_add_array_driver(dst, source_data_path, d1.array_index)
            else:
                # Simple Drivers
                d2 = try_add_driver(dst, source_data_path)

            if isinstance(d2, bpy.types.FCurve):
                copy_fcurve_attr(d1, d2, print_fails)
                copy_driver_attr(d1.driver, d2.driver, print_fails)

                # Remove default modifiers, variables, etc.
                for m in d2.modifiers:
                    d2.modifiers.remove(m)
                for v in d2.driver.variables:
                    d2.driver.variables.remove(v)

                # Copy modifiers
                for m1 in d1.modifiers:
                    m2 = d2.modifiers.new(type=m1.type)
                    copy_modifier_attr(m1, m2, print_fails)

                # Copy variables
                for v1 in d1.driver.variables:
                    v2 = d2.driver.variables.new()
                    copy_drivervariable_attr(v1, v2, print_fails)
                    for i in range(len(v1.targets)):
                        copy_drivertarget_attr(v1.targets[i], v2.targets[i], print_fails)
                        # Switch self reference targets to new self
                        if v2.targets[i].id == src:
                            v2.targets[i].id = dst

                # Copy keyframes
                copy_fcurve = ProxyCopy_FCurve(d1)
                copy_fcurve.paste_data_on(d2)


class AnimationManagment():
    """
    Helper class for managing animation data in Blender.
    """

    def __init__(self):
        self.use_animation_data = False
        self.action = None
        self.action_slot = None
        self.action_extrapolation = "HOLD"
        self.action_blend_type = "REPLACE"
        self.action_influence = 1.0
        self.nla_tracks_save = None

    def save_animation_data(self, obj: bpy.types.Object):
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

            # Action was was added in Blender 4.4
            if bpy.app.version >= (4, 4, 0):
                self.action_slot = obj.animation_data.action_slot

            self.nla_tracks_save = NLA_Save(obj.animation_data.nla_tracks)
            self.use_animation_data = True
        else:
            self.use_animation_data = False

    def clear_animation_data(self, obj: bpy.types.Object):
        """
        Clears the animation data from the object.

        Args:
            obj (bpy.types.Object): The object to clear the animation data from.
        """
        obj.animation_data_clear()

    def set_animation_data(self, obj: bpy.types.Object, copy_nla=False):
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

            # Action was was added in Blender 4.4
            if bpy.app.version >= (4, 4, 0):
                # Cannot set slot without an assigned Action.
                if obj.animation_data.action: 
                    obj.animation_data.action_slot = self.action_slot

            obj.animation_data.action_extrapolation = self.action_extrapolation  # type: ignore
            obj.animation_data.action_blend_type = self.action_blend_type  # type: ignore
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

def reset_armature_pose(obj: bpy.types.Object):
    """
    Resets the pose of an armature object.

    Args:
        obj (bpy.types.Object): The armature object.

    Returns:
        None
    """
    for b in obj.pose.bones:
        b.rotation_quaternion = mathutils.Quaternion()
        b.rotation_euler = mathutils.Euler((0, 0, 0))
        b.scale = mathutils.Vector((1, 1, 1))
        b.location = mathutils.Vector((0, 0, 0))


class ProxyCopy_Constraint:
    """
    Proxy class for copying Blender PoseBoneConstraints.

    It is used to safely copy Blender PoseBoneConstraints.
    """

    def __init__(self, constraint: bpy.types.Constraint):
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
