# SPDX-FileCopyrightText: Xavier Loux (BleuRaven)
#
# SPDX-License-Identifier: GPL-3.0-or-later

# ----------------------------------------------
#  Blender For UnrealEngine
#  https://github.com/xavier150/Blender-For-UnrealEngine-Addons
# ----------------------------------------------

# Minimum Volume Bounding Box (MVBB) computation
# Based on:
# - O'Rourke, J. (1985). "Finding minimal enclosing boxes."
#   International Journal of Computer and Information Sciences, 14(3):183–199.
# - Barequet, G. & Har-Peled, S. (2001).
#   "Efficiently approximating the minimum-volume bounding box of a point set in three dimensions."
#   Journal of Algorithms, 38(1):91–109.

import numpy as np
import bmesh
from typing import Any, Optional
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

def _orthonormalize(
    n1: np.ndarray[Any, np.dtype[np.float64]], 
    n2: np.ndarray[Any, np.dtype[np.float64]], 
    n3: np.ndarray[Any, np.dtype[np.float64]], 
    eps: float = 1e-8
) -> Optional[np.ndarray[Any, np.dtype[np.float64]]]:

    """Orthonormalize three directions using Gram-Schmidt. Returns 3x3 or None if degenerate."""
    # Normalize first
    n1n = n1 / (np.linalg.norm(n1) + 1e-20)

    # Make n2 orthogonal to n1
    n2o = n2 - n1n * np.dot(n1n, n2)
    n2n = n2o / (np.linalg.norm(n2o) + 1e-20)
    if np.linalg.norm(n2o) < eps:
        return None

    # n3 as cross to ensure orthogonality (and best stability)
    n3c = np.cross(n1n, n2n) # type: ignore
    if np.linalg.norm(n3c) < eps: # type: ignore
        return None
    n3n = n3c / (np.linalg.norm(n3c) + 1e-20) # type: ignore

    R = np.stack([n1n, n2n, n3n], axis=0)  # rows are axes # type: ignore
    # Ensure right-handed
    if np.linalg.det(R) < 0:
        R[2] *= -1.0
    return R

def _pca_ref_volume(
    coords: np.ndarray[Any, np.dtype[np.float64]]
) -> float:

    """Cheap reference volume using PCA-aligned AABB (for outlier filtering)."""
    C = coords - coords.mean(axis=0)
    cov = np.cov(C.T) # type: ignore
    _, evecs = np.linalg.eigh(cov) # type: ignore
    R = evecs.T
    CR = C @ R.T
    side = CR.max(axis=0) - CR.min(axis=0)
    vol = float(np.prod(side)) # type: ignore
    return max(vol, 1e-18)

