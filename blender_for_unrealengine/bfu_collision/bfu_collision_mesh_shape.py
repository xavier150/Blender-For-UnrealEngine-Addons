# SPDX-FileCopyrightText: Xavier Loux (BleuRaven)
#
# SPDX-License-Identifier: GPL-3.0-or-later

# ----------------------------------------------
#  Blender For UnrealEngine
#  https://github.com/xavier150/Blender-For-UnrealEngine-Addons
# ----------------------------------------------

import bpy
import bmesh
import mathutils
from typing import List, Optional
from . import shape_algorithms

def join_bmeshes(target_bm: bmesh.types.BMesh, other_bm: List[bmesh.types.BMesh]) -> None:
    for src_bm in other_bm:
        # Join src_bm into target_bm
        vert_map = {}
        for v in src_bm.verts:
            new_vert = target_bm.verts.new(v.co)
            vert_map[v] = new_vert
        target_bm.verts.ensure_lookup_table()

        for face in src_bm.faces:
            target_bm.faces.new([vert_map[v] for v in face.verts])  # type: ignore

def apply_mvbb(
    src_bm: bmesh.types.BMesh, 
    target_bm: bmesh.types.BMesh, 
    use_pca_approximation: bool = True
) -> None:

    if use_pca_approximation:
        new_bm = shape_algorithms.pca_mvbb.get_mvbb_bmesh(src_bm)
        join_bmeshes(target_bm, [new_bm])
    else:
        new_bm = shape_algorithms.true_mvbb.get_mvbb_bmesh(src_bm)
        join_bmeshes(target_bm, [new_bm])


def convert_to_box_shape(obj: bpy.types.Object, use_world_space: bool = True, use_pca_approximation: bool = True, keep_original: bool = False) -> None:
    # Convert obj to Box Shape.
    # keep_original: If True, keep the original mesh vertices and replace them with the box corners.
    # Unreal don't detect the shape as an box if it not perfectly a box.
    # Calculate the minimum-volume bounding box (MVBB) and replace vertices with the box corners.
    mesh = obj.data
    if not isinstance(mesh, bpy.types.Mesh):
        print("Object does not have a mesh, cannot convert to box shape.")
        return
    if mesh.is_editmode:
        print("Object is in edit mode, cannot convert to box shape.")
        return

    src_bm = bmesh.new()
    src_bm.from_mesh(mesh)

    inv_world_matrix: Optional[mathutils.Matrix] = None
    if use_world_space:
        # === Transform vertices into world space ===
        world_matrix = obj.matrix_world.copy()
        inv_world_matrix = world_matrix.inverted()
        for v in src_bm.verts:
            v.co = world_matrix @ v.co

    # === Compute MVBB in world space ===
    if keep_original:
        apply_mvbb(src_bm, src_bm, use_pca_approximation)
        bm = src_bm
    else:
        bm = bmesh.new()
        apply_mvbb(src_bm, bm, use_pca_approximation)

    if use_world_space and inv_world_matrix:
        # === Transform back to local space ===
        for v in bm.verts:
            v.co = inv_world_matrix @ v.co
        pass

    # Write back to mesh
    bm.to_mesh(mesh)
    bm.free()
    mesh.update()

def convert_to_convex_hull_shape(obj: bpy.types.Object, keep_original: bool = False) -> None:
    # Convert obj to Convex Hull Shape.
    # keep_original: If True, keep the original mesh vertices and add the convex hull around them.
    mesh = obj.data
    if not isinstance(mesh, bpy.types.Mesh):
        print("Object has no mesh, cannot compute convex hull.")
        return
    if obj.mode != 'OBJECT':
        print("Object must be in OBJECT mode.")
        return

    bm = bmesh.new()
    bm.from_mesh(mesh)

    result = bmesh.ops.convex_hull(
        bm,
        input=bm.verts, # type: ignore
        use_existing_faces=False
    )

    if not keep_original:
        # The convex hull operation may leave the original vertices, but since we are
        # using a clean bmesh, only the hull faces exist. Still, let's ensure cleanup.
        geom = set(result.get("geom", []))
        all_geom = set(bm.verts) | set(bm.edges) | set(bm.faces)
        extra_geom = all_geom - geom
        if extra_geom:
            bmesh.ops.delete(bm, geom=list(extra_geom), context='VERTS') # type: ignore

    if bm.faces:
        bmesh.ops.recalc_face_normals(bm, faces=bm.faces) # type: ignore

    # Write back to mesh
    bm.to_mesh(mesh)
    bm.free()
    mesh.update()
