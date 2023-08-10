# SPDX-License-Identifier: GPL-2.0-or-later

# Script copyright (C) Campbell Barton, Bastien Montagne


import math
import time
import re

from collections import namedtuple
from collections.abc import Iterable
from itertools import zip_longest, chain
import numpy as np

import bpy
import bpy_extras
from bpy.types import Object, Bone, PoseBone, DepsgraphObjectInstance
from mathutils import Vector, Matrix, Quaternion

from . import encode_bin, data_types


# "Constants"
FBX_VERSION = 7400
FBX_HEADER_VERSION = 1003
FBX_SCENEINFO_VERSION = 100
FBX_TEMPLATES_VERSION = 100

FBX_MODELS_VERSION = 232

FBX_GEOMETRY_VERSION = 124
# Revert back normals to 101 (simple 3D values) for now, 102 (4D + weights) seems not well supported by most apps
# currently, apart from some AD products.
FBX_GEOMETRY_NORMAL_VERSION = 101
FBX_GEOMETRY_BINORMAL_VERSION = 101
FBX_GEOMETRY_TANGENT_VERSION = 101
FBX_GEOMETRY_SMOOTHING_VERSION = 102
FBX_GEOMETRY_CREASE_VERSION = 101
FBX_GEOMETRY_VCOLOR_VERSION = 101
FBX_GEOMETRY_UV_VERSION = 101
FBX_GEOMETRY_MATERIAL_VERSION = 101
FBX_GEOMETRY_LAYER_VERSION = 100
FBX_GEOMETRY_SHAPE_VERSION = 100
FBX_DEFORMER_SHAPE_VERSION = 100
FBX_DEFORMER_SHAPECHANNEL_VERSION = 100
FBX_POSE_BIND_VERSION = 100
FBX_DEFORMER_SKIN_VERSION = 101
FBX_DEFORMER_CLUSTER_VERSION = 100
FBX_MATERIAL_VERSION = 102
FBX_TEXTURE_VERSION = 202
FBX_ANIM_KEY_VERSION = 4008

FBX_NAME_CLASS_SEP = b"\x00\x01"
FBX_ANIM_PROPSGROUP_NAME = "d"

FBX_KTIME = 46186158000  # This is the number of "ktimes" in one second (yep, precision over the nanosecond...)


MAT_CONVERT_LIGHT = Matrix.Rotation(math.pi / 2.0, 4, 'X')  # Blender is -Z, FBX is -Y.
MAT_CONVERT_CAMERA = Matrix.Rotation(math.pi / 2.0, 4, 'Y')  # Blender is -Z, FBX is +X.
# XXX I can't get this working :(
# MAT_CONVERT_BONE = Matrix.Rotation(math.pi / 2.0, 4, 'Z')  # Blender is +Y, FBX is -X.
MAT_CONVERT_BONE = Matrix()


BLENDER_OTHER_OBJECT_TYPES = {'CURVE', 'SURFACE', 'FONT', 'META'}
BLENDER_OBJECT_TYPES_MESHLIKE = {'MESH'} | BLENDER_OTHER_OBJECT_TYPES


# Lamps.
FBX_LIGHT_TYPES = {
    'POINT': 0,  # Point.
    'SUN': 1,    # Directional.
    'SPOT': 2,   # Spot.
    'HEMI': 1,   # Directional.
    'AREA': 3,   # Area.
}
FBX_LIGHT_DECAY_TYPES = {
    'CONSTANT': 0,                   # None.
    'INVERSE_LINEAR': 1,             # Linear.
    'INVERSE_SQUARE': 2,             # Quadratic.
    'INVERSE_COEFFICIENTS': 2,       # Quadratic...
    'CUSTOM_CURVE': 2,               # Quadratic.
    'LINEAR_QUADRATIC_WEIGHTED': 2,  # Quadratic.
}


RIGHT_HAND_AXES = {
    # Up, Forward -> FBX values (tuples of (axis, sign), Up, Front, Coord).
    ( 'X', '-Y'): ((0,  1), (1,  1), (2,  1)),
    ( 'X',  'Y'): ((0,  1), (1, -1), (2, -1)),
    ( 'X', '-Z'): ((0,  1), (2,  1), (1, -1)),
    ( 'X',  'Z'): ((0,  1), (2, -1), (1,  1)),
    ('-X', '-Y'): ((0, -1), (1,  1), (2, -1)),
    ('-X',  'Y'): ((0, -1), (1, -1), (2,  1)),
    ('-X', '-Z'): ((0, -1), (2,  1), (1,  1)),
    ('-X',  'Z'): ((0, -1), (2, -1), (1, -1)),
    ( 'Y', '-X'): ((1,  1), (0,  1), (2, -1)),
    ( 'Y',  'X'): ((1,  1), (0, -1), (2,  1)),
    ( 'Y', '-Z'): ((1,  1), (2,  1), (0,  1)),
    ( 'Y',  'Z'): ((1,  1), (2, -1), (0, -1)),
    ('-Y', '-X'): ((1, -1), (0,  1), (2,  1)),
    ('-Y',  'X'): ((1, -1), (0, -1), (2, -1)),
    ('-Y', '-Z'): ((1, -1), (2,  1), (0, -1)),
    ('-Y',  'Z'): ((1, -1), (2, -1), (0,  1)),
    ( 'Z', '-X'): ((2,  1), (0,  1), (1,  1)),
    ( 'Z',  'X'): ((2,  1), (0, -1), (1, -1)),
    ( 'Z', '-Y'): ((2,  1), (1,  1), (0, -1)),
    ( 'Z',  'Y'): ((2,  1), (1, -1), (0,  1)),  # Blender system!
    ('-Z', '-X'): ((2, -1), (0,  1), (1, -1)),
    ('-Z',  'X'): ((2, -1), (0, -1), (1,  1)),
    ('-Z', '-Y'): ((2, -1), (1,  1), (0,  1)),
    ('-Z',  'Y'): ((2, -1), (1, -1), (0, -1)),
}


# NOTE: Not fully in enum value order, since when exporting the first entry matching the framerate value is used
# (e.g. better have NTSC fullframe than NTSC drop frame for 29.97 framerate).
FBX_FRAMERATES = (
    #(-1.0, 0),  # Default framerate.
    (-1.0, 14),  # Custom framerate.
    (120.0, 1),
    (100.0, 2),
    (60.0, 3),
    (50.0, 4),
    (48.0, 5),
    (30.0, 6),  # BW NTSC, full frame.
    (30.0, 7),  # Drop frame.
    (30.0 / 1.001, 9),  # Color NTSC, full frame.
    (30.0 / 1.001, 8),  # Color NTSC, drop frame.
    (25.0, 10),
    (24.0, 11),
    #(1.0, 12),  # 1000 milli/s (use for date time?).
    (24.0 / 1.001, 13),
    (96.0, 15),
    (72.0, 16),
    (60.0 / 1.001, 17),
    (120.0 / 1.001, 18),
)


# ##### Misc utilities #####

# Enable performance reports (measuring time used to perform various steps of importing or exporting).
DO_PERFMON = False

if DO_PERFMON:
    class PerfMon():
        def __init__(self):
            self.level = -1
            self.ref_time = []

        def level_up(self, message=""):
            self.level += 1
            self.ref_time.append(None)
            if message:
                print("\t" * self.level, message, sep="")

        def level_down(self, message=""):
            if not self.ref_time:
                if message:
                    print(message)
                return
            ref_time = self.ref_time[self.level]
            print("\t" * self.level,
                  "\tDone (%f sec)\n" % ((time.process_time() - ref_time) if ref_time is not None else 0.0),
                  sep="")
            if message:
                print("\t" * self.level, message, sep="")
            del self.ref_time[self.level]
            self.level -= 1

        def step(self, message=""):
            ref_time = self.ref_time[self.level]
            curr_time = time.process_time()
            if ref_time is not None:
                print("\t" * self.level, "\tDone (%f sec)\n" % (curr_time - ref_time), sep="")
            self.ref_time[self.level] = curr_time
            print("\t" * self.level, message, sep="")
else:
    class PerfMon():
        def __init__(self):
            pass

        def level_up(self, message=""):
            pass

        def level_down(self, message=""):
            pass

        def step(self, message=""):
            pass


# Scale/unit mess. FBX can store the 'reference' unit of a file in its UnitScaleFactor property
# (1.0 meaning centimeter, afaik). We use that to reflect user's default unit as set in Blender with scale_length.
# However, we always get values in BU (i.e. meters), so we have to reverse-apply that scale in global matrix...
# Note that when no default unit is available, we assume 'meters' (and hence scale by 100).
def units_blender_to_fbx_factor(scene):
    return 100.0 if (scene.unit_settings.system == 'NONE') else (100.0 * scene.unit_settings.scale_length)


