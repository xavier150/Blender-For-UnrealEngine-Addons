import bpy
from typing import List, Optional, Tuple

CONFLIT_RESOLUTIONS: Tuple[str, ...] = ("keep_both", "remove_old", "remove_new", "merge")

class SkinWeightMeshUpdater:
    """
    A class to update mesh skin weights by renaming vertex groups.
    """
    def __init__(self):
        self.update_weights: int = 0
        self.remove_weights: int = 0
        self.print_log: bool = False

    def update_mesh_skin_weight(
        self, obj: bpy.types.Object, old_names: List[str], new_name: str,
        conflit_resolution: Optional[str] = None,
    ):
        """
        Updates the skin weights of a mesh by renaming one or more old vertex groups to a new name.

        Args:
            obj (bpy.types.Object): The object whose skin weights need to be updated.
            old_names (list of str): A list of names of old vertex groups to rename.
            new_name (str): The new name for the specified vertex groups.
            conflit_resolution (str, optional): One of CONFLIT_RESOLUTIONS. "keep_both" skips
                conflicting groups, "remove_old" keeps the existing group, "remove_new" replaces
                it, and "merge" adds weights up to 1.0. None preserves the original behavior of
                replacing overlapping weights.

        Returns:
            None

        :param obj: The object whose skin weights need to be updated.
        :param old_names: A list of names of old vertex groups to rename.
        :param new_name: The new name for the specified vertex groups.
        """

        if conflit_resolution is not None and conflit_resolution not in CONFLIT_RESOLUTIONS:
            raise ValueError(f"Unknown conflict resolution: {conflit_resolution!r}.")

        if not isinstance(obj.data, bpy.types.Mesh):
            print("The object is not a mesh.")
            return

        # Check if the object has vertex groups
        if not obj.vertex_groups:
            print("The object does not contain any vertex groups.")
            return

        for old_name in old_names:
            if old_name == new_name:
                continue
            vg_old = obj.vertex_groups.get(old_name)
            if not vg_old:
                if self.print_log:
                    print(f"The vertex group '{old_name}' does not exist in the object: '{obj.name}'.")
                continue
            
            vg_new = obj.vertex_groups.get(new_name)
            if vg_new is not None:
                if conflit_resolution == "remove_old":
                    obj.vertex_groups.remove(vg_old)
                    self.remove_weights += 1
                    print(f'"{old_name}" removed from "{obj.name}"; keeping "{new_name}".')
                    continue
                if conflit_resolution == "keep_both":
                    print(f'Warning; Mesh "{obj.name}" already has Group "{new_name}"; keeping "{old_name}".')
                    continue
                if conflit_resolution == "remove_new":
                    obj.vertex_groups.remove(vg_new)
                    self.remove_weights += 1
                    print(f'"{new_name}" removed from "{obj.name}"; replacing it with "{old_name}".')
                    vg_new = None
            if vg_new is None:
                vg_new = obj.vertex_groups.new(name=new_name)

            for vert in obj.data.vertices:
                old_weight = None
                new_weight = 0.0
                for group in vert.groups:
                    if group.group == vg_old.index:
                        old_weight = group.weight
                    elif conflit_resolution == "merge" and group.group == vg_new.index:
                        new_weight = group.weight
                if old_weight is not None:
                    weight = min(old_weight + new_weight, 1.0) if conflit_resolution == "merge" else old_weight
                    vg_new.add([vert.index], weight, 'REPLACE')

            # Remove the old vertex group
            obj.vertex_groups.remove(vg_old)
            if self.print_log:
                print(f"The vertex group '{old_name}' has been renamed to '{new_name}'.")
            self.update_weights += 1

    def print_update_log(self):
        """
        Print a log of the number of data variables updated and removed.

        Args:
            None

        Returns:
            None
        """
        print(f'{self.update_weights} vertex groups have been updated.')
        print(f'{self.remove_weights} vertex groups have been removed.')