def calculate_true_mvbb(bm: bmesh.types.BMesh) -> np.ndarray[Any, np.dtype[np.float64]]:
    # === STEP 1: Convex hull (clean) ===
    result = bmesh.ops.convex_hull(
        bm,
        input=bm.verts,  # type: ignore
        use_existing_faces=False
    )
    geom = set(result.get("geom", []))
    all_geom = set(bm.verts) | set(bm.edges) | set(bm.faces)
    extra_geom = all_geom - geom
    if extra_geom:
        bmesh.ops.delete(bm, geom=list(extra_geom), context='VERTS')  # type: ignore
    if bm.faces:
        bmesh.ops.recalc_face_normals(bm, faces=bm.faces)  # type: ignore

    # Collect hull vertices as Nx3 array
    coords = np.array([v.co[:] for v in bm.verts], dtype=np.float64)
    if coords.shape[0] < 3:
        # Degenerate: build a tiny box around the point/segment
        center = coords.mean(axis=0) if coords.size else np.zeros(3)
        half = np.array([1e-6, 1e-6, 1e-6])
        corners = np.array([[x,y,z] for x in [center[0]-half[0], center[0]+half[0]]
                                      for y in [center[1]-half[1], center[1]+half[1]]
                                      for z in [center[2]-half[2], center[2]+half[2]]])
        return corners

    # Center for numerical stability
    center = coords.mean(axis=0)
    C = coords - center

    # Reference volume (PCA) to filter absurd cases
    ref_vol = _pca_ref_volume(coords)
    vol_upper_bound = ref_vol * 1e6  # generous outlier cap

    # === STEP 2: Unique face normals (with tolerance) ===
    # We gather directions up to sign (n and -n are equivalent for orientation).
    uniq = []
    for f in bm.faces:
        n = np.array(f.normal[:], dtype=np.float64)
        ln = np.linalg.norm(n)
        if ln < 1e-12:
            continue
        n /= ln  # type: ignore
        # fold sign to have a consistent hemisphere
        if n[0] < 0 or (abs(n[0]) < 1e-12 and (n[1] < 0 or (abs(n[1]) < 1e-12 and n[2] < 0))):
            n = -n  # type: ignore
        if not any(np.linalg.norm(n - m) < 1e-5 for m in uniq):  # type: ignore
            uniq.append(n)  # type: ignore

    if len(uniq) < 3:  # type: ignore
        # Fallback to PCA box if not enough distinct directions
        eig = np.linalg.eigh(np.cov(C.T))[1].T  # type: ignore
        CR = C @ eig.T
        mins, maxs = CR.min(axis=0), CR.max(axis=0)
        corners = np.array([[x,y,z] for x in [mins[0],maxs[0]]
                                     for y in [mins[1],maxs[1]]
                                     for z in [mins[2],maxs[2]]])
        corners_world = corners @ eig + center
        obb_bm = bmesh.new()
        vs = [obb_bm.verts.new(co) for co in corners_world]
        obb_bm.verts.ensure_lookup_table()
        for f in [(0,1,3,2),(4,5,7,6),(0,1,5,4),(2,3,7,6),(0,2,6,4),(1,3,7,5)]:
            obb_bm.faces.new([vs[i] for i in f])
        obb_bm.normal_update()
        return obb_bm  # type: ignore

    normals = uniq
    nN = len(normals)  # type: ignore

    # === STEP 3: Enumerate robust triplets ===
    best = (float("inf"), None, None, None)  # (vol, R, mins, maxs)

    # thresholds
    parallel_dot = 0.9995     # reject near-parallel pairs
    coplanar_eps = 1e-4       # reject near-coplanar triplets

    for i in range(nN):
        n1 = normals[i]  # type: ignore
        for j in range(i + 1, nN):
            n2 = normals[j]  # type: ignore
            if abs(np.dot(n1, n2)) > parallel_dot:  # type: ignore
                continue
            for k in range(j + 1, nN):
                n3 = normals[k]  # type: ignore
                # triple product magnitude -> coplanarity check
                triple = abs(np.dot(np.cross(n1, n2), n3))  # type: ignore
                if triple < coplanar_eps:
                    continue

                # Build a stable orthonormal basis (right-handed)
                R = _orthonormalize(n1, n2, n3)  # type: ignore
                if R is None:
                    continue

                # Project hull points
                CR = C @ R.T  # type: ignore
                mins = CR.min(axis=0)
                maxs = CR.max(axis=0)

                # Validate finite and reasonable volume
                side = maxs - mins
                if np.any(~np.isfinite(side)) or np.any(side <= 0):
                    continue
                volume = float(np.prod(side))  # type: ignore
                if not np.isfinite(volume) or volume <= 0 or volume > vol_upper_bound:
                    continue

                if volume < best[0]:
                    best = (volume, R.copy(), mins.copy(), maxs.copy())

    # Fallback to PCA if no valid triplet (very rare but safe)
    if best[1] is None:
        eig = np.linalg.eigh(np.cov(C.T))[1].T  # type: ignore
        CR = C @ eig.T  # type: ignore
        mins, maxs = CR.min(axis=0), CR.max(axis=0)
        corners = np.array([[x,y,z] for x in [mins[0],maxs[0]]
                                     for y in [mins[1],maxs[1]]
                                     for z in [mins[2],maxs[2]]])
        corners_world = corners @ eig + center
    else:
        _, R_best, mins, maxs = best
        corners = np.array([[x,y,z] for x in [mins[0],maxs[0]]
                                     for y in [mins[1],maxs[1]]
                                     for z in [mins[2],maxs[2]]])
        corners_world = corners @ R_best + center

    # === STEP 5: return final corners ===
    return corners_world

def get_mvbb_bmesh(src_bm: bmesh.types.BMesh) -> bmesh.types.BMesh:
    counter = bpl.utils.CounterTimer()

    # Calculate the minimum-volume bounding box (MVBB) and add its faces to the target BMesh.
    corners_world: np.ndarray[Any, np.dtype[np.float64]] = calculate_true_mvbb(src_bm)

    # === Build box BMesh ===
    obb_bm = bmesh.new()

    # Create verts at corners
    verts = [obb_bm.verts.new(corner) for corner in corners_world] # type: ignore
    obb_bm.verts.ensure_lookup_table()

    # Define faces by indices of verts (each face = quad)
    faces_idx = [
        (0, 1, 3, 2),  # bottom
        (4, 5, 7, 6),  # top
        (0, 1, 5, 4),  # front
        (2, 3, 7, 6),  # back
        (0, 2, 6, 4),  # left
        (1, 3, 7, 5),  # right
    ]
    for f in faces_idx:
        obb_bm.faces.new([verts[i] for i in f])
    obb_bm.normal_update()

    print("True MVBB calculation time: ", counter.get_str_time())
    return obb_bm

    