# Note: this could be in a utility (math.units e.g.)...

UNITS = {
    "meter": 1.0,  # Ref unit!
    "kilometer": 0.001,
    "millimeter": 1000.0,
    "foot": 1.0 / 0.3048,
    "inch": 1.0 / 0.0254,
    "turn": 1.0,  # Ref unit!
    "degree": 360.0,
    "radian": math.pi * 2.0,
    "second": 1.0,  # Ref unit!
    "ktime": FBX_KTIME,
}


def units_convertor(u_from, u_to):
    """Return a convertor between specified units."""
    conv = UNITS[u_to] / UNITS[u_from]
    return lambda v: v * conv


def units_convertor_iter(u_from, u_to):
    """Return an iterable convertor between specified units."""
    conv = units_convertor(u_from, u_to)

    def convertor(it):
        for v in it:
            yield(conv(v))

    return convertor


def matrix4_to_array(mat):
    """Concatenate matrix's columns into a single, flat tuple"""
    # blender matrix is row major, fbx is col major so transpose on write
    return tuple(f for v in mat.transposed() for f in v)


def array_to_matrix4(arr):
    """Convert a single 16-len tuple into a valid 4D Blender matrix"""
    # Blender matrix is row major, fbx is col major so transpose on read
    return Matrix(tuple(zip(*[iter(arr)]*4))).transposed()


def parray_as_ndarray(arr):
    """Convert an array.array into an np.ndarray that shares the same memory"""
    return np.frombuffer(arr, dtype=arr.typecode)


def similar_values(v1, v2, e=1e-6):
    """Return True if v1 and v2 are nearly the same."""
    if v1 == v2:
        return True
    return ((abs(v1 - v2) / max(abs(v1), abs(v2))) <= e)


def similar_values_iter(v1, v2, e=1e-6):
    """Return True if iterables v1 and v2 are nearly the same."""
    if v1 == v2:
        return True
    for v1, v2 in zip(v1, v2):
        if (v1 != v2) and ((abs(v1 - v2) / max(abs(v1), abs(v2))) > e):
            return False
    return True


def shape_difference_exclude_similar(sv_cos, ref_cos, e=1e-6):
    """Return a tuple of:
        the difference between the vertex cos in sv_cos and ref_cos, excluding any that are nearly the same,
        and the indices of the vertices that are not nearly the same"""
    assert(sv_cos.size == ref_cos.size)

    # Create views of 1 co per row of the arrays, only making copies if needed.
    sv_cos = sv_cos.reshape(-1, 3)
    ref_cos = ref_cos.reshape(-1, 3)

    # Quick check for equality
    if np.array_equal(sv_cos, ref_cos):
        # There's no difference between the two arrays.
        empty_cos = np.empty((0, 3), dtype=sv_cos.dtype)
        empty_indices = np.empty(0, dtype=np.int32)
        return empty_cos, empty_indices

    # Note that unlike math.isclose(a,b), np.isclose(a,b) is not symmetrical and the second argument 'b', is
    # considered to be the reference value.
    # Note that atol=0 will mean that if only one co component being compared is zero, they won't be considered close.
    similar_mask = np.isclose(sv_cos, ref_cos, atol=0, rtol=e)

    # A co is only similar if every component in it is similar.
    co_similar_mask = np.all(similar_mask, axis=1)

    # Get the indices of cos that are not similar.
    not_similar_verts_idx = np.flatnonzero(~co_similar_mask)

    # Subtracting first over the entire arrays and then indexing seems faster than indexing both arrays first and then
    # subtracting, until less than about 3% of the cos are being indexed.
    difference_cos = (sv_cos - ref_cos)[not_similar_verts_idx]
    return difference_cos, not_similar_verts_idx


def _mat4_vec3_array_multiply(mat4, vec3_array, dtype=None, return_4d=False):
    """Multiply a 4d matrix by each 3d vector in an array and return as an array of either 3d or 4d vectors.

    A view of the input array is returned if return_4d=False, the dtype matches the input array and either the matrix is
    None or, ignoring the last row, is a 3x3 identity matrix with no translation:
    ┌1, 0, 0, 0┐
    │0, 1, 0, 0│
    └0, 0, 1, 0┘

    When dtype=None, it defaults to the dtype of the input array."""
    return_dtype = dtype if dtype is not None else vec3_array.dtype
    vec3_array = vec3_array.reshape(-1, 3)

    # Multiplying a 4d mathutils.Matrix by a 3d mathutils.Vector implicitly extends the Vector to 4d during the
    # calculation by appending 1.0 to the Vector and then the 4d result is truncated back to 3d.
    # Numpy does not do an implicit extension to 4d, so it would have to be done explicitly by extending the entire
    # vec3_array to 4d.
    # However, since the w component of the vectors is always 1.0, the last column can be excluded from the
    # multiplication and then added to every multiplied vector afterwards, which avoids having to make a 4d copy of
    # vec3_array beforehand.
    # For a single column vector:
    # ┌a, b, c, d┐   ┌x┐   ┌ax+by+cz+d┐
    # │e, f, g, h│ @ │y│ = │ex+fy+gz+h│
    # │i, j, k, l│   │z│   │ix+jy+kz+l│
    # └m, n, o, p┘   └1┘   └mx+ny+oz+p┘
    # ┌a, b, c┐   ┌x┐   ┌d┐   ┌ax+by+cz┐   ┌d┐   ┌ax+by+cz+d┐
    # │e, f, g│ @ │y│ + │h│ = │ex+fy+gz│ + │h│ = │ex+fy+gz+h│
    # │i, j, k│   └z┘   │l│   │ix+jy+kz│   │l│   │ix+jy+kz+l│
    # └m, n, o┘         └p┘   └mx+ny+oz┘   └p┘   └mx+ny+oz+p┘

    # column_vector_multiplication in mathutils_Vector.c uses double precision math for Matrix @ Vector by casting the
    # matrix's values to double precision and then casts back to single precision when returning the result, so at least
    # double precision math is always be used to match standard Blender behaviour.
    math_precision = np.result_type(np.double, vec3_array)

    to_multiply = None
    to_add = None
    w_to_set = 1.0
    if mat4 is not None:
        mat_np = np.array(mat4, dtype=math_precision)
        # Identity matrix is compared against to check if any matrix multiplication is required.
        identity = np.identity(4, dtype=math_precision)
        if not return_4d:
            # If returning 3d, the entire last row of the matrix can be ignored because it only affects the w component.
            mat_np = mat_np[:3]
            identity = identity[:3]

        # Split mat_np into the columns to multiply and the column to add afterwards.
        # First 3 columns
        multiply_columns = mat_np[:, :3]
        multiply_identity = identity[:, :3]
        # Last column only
        add_column = mat_np.T[3]

        # Analyze the split parts of the matrix to figure out if there is anything to multiply and anything to add.
        if not np.array_equal(multiply_columns, multiply_identity):
            to_multiply = multiply_columns

        if return_4d and to_multiply is None:
            # When there's nothing to multiply, the w component of add_column can be set directly into the array because
            # mx+ny+oz+p becomes 0x+0y+0z+p where p is add_column[3].
            w_to_set = add_column[3]
            # Replace add_column with a view of only the translation.
            add_column = add_column[:3]

        if add_column.any():
            to_add = add_column

    if to_multiply is None:
        # If there's anything to add, ensure it's added using the precision being used for math.
        array_dtype = math_precision if to_add is not None else return_dtype
        if return_4d:
            multiplied_vectors = np.empty((len(vec3_array), 4), dtype=array_dtype)
            multiplied_vectors[:, :3] = vec3_array
            multiplied_vectors[:, 3] = w_to_set
        else:
            # If there's anything to add, ensure a copy is made so that the input vec3_array isn't modified.
            multiplied_vectors = vec3_array.astype(array_dtype, copy=to_add is not None)
    else:
        # Matrix multiplication has the signature (n,k) @ (k,m) -> (n,m).
        # Where v is the number of vectors in vec3_array and d is the number of vector dimensions to return:
        # to_multiply has shape (d,3), vec3_array has shape (v,3) and the result should have shape (v,d).
        # Either vec3_array or to_multiply must be transposed:
        # Can transpose vec3_array and then transpose the result:
        # (v,3).T -> (3,v); (d,3) @ (3,v) -> (d,v); (d,v).T -> (v,d)
        # Or transpose to_multiply and swap the order of multiplication:
        # (d,3).T -> (3,d); (v,3) @ (3,d) -> (v,d)
        # There's no, or negligible, performance difference between the two options, however, the result of the latter
        # will be C contiguous in memory, making it faster to convert to flattened bytes with .tobytes().
        multiplied_vectors = vec3_array @ to_multiply.T

    if to_add is not None:
        for axis, to_add_to_axis in zip(multiplied_vectors.T, to_add):
            if to_add_to_axis != 0:
                axis += to_add_to_axis

    # Cast to the desired return type before returning.
    return multiplied_vectors.astype(return_dtype, copy=False)


