# SPDX-FileCopyrightText: Xavier Loux (BleuRaven)
#
# SPDX-License-Identifier: GPL-3.0-or-later

# ----------------------------------------------
#  Blender For UnrealEngine
#  https://github.com/xavier150/Blender-For-UnrealEngine-Addons
# ----------------------------------------------

# Principal Component Analysis (PCA) oriented bounding box
# Based on:
# - Pearson, K. (1901). "On lines and planes of closest fit to systems of points in space."
#   Philosophical Magazine, 2(11):559–572.
# - Jolliffe, I. T. (2002). "Principal Component Analysis," 2nd edition.
#   Springer Series in Statistics.
#
# Implementation adapted for geometric bounding box estimation.
# This version aligns the bounding box to the principal axes of variance
# computed from the point cloud covariance matrix (fast approximation of MVBB).

import numpy as np
import bmesh
from typing import Any
from ... import bpl

# Compatibility fix for older Python versions - numpy type annotations
import sys
if sys.version_info >= (3, 10):
    # Python 3.10+ supports subscriptable numpy types natively
    pass
else:
    # Python simple monkey patch - avoid metaclass conflicts
    _original_ndarray = np.ndarray
    _original_dtype = np.dtype
    
    # Simple wrapper classes that just support __getitem__
    class ndarray:
        def __class_getitem__(cls, item):
            return _original_ndarray
    
    class dtype:
        def __class_getitem__(cls, item):
            return _original_dtype
    
    # Only patch if not already done (avoid reload issues)
    if not hasattr(np.ndarray, '__class_getitem__'):
        np.ndarray = ndarray
    if not hasattr(np.dtype, '__class_getitem__'):
        np.dtype = dtype


def calculate_mvbb_with_pca(coords: np.ndarray[Any, np.dtype[np.float64]]) -> np.ndarray[Any, np.dtype[np.float64]]:
    # Calculate the minimum-volume bounding box (MVBB) for the given object.
    # This is a placeholder implementation and should be replaced with actual MVBB calculation logic.
    
    # Center data
    mean = coords.mean(axis=0)
    coords_centered = coords - mean

    # PCA (use transpose so covariance is 3x3)
    cov = np.cov(coords_centered.T)  # type: ignore
    _, eigvecs = np.linalg.eigh(cov)  # type: ignore[arg-type]
    
    # Rotation matrix (principal axes)
    rot = eigvecs.T  # shape (3,3)

    # Rotate points into PCA frame
    coords_rot = coords_centered @ rot.T  # shape (N,3)

    # Bounding box in PCA frame
    mins = coords_rot.min(axis=0)
    maxs = coords_rot.max(axis=0)

    # Bounding box in PCA space
    mins = coords_rot.min(axis=0)
    maxs = coords_rot.max(axis=0)

    # 8 corners in PCA space
    corners: np.ndarray[Any, np.dtype[np.float64]] = np.array([
        [x, y, z]
        for x in [mins[0], maxs[0]]
        for y in [mins[1], maxs[1]]
        for z in [mins[2], maxs[2]]
    ])

    # Back to original space and return final corners
    corners_world = corners @ rot + mean
    return corners_world

def get_mvbb_bmesh(src_bm: bmesh.types.BMesh) -> bmesh.types.BMesh:
    counter = bpl.utils.CounterTimer()

    # Calculate the minimum-volume bounding box (MVBB) and add its faces to the target BMesh.
    coords: np.ndarray[Any, np.dtype[np.float64]] = np.array([v.co for v in src_bm.verts])
    corners_world: np.ndarray[Any, np.dtype[np.float64]] = calculate_mvbb_with_pca(coords)
    
    # === Build box BMesh ===
    obb_bm = bmesh.new()

    # Create verts at corners
    verts: list[bmesh.types.BMVert] = []
    for corner in corners_world:
        # Convert numpy array to tuple of floats for bmesh
        coord = tuple(float(x) for x in corner)  # type: ignore[arg-type]
        verts.append(obb_bm.verts.new(coord))
    obb_bm.verts.ensure_lookup_table()

    # Define faces by indices of verts (each face = quad)
    faces_idx = [
        (0,2,3,1),  # bottom
        (4,5,7,6),  # top
        (0,1,5,4),  # front
        (2,6,7,3),  # back
        (0,4,6,2),  # left
        (1,3,7,5),  # right
    ]
    for f in faces_idx:
        obb_bm.faces.new([verts[i] for i in f])
    obb_bm.normal_update()

    print("PCA MVBB calculation time: ", counter.get_str_time())
    return obb_bm

