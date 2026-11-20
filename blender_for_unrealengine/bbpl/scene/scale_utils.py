# SPDX-FileCopyrightText: Xavier Loux (BleuRaven)
#
# SPDX-License-Identifier: GPL-3.0-or-later

# ----------------------------------------------
#  BBPL -> BleuRaven Blender Python Library
#  https://github.com/xavier150/BBPL
# ----------------------------------------------

import math
from typing import Iterable, Iterator, Optional, TypeVar

import bpy


_DataT = TypeVar("_DataT")


def _validate_scale_factor(scale_factor: float) -> None:
    if not math.isfinite(scale_factor) or scale_factor <= 0:
        raise ValueError("scale_factor must be a finite positive number")


def _iter_filtered_items(
    items: Iterable[_DataT],
    white_list: Optional[Iterable[_DataT]],
    black_list: Optional[Iterable[_DataT]],
) -> Iterator[_DataT]:
    white_items = list(white_list or ())
    black_items = list(black_list or ())

    for item in items:
        if white_items and item not in white_items:
            continue
        if item in black_items:
            continue
        yield item


def scale_objects(
    scale_factor: float,
    use_location: bool = True,
    use_scale: bool = True,
    white_list: Optional[Iterable[bpy.types.Object]] = None,
    black_list: Optional[Iterable[bpy.types.Object]] = None,
) -> None:
    """Scale object location and/or scale; an empty whitelist means all non-black-listed objects."""
    _validate_scale_factor(scale_factor)

    for obj in _iter_filtered_items(bpy.data.objects, white_list, black_list):
        if use_location:
            obj.location *= scale_factor
        if use_scale:
            obj.scale *= scale_factor


def _iter_action_fcurves(action: bpy.types.Action) -> Iterator[bpy.types.FCurve]:
    if bpy.app.version >= (4, 4, 0):
        for slot in action.slots:
            found_channelbag = False
            for layer in action.layers:
                for strip in layer.strips:
                    if not isinstance(strip, bpy.types.ActionKeyframeStrip):
                        continue
                    channelbag = strip.channelbag(slot)
                    if channelbag:
                        yield from channelbag.fcurves
                        found_channelbag = True
                        break
                if found_channelbag:
                    break
    else:
        yield from action.fcurves  # type: ignore[attr-defined]


def _scale_location_fcurves(
    fcurves: Iterable[bpy.types.FCurve],
    scale_factor: float,
) -> None:
    for fcurve in fcurves:
        if (
            fcurve.data_path != "location"
            and fcurve.data_path.split(".")[-1] != "location"
        ):
            continue

        for key in fcurve.keyframe_points:
            key.co[1] *= scale_factor
            key.handle_left[1] *= scale_factor
            key.handle_right[1] *= scale_factor

        for modifier in fcurve.modifiers:
            if isinstance(modifier, bpy.types.FModifierNoise):
                modifier.strength *= scale_factor


def scale_animations(
    scale_factor: float,
    white_list: Optional[Iterable[bpy.types.Action]] = None,
    black_list: Optional[Iterable[bpy.types.Action]] = None,
) -> None:
    """Scale object and bone location curves in matching actions."""
    _validate_scale_factor(scale_factor)

    for action in _iter_filtered_items(bpy.data.actions, white_list, black_list):
        _scale_location_fcurves(
            _iter_action_fcurves(action),
            scale_factor,
        )


def _scale_shape_key_drivers(obj: bpy.types.Object, scale_factor: float) -> None:
    if not isinstance(obj.data, bpy.types.Mesh) or obj.data.shape_keys is None:
        return

    shape_keys = obj.data.shape_keys
    animation_data = shape_keys.animation_data
    if animation_data is None:
        return

    inverse_scale = 1 / scale_factor
    for driver_curve in animation_data.drivers:
        driver = driver_curve.driver
        if driver is None:
            continue

        is_location_dependent = False
        for variable in driver.variables:
            if variable.type == "TRANSFORMS":
                for target in variable.targets:
                    if "LOC" in target.transform_type:
                        is_location_dependent = True
            elif variable.type == "LOC_DIFF":
                is_location_dependent = True

        if not is_location_dependent:
            continue

        for key in driver_curve.keyframe_points:
            key.co[1] *= inverse_scale
            key.handle_left[1] *= inverse_scale
            key.handle_right[1] *= inverse_scale

        for modifier in driver_curve.modifiers:
            if isinstance(modifier, bpy.types.FModifierGenerator):
                modifier.coefficients[0] *= inverse_scale
                modifier.coefficients[1] *= inverse_scale


def _scale_armature_constraints(obj: bpy.types.Object, scale_factor: float) -> None:
    if not isinstance(obj.data, bpy.types.Armature) or obj.pose is None:
        return

    for bone in obj.pose.bones:
        for constraint in bone.constraints:
            if isinstance(constraint, bpy.types.StretchToConstraint):
                constraint.rest_length *= scale_factor
            elif isinstance(constraint, bpy.types.LimitLocationConstraint):
                constraint.min_x *= scale_factor
                constraint.min_y *= scale_factor
                constraint.min_z *= scale_factor
                constraint.max_x *= scale_factor
                constraint.max_y *= scale_factor
                constraint.max_z *= scale_factor
            elif isinstance(constraint, bpy.types.LimitDistanceConstraint):
                constraint.distance *= scale_factor


def _scale_curve_hooks(
    obj: bpy.types.Object,
    scale_factor: float,
) -> None:
    if not isinstance(obj.data, bpy.types.Curve):
        return

    for modifier in obj.modifiers:
        if not isinstance(modifier, bpy.types.HookModifier):
            continue

        inverse_matrix = modifier.matrix_inverse.copy()
        for axis in range(3):
            inverse_matrix[axis][3] *= scale_factor
        modifier.matrix_inverse = inverse_matrix

    inverse_scale = 1 / scale_factor
    for spline in obj.data.splines:
        for point in spline.bezier_points:
            point.radius *= inverse_scale


def scale_rigs_data(
    scale_factor: float,
    white_list: Optional[Iterable[bpy.types.Object]] = None,
    black_list: Optional[Iterable[bpy.types.Object]] = None,
    use_shape_key_drivers: bool = True,
    use_armature_constraint: bool = True,
    use_modifiers: bool = True,
    use_curve_hooks: bool = True,
) -> None:
    """Scale selected rig data categories without applying object transforms."""
    _validate_scale_factor(scale_factor)

    for obj in _iter_filtered_items(bpy.data.objects, white_list, black_list):
        if use_armature_constraint:
            _scale_armature_constraints(obj, scale_factor)
        if use_shape_key_drivers:
            _scale_shape_key_drivers(obj, scale_factor)
        if use_curve_hooks:
            _scale_curve_hooks(obj, scale_factor)

        if use_modifiers and isinstance(obj.data, bpy.types.Mesh):
            for modifier in obj.modifiers:
                if isinstance(modifier, bpy.types.MirrorModifier):
                    modifier.merge_threshold *= scale_factor