def vcos_transformed(raw_cos, m=None, dtype=None):
    return _mat4_vec3_array_multiply(m, raw_cos, dtype)


def nors_transformed(raw_nors, m=None, dtype=None):
    # Great, now normals are also expected 4D!
    # XXX Back to 3D normals for now!
    # return _mat4_vec3_array_multiply(m, raw_nors, dtype, return_4d=True)
    return _mat4_vec3_array_multiply(m, raw_nors, dtype)


def astype_view_signedness(arr, new_dtype):
    """Unsafely views arr as new_dtype if the itemsize and byteorder of arr matches but the signedness does not,
    otherwise calls np.ndarray.astype with copy=False.

    The benefit of copy=False is that if the array can be safely viewed as the new type, then a view is made, instead of
    a copy with the new type.

    Unsigned types can't be viewed safely as signed or vice-versa, meaning that a copy would always be made by
    .astype(..., copy=False).

    This is intended for viewing uintc data (a common Blender C type with variable itemsize, though usually 4 bytes, so
    uint32) as int32 (a common FBX type), when the itemsizes match."""
    arr_dtype = arr.dtype

    if not isinstance(new_dtype, np.dtype):
        # new_dtype could be a type instance or a string, but it needs to be a dtype to compare its itemsize, byteorder
        # and kind.
        new_dtype = np.dtype(new_dtype)

    # For simplicity, only dtypes of the same itemsize and byteorder, but opposite signedness, are handled. Everything
    # else is left to .astype.
    arr_kind = arr_dtype.kind
    new_kind = new_dtype.kind
    if (
        # Signed and unsigned int are opposite in terms of signedness. Other types don't have signedness.
        ((arr_kind == 'i' and new_kind == 'u') or (arr_kind == 'u' and new_kind == 'i'))
        and arr_dtype.itemsize == new_dtype.itemsize
        and arr_dtype.byteorder == new_dtype.byteorder
    ):
        # new_dtype has opposite signedness and matching itemsize and byteorder, so return a view of the new type.
        return arr.view(new_dtype)
    else:
        return arr.astype(new_dtype, copy=False)


def fast_first_axis_flat(ar):
    """Get a flat view (or a copy if a view is not possible) of the input array whereby each element is a single element
    of a dtype that is fast to sort, sorts according to individual bytes and contains the data for an entire row (and
    any further dimensions) of the input array.

    Since the dtype of the view could sort in a different order to the dtype of the input array, this isn't typically
    useful for actual sorting, but it is useful for sorting-based uniqueness, such as np.unique."""
    # If there are no rows, each element will be viewed as the new dtype.
    elements_per_row = math.prod(ar.shape[1:])
    row_itemsize = ar.itemsize * elements_per_row

    # Get a dtype with itemsize that equals row_itemsize.
    # Integer types sort the fastest, but are only available for specific itemsizes.
    uint_dtypes_by_itemsize = {1: np.uint8, 2: np.uint16, 4: np.uint32, 8: np.uint64}
    # Signed/unsigned makes no noticeable speed difference, but using unsigned will result in ordering according to
    # individual bytes like the other, non-integer types.
    if row_itemsize in uint_dtypes_by_itemsize:
        entire_row_dtype = uint_dtypes_by_itemsize[row_itemsize]
    else:
        # When using kind='stable' sorting, numpy only uses radix sort with integer types, but it's still
        # significantly faster to sort by a single item per row instead of multiple row elements or multiple structured
        # type fields.
        # Construct a flexible size dtype with matching itemsize.
        # Should always be 4 because each character in a unicode string is UCS4.
        str_itemsize = np.dtype((np.str_, 1)).itemsize
        if row_itemsize % str_itemsize == 0:
            # Unicode strings seem to be slightly faster to sort than bytes.
            entire_row_dtype = np.dtype((np.str_, row_itemsize // str_itemsize))
        else:
            # Bytes seem to be slightly faster to sort than raw bytes (np.void).
            entire_row_dtype = np.dtype((np.bytes_, row_itemsize))

    # View each element along the first axis as a single element.
    # View (or copy if a view is not possible) as flat
    ar = ar.reshape(-1)
    # To view as a dtype of different size, the last axis (entire array in NumPy 1.22 and earlier) must be C-contiguous.
    if row_itemsize != ar.itemsize and not ar.flags.c_contiguous:
        ar = np.ascontiguousarray(ar)
    return ar.view(entire_row_dtype)


def fast_first_axis_unique(ar, return_unique=True, return_index=False, return_inverse=False, return_counts=False):
    """np.unique with axis=0 but optimised for when the input array has multiple elements per row, and the returned
    unique array doesn't need to be sorted.

    Arrays with more than one element per row are more costly to sort in np.unique due to being compared one
    row-element at a time, like comparing tuples.

    By viewing each entire row as a single non-structured element, much faster sorting can be achieved. Since the values
    are viewed as a different type to their original, this means that the returned array of unique values may not be
    sorted according to their original type.

    The array of unique values can be excluded from the returned tuple by specifying return_unique=False.

    Float type caveats:
    All elements of -0.0 in the input array will be replaced with 0.0 to ensure that both values are collapsed into one.
    NaN values can have lots of different byte representations (e.g. signalling/quiet and custom payloads). Only the
    duplicates of each unique byte representation will be collapsed into one."""
    # At least something should always be returned.
    assert(return_unique or return_index or return_inverse or return_counts)
    # Only signed integer, unsigned integer and floating-point kinds of data are allowed. Other kinds of data have not
    # been tested.
    assert(ar.dtype.kind in "iuf")

    # Floating-point types have different byte representations for -0.0 and 0.0. Collapse them together by replacing all
    # -0.0 in the input array with 0.0.
    if ar.dtype.kind == 'f':
        ar[ar == -0.0] = 0.0

    # It's a bit annoying that the unique array is always calculated even when it might not be needed, but it is
    # generally insignificant compared to the cost of sorting.
    result = np.unique(fast_first_axis_flat(ar), return_index=return_index,
                       return_inverse=return_inverse, return_counts=return_counts)

    if return_unique:
        unique = result[0] if isinstance(result, tuple) else result
        # View in the original dtype.
        unique = unique.view(ar.dtype)
        # Return the same number of elements per row and any extra dimensions per row as the input array.
        unique.shape = (-1, *ar.shape[1:])
        if isinstance(result, tuple):
            return (unique,) + result[1:]
        else:
            return unique
    else:
        # Remove the first element, the unique array.
        result = result[1:]
        if len(result) == 1:
            # Unpack single element tuples.
            return result[0]
        else:
            return result


def ensure_object_not_in_edit_mode(context, obj):
    """Objects in Edit mode usually cannot be exported because much of the API used when exporting is not available for
    Objects in Edit mode.

    Exiting the currently active Object (and any other Objects opened in multi-editing) from Edit mode is simple and
    should be done with `bpy.ops.mesh.mode_set(mode='OBJECT')` instead of using this function.

    This function is for the rare case where an Object is in Edit mode, but the current context mode is not Edit mode.
    This can occur from a state where the current context mode is Edit mode, but then the active Object of the current
    View Layer is changed to a different Object that is not in Edit mode. This changes the current context mode, but
    leaves the other Object(s) in Edit mode.
    """
    if obj.mode != 'EDIT':
        return True

    # Get the active View Layer.
    view_layer = context.view_layer

    # A View Layer belongs to a scene.
    scene = view_layer.id_data

    # Get the current active Object of this View Layer, so we can restore it once done.
    orig_active = view_layer.objects.active

    # Check if obj is in the View Layer. If obj is not in the View Layer, it cannot be set as the active Object.
    # We don't use `obj.name in view_layer.objects` because an Object from a Library could have the same name.
    is_in_view_layer = any(o == obj for o in view_layer.objects)

    do_unlink_from_scene_collection = False
    try:
        if not is_in_view_layer:
            # There might not be any enabled collections in the View Layer, so link obj into the Scene Collection
            # instead, which is always available to all View Layers of that Scene.
            scene.collection.objects.link(obj)
            do_unlink_from_scene_collection = True
        view_layer.objects.active = obj

        # Now we're finally ready to attempt to change obj's mode.
        if bpy.ops.object.mode_set.poll():
            bpy.ops.object.mode_set(mode='OBJECT')
        if obj.mode == 'EDIT':
            # The Object could not be set out of EDIT mode and therefore cannot be exported.
            return False
    finally:
        # Always restore the original active Object and unlink obj from the Scene Collection if it had to be linked.
        view_layer.objects.active = orig_active
        if do_unlink_from_scene_collection:
            scene.collection.objects.unlink(obj)

    return True


# ##### UIDs code. #####

# ID class (mere int).
class UUID(int):
    pass


# UIDs storage.
_keys_to_uuids = {}
_uuids_to_keys = {}


def _key_to_uuid(uuids, key):
    # TODO: Check this is robust enough for our needs!
    # Note: We assume we have already checked the related key wasn't yet in _keys_to_uids!
    #       As int64 is signed in FBX, we keep uids below 2**63...
    if isinstance(key, int) and 0 <= key < 2**63:
        # We can use value directly as id!
        uuid = key
    else:
        uuid = hash(key)
        if uuid < 0:
            uuid = -uuid
        if uuid >= 2**63:
            uuid //= 2
    # Try to make our uid shorter!
    if uuid > int(1e9):
        t_uuid = uuid % int(1e9)
        if t_uuid not in uuids:
            uuid = t_uuid
    # Make sure our uuid *is* unique.
    if uuid in uuids:
        inc = 1 if uuid < 2**62 else -1
        while uuid in uuids:
            uuid += inc
            if 0 > uuid >= 2**63:
                # Note that this is more that unlikely, but does not harm anyway...
                raise ValueError("Unable to generate an UUID for key {}".format(key))
    return UUID(uuid)


def get_fbx_uuid_from_key(key):
    """
    Return an UUID for given key, which is assumed to be hashable.
    """
    uuid = _keys_to_uuids.get(key, None)
    if uuid is None:
        uuid = _key_to_uuid(_uuids_to_keys, key)
        _keys_to_uuids[key] = uuid
        _uuids_to_keys[uuid] = key
    return uuid


# XXX Not sure we'll actually need this one?
def get_key_from_fbx_uuid(uuid):
    """
    Return the key which generated this uid.
    """
    assert(uuid.__class__ == UUID)
    return _uuids_to_keys.get(uuid, None)


# Blender-specific key generators
def get_bid_name(bid):
    library = getattr(bid, "library", None)
    if library is not None:
        return "%s_L_%s" % (bid.name, library.name)
    else:
        return bid.name


def get_blenderID_key(bid):
    if isinstance(bid, Iterable):
        return "|".join("B" + e.rna_type.name + "#" + get_bid_name(e) for e in bid)
    else:
        return "B" + bid.rna_type.name + "#" + get_bid_name(bid)


def get_blenderID_name(bid):
    if isinstance(bid, Iterable):
        return "|".join(get_bid_name(e) for e in bid)
    else:
        return get_bid_name(bid)


def get_blender_empty_key(obj):
    """Return bone's keys (Model and NodeAttribute)."""
    return "|".join((get_blenderID_key(obj), "Empty"))


def get_blender_mesh_shape_key(me):
    """Return main shape deformer's key."""
    return "|".join((get_blenderID_key(me), "Shape"))


def get_blender_mesh_shape_channel_key(me, shape):
    """Return shape channel and geometry shape keys."""
    return ("|".join((get_blenderID_key(me), "Shape", get_blenderID_key(shape))),
            "|".join((get_blenderID_key(me), "Geometry", get_blenderID_key(shape))))


def get_blender_bone_key(armature, bone):
    """Return bone's keys (Model and NodeAttribute)."""
    return "|".join((get_blenderID_key((armature, bone)), "Data"))


def get_blender_bindpose_key(obj, mesh):
    """Return object's bindpose key."""
    return "|".join((get_blenderID_key(obj), get_blenderID_key(mesh), "BindPose"))


def get_blender_armature_skin_key(armature, mesh):
    """Return armature's skin key."""
    return "|".join((get_blenderID_key(armature), get_blenderID_key(mesh), "DeformerSkin"))


def get_blender_bone_cluster_key(armature, mesh, bone):
    """Return bone's cluster key."""
    return "|".join((get_blenderID_key(armature), get_blenderID_key(mesh),
                     get_blenderID_key(bone), "SubDeformerCluster"))


def get_blender_anim_id_base(scene, ref_id):
    if ref_id is not None:
        return get_blenderID_key(scene) + "|" + get_blenderID_key(ref_id)
    else:
        return get_blenderID_key(scene)


def get_blender_anim_stack_key(scene, ref_id):
    """Return single anim stack key."""
    return get_blender_anim_id_base(scene, ref_id) + "|AnimStack"


def get_blender_anim_layer_key(scene, ref_id):
    """Return ID's anim layer key."""
    return get_blender_anim_id_base(scene, ref_id) + "|AnimLayer"


def get_blender_anim_curve_node_key(scene, ref_id, obj_key, fbx_prop_name):
    """Return (stack/layer, ID, fbxprop) curve node key."""
    return "|".join((get_blender_anim_id_base(scene, ref_id), obj_key, fbx_prop_name, "AnimCurveNode"))


def get_blender_anim_curve_key(scene, ref_id, obj_key, fbx_prop_name, fbx_prop_item_name):
    """Return (stack/layer, ID, fbxprop, item) curve key."""
    return "|".join((get_blender_anim_id_base(scene, ref_id), obj_key, fbx_prop_name,
                     fbx_prop_item_name, "AnimCurve"))


def get_blender_nodetexture_key(ma, socket_names):
    return "|".join((get_blenderID_key(ma), *socket_names))


# ##### Element generators. #####

# Note: elem may be None, in this case the element is not added to any parent.
def elem_empty(elem, name):
    sub_elem = encode_bin.FBXElem(name)
    if elem is not None:
        elem.elems.append(sub_elem)
    return sub_elem


def _elem_data_single(elem, name, value, func_name):
    sub_elem = elem_empty(elem, name)
    getattr(sub_elem, func_name)(value)
    return sub_elem


def _elem_data_vec(elem, name, value, func_name):
    sub_elem = elem_empty(elem, name)
    func = getattr(sub_elem, func_name)
    for v in value:
        func(v)
    return sub_elem


def elem_data_single_bool(elem, name, value):
    return _elem_data_single(elem, name, value, "add_bool")


def elem_data_single_int8(elem, name, value):
    return _elem_data_single(elem, name, value, "add_int8")


def elem_data_single_int16(elem, name, value):
    return _elem_data_single(elem, name, value, "add_int16")


def elem_data_single_int32(elem, name, value):
    return _elem_data_single(elem, name, value, "add_int32")


def elem_data_single_int64(elem, name, value):
    return _elem_data_single(elem, name, value, "add_int64")


def elem_data_single_float32(elem, name, value):
    return _elem_data_single(elem, name, value, "add_float32")


def elem_data_single_float64(elem, name, value):
    return _elem_data_single(elem, name, value, "add_float64")


def elem_data_single_bytes(elem, name, value):
    return _elem_data_single(elem, name, value, "add_bytes")


def elem_data_single_string(elem, name, value):
    return _elem_data_single(elem, name, value, "add_string")


def elem_data_single_string_unicode(elem, name, value):
    return _elem_data_single(elem, name, value, "add_string_unicode")


def elem_data_single_bool_array(elem, name, value):
    return _elem_data_single(elem, name, value, "add_bool_array")


def elem_data_single_int32_array(elem, name, value):
    return _elem_data_single(elem, name, value, "add_int32_array")


def elem_data_single_int64_array(elem, name, value):
    return _elem_data_single(elem, name, value, "add_int64_array")


def elem_data_single_float32_array(elem, name, value):
    return _elem_data_single(elem, name, value, "add_float32_array")


def elem_data_single_float64_array(elem, name, value):
    return _elem_data_single(elem, name, value, "add_float64_array")


def elem_data_single_byte_array(elem, name, value):
    return _elem_data_single(elem, name, value, "add_byte_array")


def elem_data_vec_float64(elem, name, value):
    return _elem_data_vec(elem, name, value, "add_float64")


# ##### Generators for standard FBXProperties70 properties. #####

def elem_properties(elem):
    return elem_empty(elem, b"Properties70")


# Properties definitions, format: (b"type_1", b"label(???)", "name_set_value_1", "name_set_value_2", ...)
# XXX Looks like there can be various variations of formats here... Will have to be checked ultimately!
#     Also, those "custom" types like 'FieldOfView' or 'Lcl Translation' are pure nonsense,
#     these are just Vector3D ultimately... *sigh* (again).
FBX_PROPERTIES_DEFINITIONS = {
    # Generic types.
    "p_bool": (b"bool", b"", "add_int32"),  # Yes, int32 for a bool (and they do have a core bool type)!!!
    "p_integer": (b"int", b"Integer", "add_int32"),
    "p_ulonglong": (b"ULongLong", b"", "add_int64"),
    "p_double": (b"double", b"Number", "add_float64"),  # Non-animatable?
    "p_number": (b"Number", b"", "add_float64"),  # Animatable-only?
    "p_enum": (b"enum", b"", "add_int32"),
    "p_vector_3d": (b"Vector3D", b"Vector", "add_float64", "add_float64", "add_float64"),  # Non-animatable?
    "p_vector": (b"Vector", b"", "add_float64", "add_float64", "add_float64"),  # Animatable-only?
    "p_color_rgb": (b"ColorRGB", b"Color", "add_float64", "add_float64", "add_float64"),  # Non-animatable?
    "p_color": (b"Color", b"", "add_float64", "add_float64", "add_float64"),  # Animatable-only?
    "p_string": (b"KString", b"", "add_string_unicode"),
    "p_string_url": (b"KString", b"Url", "add_string_unicode"),
    "p_timestamp": (b"KTime", b"Time", "add_int64"),
    "p_datetime": (b"DateTime", b"", "add_string_unicode"),
    # Special types.
    "p_object": (b"object", b""),  # XXX Check this! No value for this prop??? Would really like to know how it works!
    "p_compound": (b"Compound", b""),
    # Specific types (sic).
    # ## Objects (Models).
    "p_lcl_translation": (b"Lcl Translation", b"", "add_float64", "add_float64", "add_float64"),
    "p_lcl_rotation": (b"Lcl Rotation", b"", "add_float64", "add_float64", "add_float64"),
    "p_lcl_scaling": (b"Lcl Scaling", b"", "add_float64", "add_float64", "add_float64"),
    "p_visibility": (b"Visibility", b"", "add_float64"),
    "p_visibility_inheritance": (b"Visibility Inheritance", b"", "add_int32"),
    # ## Cameras!!!
    "p_roll": (b"Roll", b"", "add_float64"),
    "p_opticalcenterx": (b"OpticalCenterX", b"", "add_float64"),
    "p_opticalcentery": (b"OpticalCenterY", b"", "add_float64"),
    "p_fov": (b"FieldOfView", b"", "add_float64"),
    "p_fov_x": (b"FieldOfViewX", b"", "add_float64"),
    "p_fov_y": (b"FieldOfViewY", b"", "add_float64"),
}


def _elem_props_set(elem, ptype, name, value, flags):
    p = elem_data_single_string(elem, b"P", name)
    for t in ptype[:2]:
        p.add_string(t)
    p.add_string(flags)
    if len(ptype) == 3:
        getattr(p, ptype[2])(value)
    elif len(ptype) > 3:
        # We assume value is iterable, else it's a bug!
        for callback, val in zip(ptype[2:], value):
            getattr(p, callback)(val)


def _elem_props_flags(animatable, animated, custom):
    # XXX: There are way more flags, see
    #      http://help.autodesk.com/view/FBX/2015/ENU/?guid=__cpp_ref_class_fbx_property_flags_html
    #      Unfortunately, as usual, no doc at all about their 'translation' in actual FBX file format.
    #      Curse you-know-who.
    if animatable:
        if animated:
            if custom:
                return b"A+U"
            return b"A+"
        if custom:
            # Seems that customprops always need those 'flags', see T69554. Go figure...
            return b"A+U"
        return b"A"
    if custom:
        # Seems that customprops always need those 'flags', see T69554. Go figure...
        return b"A+U"
    return b""


def elem_props_set(elem, ptype, name, value=None, animatable=False, animated=False, custom=False):
    ptype = FBX_PROPERTIES_DEFINITIONS[ptype]
    _elem_props_set(elem, ptype, name, value, _elem_props_flags(animatable, animated, custom))


def elem_props_compound(elem, cmpd_name, custom=False):
    def _setter(ptype, name, value, animatable=False, animated=False, custom=False):
        name = cmpd_name + b"|" + name
        elem_props_set(elem, ptype, name, value, animatable=animatable, animated=animated, custom=custom)

    elem_props_set(elem, "p_compound", cmpd_name, custom=custom)
    return _setter


def elem_props_template_init(templates, template_type):
    """
    Init a writing template of given type, for *one* element's properties.
    """
    ret = {}
    tmpl = templates.get(template_type)
    if tmpl is not None:
        written = tmpl.written[0]
        props = tmpl.properties
        ret = {name: [val, ptype, anim, written] for name, (val, ptype, anim) in props.items()}
    return ret


def elem_props_template_set(template, elem, ptype_name, name, value, animatable=False, animated=False):
    """
    Only add a prop if the same value is not already defined in given template.
    Note it is important to not give iterators as value, here!
    """
    ptype = FBX_PROPERTIES_DEFINITIONS[ptype_name]
    if len(ptype) > 3:
        value = tuple(value)
    tmpl_val, tmpl_ptype, tmpl_animatable, tmpl_written = template.get(name, (None, None, False, False))
    # Note animatable flag from template takes precedence over given one, if applicable.
    # However, animated properties are always written, since they cannot match their template!
    if tmpl_ptype is not None and not animated:
        if (tmpl_written and
            ((len(ptype) == 3 and (tmpl_val, tmpl_ptype) == (value, ptype_name)) or
             (len(ptype) > 3 and (tuple(tmpl_val), tmpl_ptype) == (value, ptype_name)))):
            return  # Already in template and same value.
        _elem_props_set(elem, ptype, name, value, _elem_props_flags(tmpl_animatable, animated, False))
        template[name][3] = True
    else:
        _elem_props_set(elem, ptype, name, value, _elem_props_flags(animatable, animated, False))


def elem_props_template_finalize(template, elem):
    """
    Finalize one element's template/props.
    Issue is, some templates might be "needed" by different types (e.g. NodeAttribute is for lights, cameras, etc.),
    but values for only *one* subtype can be written as template. So we have to be sure we write those for the other
    subtypes in each and every elements, if they are not overridden by that element.
    Yes, hairy, FBX that is to say. When they could easily support several subtypes per template... :(
    """
    for name, (value, ptype_name, animatable, written) in template.items():
        if written:
            continue
        ptype = FBX_PROPERTIES_DEFINITIONS[ptype_name]
        _elem_props_set(elem, ptype, name, value, _elem_props_flags(animatable, False, False))


# ##### Templates #####
# TODO: check all those "default" values, they should match Blender's default as much as possible, I guess?

FBXTemplate = namedtuple("FBXTemplate", ("type_name", "prop_type_name", "properties", "nbr_users", "written"))


def fbx_templates_generate(root, fbx_templates):
    # We may have to gather different templates in the same node (e.g. NodeAttribute template gathers properties
    # for Lights, Cameras, LibNodes, etc.).
    ref_templates = {(tmpl.type_name, tmpl.prop_type_name): tmpl for tmpl in fbx_templates.values()}

    templates = {}
    for type_name, prop_type_name, properties, nbr_users, _written in fbx_templates.values():
        tmpl = templates.setdefault(type_name, [{}, 0])
        tmpl[0][prop_type_name] = (properties, nbr_users)
        tmpl[1] += nbr_users

    for type_name, (subprops, nbr_users) in templates.items():
        template = elem_data_single_string(root, b"ObjectType", type_name)
        elem_data_single_int32(template, b"Count", nbr_users)

        if len(subprops) == 1:
            prop_type_name, (properties, _nbr_sub_type_users) = next(iter(subprops.items()))
            subprops = (prop_type_name, properties)
            ref_templates[(type_name, prop_type_name)].written[0] = True
        else:
            # Ack! Even though this could/should work, looks like it is not supported. So we have to chose one. :|
            max_users = max_props = -1
            written_prop_type_name = None
            for prop_type_name, (properties, nbr_sub_type_users) in subprops.items():
                if nbr_sub_type_users > max_users or (nbr_sub_type_users == max_users and len(properties) > max_props):
                    max_users = nbr_sub_type_users
                    max_props = len(properties)
                    written_prop_type_name = prop_type_name
            subprops = (written_prop_type_name, properties)
            ref_templates[(type_name, written_prop_type_name)].written[0] = True

        prop_type_name, properties = subprops
        if prop_type_name and properties:
            elem = elem_data_single_string(template, b"PropertyTemplate", prop_type_name)
            props = elem_properties(elem)
            for name, (value, ptype, animatable) in properties.items():
                try:
                    elem_props_set(props, ptype, name, value, animatable=animatable)
                except Exception as e:
                    print("Failed to write template prop (%r)" % e)
                    print(props, ptype, name, value, animatable)


# ##### FBX animation helpers. #####


class AnimationCurveNodeWrapper:
    """
    This class provides a same common interface for all (FBX-wise) AnimationCurveNode and AnimationCurve elements,
    and easy API to handle those.
    """
    __slots__ = (
        'elem_keys', '_keys', 'default_values', 'fbx_group', 'fbx_gname', 'fbx_props',
        'force_keying', 'force_startend_keying')

    kinds = {
        'LCL_TRANSLATION': ("Lcl Translation", "T", ("X", "Y", "Z")),
        'LCL_ROTATION': ("Lcl Rotation", "R", ("X", "Y", "Z")),
        'LCL_SCALING': ("Lcl Scaling", "S", ("X", "Y", "Z")),
        'SHAPE_KEY': ("DeformPercent", "DeformPercent", ("DeformPercent",)),
        'CAMERA_FOCAL': ("FocalLength", "FocalLength", ("FocalLength",)),
        'CAMERA_FOCUS_DISTANCE': ("FocusDistance", "FocusDistance", ("FocusDistance",)),
        'CUSTOM': ("Value", "Value", ("Value",)),
    }

    def __init__(self, elem_key, kind, force_keying, force_startend_keying, default_values=...):
        self.elem_keys = [elem_key]
        assert(kind in self.kinds)
        if kind == 'CUSTOM':
            self.fbx_group = [default_values[0]]
            self.fbx_gname = [default_values[0]]
            self.fbx_props = [(default_values[0],)]
            default_values = (0.0,)
        else:
            self.fbx_group = [self.kinds[kind][0]]
            self.fbx_gname = [self.kinds[kind][1]]
            self.fbx_props = [self.kinds[kind][2]]
        self.force_keying = force_keying
        self.force_startend_keying = force_startend_keying
        self._keys = []  # (frame, values, write_flags)
        if default_values is not ...:
            assert(len(default_values) == len(self.fbx_props[0]))
            self.default_values = default_values
        else:
            self.default_values = (0.0) * len(self.fbx_props[0])

    def __bool__(self):
        # We are 'True' if we do have some validated keyframes...
        return bool(self._keys) and (True in ((True in k[2]) for k in self._keys))

    def add_group(self, elem_key, fbx_group, fbx_gname, fbx_props):
        """
        Add another whole group stuff (curvenode, animated item/prop + curvnode/curve identifiers).
        E.g. Shapes animations is written twice, houra!
        """
        assert(len(fbx_props) == len(self.fbx_props[0]))
        self.elem_keys.append(elem_key)
        self.fbx_group.append(fbx_group)
        self.fbx_gname.append(fbx_gname)
        self.fbx_props.append(fbx_props)

    def add_keyframe(self, frame, values):
        """
        Add a new keyframe to all curves of the group.
        """
        assert(len(values) == len(self.fbx_props[0]))
        self._keys.append((frame, values, [True] * len(values)))  # write everything by default.

    def simplify(self, fac, step, force_keep=False):
        """
        Simplifies sampled curves by only enabling samples when:
            * their values relatively differ from the previous sample ones.
        """
        if not self._keys:
            return

        if fac == 0.0:
            return

        # So that, with default factor and step values (1), we get:
        min_reldiff_fac = fac * 1.0e-3  # min relative value evolution: 0.1% of current 'order of magnitude'.
        min_absdiff_fac = 0.1  # A tenth of reldiff...
        keys = self._keys

        p_currframe, p_key, p_key_write = keys[0]
        p_keyed = list(p_key)
        are_keyed = [False] * len(p_key)
        for currframe, key, key_write in keys:
            for idx, (val, p_val) in enumerate(zip(key, p_key)):
                key_write[idx] = False
                p_keyedval = p_keyed[idx]
                if val == p_val:
                    # Never write keyframe when value is exactly the same as prev one!
                    continue
                # This is contracted form of relative + absolute-near-zero difference:
                #     absdiff = abs(a - b)
                #     if absdiff < min_reldiff_fac * min_absdiff_fac:
                #         return False
                #     return (absdiff / ((abs(a) + abs(b)) / 2)) > min_reldiff_fac
                # Note that we ignore the '/ 2' part here, since it's not much significant for us.
                if abs(val - p_val) > (min_reldiff_fac * max(abs(val) + abs(p_val), min_absdiff_fac)):
                    # If enough difference from previous sampled value, key this value *and* the previous one!
                    key_write[idx] = True
                    p_key_write[idx] = True
                    p_keyed[idx] = val
                    are_keyed[idx] = True
                elif abs(val - p_keyedval) > (min_reldiff_fac * max((abs(val) + abs(p_keyedval)), min_absdiff_fac)):
                    # Else, if enough difference from previous keyed value, key this value only!
                    key_write[idx] = True
                    p_keyed[idx] = val
                    are_keyed[idx] = True
            p_currframe, p_key, p_key_write = currframe, key, key_write

        # If we write nothing (action doing nothing) and are in 'force_keep' mode, we key everything! :P
        # See T41766.
        # Also, it seems some importers (e.g. UE4) do not handle correctly armatures where some bones
        # are not animated, but are children of animated ones, so added an option to systematically force writing
        # one key in this case.
        # See T41719, T41605, T41254...
        if self.force_keying or (force_keep and not self):
            are_keyed[:] = [True] * len(are_keyed)

        # If we did key something, ensure first and last sampled values are keyed as well.
        if self.force_startend_keying:
            for idx, is_keyed in enumerate(are_keyed):
                if is_keyed:
                    keys[0][2][idx] = keys[-1][2][idx] = True

    def get_final_data(self, scene, ref_id, force_keep=False):
        """
        Yield final anim data for this 'curvenode' (for all curvenodes defined).
        force_keep is to force to keep a curve even if it only has one valid keyframe.
        """
        curves = [[] for k in self._keys[0][1]]
        for currframe, key, key_write in self._keys:
            for curve, val, wrt in zip(curves, key, key_write):
                if wrt:
                    curve.append((currframe, val))

        force_keep = force_keep or self.force_keying
        for elem_key, fbx_group, fbx_gname, fbx_props in \
            zip(self.elem_keys, self.fbx_group, self.fbx_gname, self.fbx_props):
            group_key = get_blender_anim_curve_node_key(scene, ref_id, elem_key, fbx_group)
            group = {}
            for c, def_val, fbx_item in zip(curves, self.default_values, fbx_props):
                fbx_item = FBX_ANIM_PROPSGROUP_NAME + "|" + fbx_item
                curve_key = get_blender_anim_curve_key(scene, ref_id, elem_key, fbx_group, fbx_item)
                # (curve key, default value, keyframes, write flag).
                group[fbx_item] = (curve_key, def_val, c,
                                   True if (len(c) > 1 or (len(c) > 0 and force_keep)) else False)
            yield elem_key, group_key, group, fbx_group, fbx_gname


# ##### FBX objects generators. #####

# FBX Model-like data (i.e. Blender objects, depsgraph instances and bones) are wrapped in ObjectWrapper.
# This allows us to have a (nearly) same code FBX-wise for all those types.
# The wrapper tries to stay as small as possible, by mostly using callbacks (property(get...))
# to actual Blender data it contains.
# Note it caches its instances, so that you may call several times ObjectWrapper(your_object)
# with a minimal cost (just re-computing the key).

class MetaObjectWrapper(type):
    def __call__(cls, bdata, armature=None):
        if bdata is None:
            return None
        dup_mat = None
        if isinstance(bdata, Object):
            key = get_blenderID_key(bdata)
        elif isinstance(bdata, DepsgraphObjectInstance):
            if bdata.is_instance:
                key = "|".join((get_blenderID_key((bdata.parent.original, bdata.instance_object.original)),
                                cls._get_dup_num_id(bdata)))
                dup_mat = bdata.matrix_world.copy()
            else:
                key = get_blenderID_key(bdata.object.original)
        else:  # isinstance(bdata, (Bone, PoseBone)):
            if isinstance(bdata, PoseBone):
                bdata = armature.data.bones[bdata.name]
            key = get_blenderID_key((armature, bdata))

        cache = getattr(cls, "_cache", None)
        if cache is None:
            cache = cls._cache = {}
        instance = cache.get(key)
        if instance is not None:
            # Duplis hack: since dupli instances are not persistent in Blender (we have to re-create them to get updated
            # info like matrix...), we *always* need to reset that matrix when calling ObjectWrapper() (all
            # other data is supposed valid during whole cache live span, so we can skip resetting it).
            instance._dupli_matrix = dup_mat
            return instance

        instance = cls.__new__(cls, bdata, armature)
        instance.__init__(bdata, armature)
        instance.key = key
        instance._dupli_matrix = dup_mat
        cache[key] = instance
        return instance


class ObjectWrapper(metaclass=MetaObjectWrapper):
    """
    This class provides a same common interface for all (FBX-wise) object-like elements:
    * Blender Object
    * Blender Bone and PoseBone
    * Blender DepsgraphObjectInstance (for dulis).
    Note since a same Blender object might be 'mapped' to several FBX models (esp. with duplis),
    we need to use a key to identify each.
    """
    __slots__ = (
        'name', 'key', 'bdata', 'parented_to_armature', 'override_materials',
        '_tag', '_ref', '_dupli_matrix'
    )

    @classmethod
    def cache_clear(cls):
        if hasattr(cls, "_cache"):
            del cls._cache

    @staticmethod
    def _get_dup_num_id(bdata):
        INVALID_IDS = {2147483647, 0}
        pids = tuple(bdata.persistent_id)
        idx_valid = 0
        prev_i = ...
        for idx, i in enumerate(pids[::-1]):
            if i not in INVALID_IDS or (idx == len(pids) and i == 0 and prev_i != 0):
                idx_valid = len(pids) - idx
                break
            prev_i = i
        return ".".join(str(i) for i in pids[:idx_valid])

    def __init__(self, bdata, armature=None):
        """
        bdata might be an Object (deprecated), DepsgraphObjectInstance, Bone or PoseBone.
        If Bone or PoseBone, armature Object must be provided.
        """
        # Note: DepsgraphObjectInstance are purely runtime data, they become invalid as soon as we step to the next item!
        #       Hence we have to immediately copy *all* needed data...
        if isinstance(bdata, Object):  # DEPRECATED
            self._tag = 'OB'
            self.name = get_blenderID_name(bdata)
            self.bdata = bdata
            self._ref = None
        elif isinstance(bdata, DepsgraphObjectInstance):
            if bdata.is_instance:
                # Note that dupli instance matrix is set by meta-class initialization.
                self._tag = 'DP'
                self.name = "|".join((get_blenderID_name((bdata.parent.original, bdata.instance_object.original)),
                                      "Dupli", self._get_dup_num_id(bdata)))
                self.bdata = bdata.instance_object.original
                self._ref = bdata.parent.original
            else:
                self._tag = 'OB'
                self.name = get_blenderID_name(bdata)
                self.bdata = bdata.object.original
                self._ref = None
        else:  # isinstance(bdata, (Bone, PoseBone)):
            if isinstance(bdata, PoseBone):
                bdata = armature.data.bones[bdata.name]
            self._tag = 'BO'
            self.name = get_blenderID_name(bdata)
            self.bdata = bdata
            self._ref = armature
        self.parented_to_armature = False
        self.override_materials = None

    def __eq__(self, other):
        return isinstance(other, self.__class__) and self.key == other.key

    def __hash__(self):
        return hash(self.key)

    def __repr__(self):
        return self.key

    # #### Common to all _tag values.
    def get_fbx_uuid(self):
        return get_fbx_uuid_from_key(self.key)
    fbx_uuid = property(get_fbx_uuid)

    # XXX Not sure how much that’s useful now... :/
    def get_hide(self):
        return self.bdata.hide_viewport if self._tag in {'OB', 'DP'} else self.bdata.hide
    hide = property(get_hide)

    def get_parent(self):
        if self._tag == 'OB':
            if (self.bdata.parent and self.bdata.parent.type == 'ARMATURE' and
                self.bdata.parent_type == 'BONE' and self.bdata.parent_bone):
                # Try to parent to a bone.
                bo_par = self.bdata.parent.pose.bones.get(self.bdata.parent_bone, None)
                if (bo_par):
                    return ObjectWrapper(bo_par, self.bdata.parent)
                else:  # Fallback to mere object parenting.
                    return ObjectWrapper(self.bdata.parent)
            else:
                # Mere object parenting.
                return ObjectWrapper(self.bdata.parent)
        elif self._tag == 'DP':
            return ObjectWrapper(self._ref)
        else:  # self._tag == 'BO'
            return ObjectWrapper(self.bdata.parent, self._ref) or ObjectWrapper(self._ref)
    parent = property(get_parent)

    def get_bdata_pose_bone(self):
        if self._tag == 'BO':
            return self._ref.pose.bones[self.bdata.name]
        return None
    bdata_pose_bone = property(get_bdata_pose_bone)

    def get_matrix_local(self):
        if self._tag == 'OB':
            return self.bdata.matrix_local.copy()
        elif self._tag == 'DP':
            return self._ref.matrix_world.inverted_safe() @ self._dupli_matrix
        else:  # 'BO', current pose
            # PoseBone.matrix is in armature space, bring in back in real local one!
            par = self.bdata.parent
            par_mat_inv = self._ref.pose.bones[par.name].matrix.inverted_safe() if par else Matrix()
            return par_mat_inv @ self._ref.pose.bones[self.bdata.name].matrix
    matrix_local = property(get_matrix_local)

    def get_matrix_global(self):
        if self._tag == 'OB':
            return self.bdata.matrix_world.copy()
        elif self._tag == 'DP':
            return self._dupli_matrix
        else:  # 'BO', current pose
            return self._ref.matrix_world @ self._ref.pose.bones[self.bdata.name].matrix
    matrix_global = property(get_matrix_global)

    def get_matrix_rest_local(self):
        if self._tag == 'BO':
            # Bone.matrix_local is in armature space, bring in back in real local one!
            par = self.bdata.parent
            par_mat_inv = par.matrix_local.inverted_safe() if par else Matrix()
            return par_mat_inv @ self.bdata.matrix_local
        else:
            return self.matrix_local.copy()
    matrix_rest_local = property(get_matrix_rest_local)

    def get_matrix_rest_global(self):
        if self._tag == 'BO':
            return self._ref.matrix_world @ self.bdata.matrix_local
        else:
            return self.matrix_global.copy()
    matrix_rest_global = property(get_matrix_rest_global)

    # #### Transform and helpers
    def has_valid_parent(self, objects):
        par = self.parent
        if par in objects:
            if self._tag == 'OB':
                par_type = self.bdata.parent_type
                if par_type in {'OBJECT', 'BONE'}:
                    return True
                else:
                    print("Sorry, “{}” parenting type is not supported".format(par_type))
                    return False
            return True
        return False

    LEG_NAME_PATTERN = re.compile(r'[^a-zA-Z]?(thigh|calf)([^a-zA-Z]|$)', re.IGNORECASE)

    def is_leg_bone(self):
        return self.LEG_NAME_PATTERN.match(self.name) != None

    SYMMETRY_RIGHTSIDE_NAME_PATTERN = re.compile(r'(.+[_\.])(r|R)(\.\d+)?$')

    def is_rightside_bone(self, objects):
        if self.name.lower() == 'ik_hand_gun':
            return True
        match = self.SYMMETRY_RIGHTSIDE_NAME_PATTERN.match(self.name)
        if match:
            counterpartname = match.group(1) + ('l' if match.group(2) == 'r' else 'L') + (match.group(3) if match.group(3) else '')
            for i in objects:
                if i != self and i._tag == 'BO' and i.name == counterpartname:
                    #print(self.name, counterpartname)
                    return True
        return False

    def is_reverse_direction_bone(self, scene_data):
        if scene_data.settings.use_ue_mannequin_bone_alignment and self.is_leg_bone():
            return not self.is_rightside_bone(scene_data.objects)
        return self.is_rightside_bone(scene_data.objects)

    def get_bone_align_matrix(self, scene_data):
        bone_aligns = scene_data.settings.bone_align_matrix_dict
        if bone_aligns and self.armature.name in bone_aligns:
            if self.bdata.name in bone_aligns[self.armature.name]:
                return bone_aligns[self.armature.name][self.bdata.name][0]
        return None
    
    def get_parent_bone_align_matrix_inv(self, scene_data):
        if self.bdata.parent:
            bone_aligns = scene_data.settings.bone_align_matrix_dict
            if bone_aligns and self.armature.name in bone_aligns:
                if self.bdata.parent.name in bone_aligns[self.armature.name]:
                    return bone_aligns[self.armature.name][self.bdata.parent.name][1]
        return None

    def use_bake_space_transform(self, scene_data):
        # NOTE: Only applies to object types supporting this!!! Currently, only meshes and the like...
        # TODO: Check whether this can work for bones too...
        return (scene_data.settings.bake_space_transform and self._tag in {'OB', 'DP'} and
                self.bdata.type in BLENDER_OBJECT_TYPES_MESHLIKE | {'EMPTY'})

    def fbx_object_matrix(self, scene_data, rest=False, local_space=False, global_space=False):
        """
        Generate object transform matrix (*always* in matching *FBX* space!).
        If local_space is True, returned matrix is *always* in local space.
        Else if global_space is True, returned matrix is always in world space.
        If both local_space and global_space are False, returned matrix is in parent space if parent is valid,
        else in world space.
        Note local_space has precedence over global_space.
        If rest is True and object is a Bone, returns matching rest pose transform instead of current pose one.
        Applies specific rotation to bones, lamps and cameras (conversion Blender -> FBX).
        """
        # Objects which are not bones and do not have any parent are *always* in global space
        # (unless local_space is True!).
        is_global = (not local_space and
                     (global_space or not (self._tag in {'DP', 'BO'} or self.has_valid_parent(scene_data.objects))))

        # Objects (meshes!) parented to armature are not parented to anything in FBX, hence we need them
        # in global space, which is their 'virtual' local space...
        is_global = is_global or self.parented_to_armature

        # Since we have to apply corrections to some types of object, we always need local Blender space here...
        matrix = self.matrix_rest_local if rest else self.matrix_local
        parent = self.parent

        # Bones, lamps and cameras need to be rotated (in local space!).
        if self._tag == 'BO':
            # If we have a bone parent we need to undo the parent correction.
            if not is_global and scene_data.settings.bone_correction_matrix_inv and parent and parent.is_bone:
                par_mat_align_inv = self.get_parent_bone_align_matrix_inv(scene_data)
                if par_mat_align_inv:
                    matrix = par_mat_align_inv @ matrix
                if scene_data.settings.reverse_direction_bone_correction_matrix_inv and parent.is_reverse_direction_bone(scene_data):
                    matrix = scene_data.settings.reverse_direction_bone_correction_matrix_inv @ matrix
                elif scene_data.settings.bone_correction_matrix_inv:
                    matrix = scene_data.settings.bone_correction_matrix_inv @ matrix
            # Apply the bone correction.
            mat_align = self.get_bone_align_matrix(scene_data)
            if mat_align:
                matrix = matrix @ mat_align
            if scene_data.settings.reverse_direction_bone_correction_matrix and self.is_reverse_direction_bone(scene_data):
                matrix = matrix @ scene_data.settings.reverse_direction_bone_correction_matrix
            elif scene_data.settings.bone_correction_matrix:
                matrix = matrix @ scene_data.settings.bone_correction_matrix
        elif self.bdata.type == 'LIGHT':
            matrix = matrix @ MAT_CONVERT_LIGHT
        elif self.bdata.type == 'CAMERA':
            matrix = matrix @ MAT_CONVERT_CAMERA

        if self._tag in {'DP', 'OB'} and parent:
            if parent._tag == 'BO':
                # In bone parent case, we get transformation in **bone tip** space (sigh).
                # Have to bring it back into bone root, which is FBX expected value.
                matrix = Matrix.Translation((0, (parent.bdata.tail - parent.bdata.head).length, 0)) @ matrix

        # Our matrix is in local space, time to bring it in its final desired space.
        if parent:
            if is_global:
                # Move matrix to global Blender space.
                matrix = (parent.matrix_rest_global if rest else parent.matrix_global) @ matrix
            elif parent.use_bake_space_transform(scene_data):
                # Blender's and FBX's local space of parent may differ if we use bake_space_transform...
                # Apply parent's *Blender* local space...
                matrix = (parent.matrix_rest_local if rest else parent.matrix_local) @ matrix
                # ...and move it back into parent's *FBX* local space.
                par_mat = parent.fbx_object_matrix(scene_data, rest=rest, local_space=True)
                matrix = par_mat.inverted_safe() @ matrix

        if self.use_bake_space_transform(scene_data):
            # If we bake the transforms we need to post-multiply inverse global transform.
            # This means that the global transform will not apply to children of this transform.
            matrix = matrix @ scene_data.settings.global_matrix_inv
        if is_global:
            # In any case, pre-multiply the global matrix to get it in FBX global space!
            matrix = scene_data.settings.global_matrix @ matrix

        return matrix

    def fbx_object_tx(self, scene_data, rest=False, rot_euler_compat=None):
        """
        Generate object transform data (always in local space when possible).
        """
        matrix = self.fbx_object_matrix(scene_data, rest=rest)
        loc, rot, scale = matrix.decompose()
        if scene_data.settings.disable_free_scale_animation:
            scale_value = (scale.x + scale.y + scale.z) / 3.0
            if math.isclose(scale_value, 1.0, rel_tol=0.00001):
                scale_value = 1.0
            scale = Vector((scale_value, scale_value, scale_value))
        matrix_rot = rot.to_matrix()
        # quat -> euler, we always use 'XYZ' order, use ref rotation if given.
        if rot_euler_compat is not None:
            rot = rot.to_euler('XYZ', rot_euler_compat)
        else:
            rot = rot.to_euler('XYZ')
        return loc, rot, scale, matrix, matrix_rot

    # #### _tag dependent...
    def get_is_object(self):
        return self._tag == 'OB'
    is_object = property(get_is_object)

    def get_is_dupli(self):
        return self._tag == 'DP'
    is_dupli = property(get_is_dupli)

    def get_is_bone(self):
        return self._tag == 'BO'
    is_bone = property(get_is_bone)

    def get_type(self):
        if self._tag in {'OB', 'DP'}:
            return self.bdata.type
        return ...
    type = property(get_type)

    def get_armature(self):
        if self._tag == 'BO':
            return ObjectWrapper(self._ref)
        return None
    armature = property(get_armature)

    def get_bones(self):
        if self._tag == 'OB' and self.bdata.type == 'ARMATURE':
            return (ObjectWrapper(bo, self.bdata) for bo in self.bdata.data.bones)
        return ()
    bones = property(get_bones)

    def get_materials(self):
        override_materials = self.override_materials
        if override_materials is not None:
            return override_materials
        if self._tag in {'OB', 'DP'}:
            return tuple(slot.material for slot in self.bdata.material_slots)
        return ()
    materials = property(get_materials)

    def is_deformed_by_armature(self, arm_obj):
        if not (self.is_object and self.type == 'MESH'):
            return False
        if self.parent == arm_obj and self.bdata.parent_type == 'ARMATURE':
            return True
        for mod in self.bdata.modifiers:
            if mod.type == 'ARMATURE' and mod.object == arm_obj.bdata:
                return True

    # #### Duplis...
    def dupli_list_gen(self, depsgraph):
        if self._tag == 'OB' and self.bdata.is_instancer:
            return (ObjectWrapper(dup) for dup in depsgraph.object_instances
                                       if dup.parent and ObjectWrapper(dup.parent.original) == self)
        return ()


def fbx_name_class(name, cls):
    return FBX_NAME_CLASS_SEP.join((name, cls))


# ##### Top-level FBX data container. #####

# Helper sub-container gathering all exporter settings related to media (texture files).
FBXExportSettingsMedia = namedtuple("FBXExportSettingsMedia", (
    "path_mode", "base_src", "base_dst", "subdir",
    "embed_textures", "copy_set", "embedded_set",
))

# Helper container gathering all exporter settings.
FBXExportSettings = namedtuple("FBXExportSettings", (
    "report", "to_axes", "global_matrix", "global_scale", "apply_unit_scale", "unit_scale",
    "bake_space_transform", "global_matrix_inv", "global_matrix_inv_transposed",
    "context_objects", "object_types", "use_mesh_modifiers", "use_mesh_modifiers_render",
    "mesh_smooth_type", "use_subsurf", "use_mesh_edges", "use_tspace", "use_triangles",
    "armature_nodetype", "use_armature_deform_only", "add_leaf_bones",
    "bone_correction_matrix", "bone_correction_matrix_inv",
    "reverse_direction_bone_correction_matrix", "reverse_direction_bone_correction_matrix_inv",
    "use_ue_mannequin_bone_alignment", "bone_align_matrix_dict", "disable_free_scale_animation",
    "bake_anim", "bake_anim_use_all_bones", "bake_anim_use_nla_strips", "bake_anim_use_all_actions",
    "bake_anim_step", "bake_anim_simplify_factor", "bake_anim_force_startend_keying",
    "use_metadata", "media_settings", "use_custom_props", "colors_type", "prioritize_active_color"
))

# Helper container gathering some data we need multiple times:
#     * templates.
#     * settings, scene.
#     * objects.
#     * object data.
#     * skinning data (binding armature/mesh).
#     * animations.
FBXExportData = namedtuple("FBXExportData", (
    "templates", "templates_users", "connections",
    "settings", "scene", "depsgraph", "objects", "animations", "animated", "frame_start", "frame_end",
    "data_empties", "data_lights", "data_cameras", "data_meshes", "mesh_material_indices",
    "data_bones", "data_leaf_bones", "data_deformers_skin", "data_deformers_shape",
    "data_world", "data_materials", "data_textures", "data_videos",
))
