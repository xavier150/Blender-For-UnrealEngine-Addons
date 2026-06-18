# SPDX-FileCopyrightText: Xavier Loux (BleuRaven)
#
# SPDX-License-Identifier: GPL-3.0-or-later

# ----------------------------------------------
#  Blender For UnrealEngine
#  https://github.com/xavier150/Blender-For-UnrealEngine-Addons
# ----------------------------------------------


from typing import List, Tuple, TYPE_CHECKING, Optional, Any, Set
import bpy

def get_preset_values() -> List[str]:
    preset_values: List[str] = [
        ]
    return preset_values

class BFU_OT_SceneStaticCollectionExport(bpy.types.PropertyGroup):
    name: bpy.props.StringProperty(name="collection data name", default="Unknown", override={'LIBRARY_OVERRIDABLE'}) # type: ignore
    use: bpy.props.BoolProperty(name="export this collection", default=False, override={'LIBRARY_OVERRIDABLE'}) # type: ignore

    if TYPE_CHECKING:
        name: str
        use: bool

class BFU_UL_StaticCollectionExportTarget(bpy.types.UIList):

    def get_is_from_override_library(self, scene: bpy.types.Scene, collection_name: str) -> bool:
        if not scene.override_library:
            return False

        for prop in scene.override_library.properties:
            if prop.rna_path == "bfu_static_collection_asset_list":
                for op in prop.operations:
                    if op.subitem_local_name == collection_name:
                        return False
        return True

    def get_collection_source_file(self, scene: bpy.types.Scene) -> str:
        if not scene.override_library:
            return "<unknown>"

        override_library = scene.override_library
        if(override_library):
            reference = override_library.reference
            if(reference):
                library = reference.library
                if(library):
                    return library.name_full
        return "<unknown>"

    def draw_item(
            self, 
            context: bpy.types.Context, 
            layout: bpy.types.UILayout, 
            data: Optional[Any], 
            item: Optional[Any], 
            icon: Optional[int], 
            active_data: Any, 
            active_property: Optional[str], 
            index: Optional[int],
            flt_flag: Optional[int]
        ):

        collection_is_valid = False
        if not isinstance(item, BFU_OT_SceneStaticCollectionExport):
            return

        if item.name in bpy.data.collections:
            collection_is_valid = True

        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            if collection_is_valid:  # If action is valid
                layout.prop(
                    bpy.data.collections[item.name],
                    "name",
                    text="",
                    emboss=False,
                    icon="OUTLINER_COLLECTION")
                layout.prop(item, "use", text="")
            else:
                if data and self.get_is_from_override_library(data, item.name):
                    origin_file_name: str = self.get_collection_source_file(data)
                    data_text = (f'Collection named "{item.name}" Not Found. Please update it on the original file: "{origin_file_name}"')
                    layout.alert = True
                    layout.label(text=data_text, icon="LIBRARY_DATA_OVERRIDE")
                else:
                    data_text = (f'Collection named "{item.name}" Not found. Please click on update')
                    layout.alert = True
                    layout.label(text=data_text, icon="ERROR")

        # Not optimised for 'GRID' layout type.
        elif self.layout_type in {'GRID'}:
            layout.alignment = 'CENTER'
            layout.label(text="", icon_value=icon)


def scene_static_collection_asset_list(scene: bpy.types.Scene) -> List[BFU_OT_SceneStaticCollectionExport]:
    return scene.bfu_static_collection_asset_list # type: ignore

class BFU_OT_UpdateStaticCollectionButton(bpy.types.Operator):
    bl_label = "Update collection list"
    bl_idname = "object.updatecollectionlist"
    bl_description = "Update collection list"

    def execute(self, context: bpy.types.Context) -> Set[Any]:
        def update_export_collection_list(scene: bpy.types.Scene):
            # Update the provisional collection list known by the object

            def set_use_from_last(col_list: List[Tuple[str, bool]], CollectionName: str) -> bool:
                for item in col_list:
                    if item[0] == CollectionName:
                        if item[1]:
                            return True
                return False

            col_list_save: List[Tuple[str, bool]] = [("", False)]
            for col in scene_static_collection_asset_list(scene):  # CollectionProperty
                name = col.name
                use = col.use
                col_list_save.append((name, use))
            scene.bfu_static_collection_asset_list.clear() # type: ignore
            for col in bpy.data.collections:
                scene.bfu_static_collection_asset_list.add().name = col.name # type: ignore
                use_from_last = set_use_from_last(col_list_save, col.name)
                scene.bfu_static_collection_asset_list[col.name].use = use_from_last # type: ignore
        scene = context.scene
        if scene:
            update_export_collection_list(scene)
        return {'FINISHED'}


def get_scene_static_collection_asset_list(scene: bpy.types.Scene) -> List[BFU_OT_SceneStaticCollectionExport]:
    return scene.bfu_static_collection_asset_list  # type: ignore

def get_scene_active_static_collection_asset_list(scene: bpy.types.Scene) -> int:
    return scene.bfu_active_static_collection_asset_list  # type: ignore

# -------------------------------------------------------------------
#   Register & Unregister
# -------------------------------------------------------------------

classes = (
    BFU_OT_SceneStaticCollectionExport,
    BFU_UL_StaticCollectionExportTarget,
    BFU_OT_UpdateStaticCollectionButton,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.Scene.bfu_static_collection_asset_list = bpy.props.CollectionProperty( # type: ignore
        type=BFU_OT_SceneStaticCollectionExport,
        options={'LIBRARY_EDITABLE'},
        override={'LIBRARY_OVERRIDABLE', 'USE_INSERTION'},
        )
    
    bpy.types.Scene.bfu_active_static_collection_asset_list = bpy.props.IntProperty( # type: ignore
        name="Active Collection",
        description="Index of the currently active collection",
        override={'LIBRARY_OVERRIDABLE'},
        default=0
        )


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)

    del bpy.types.Scene.bfu_active_static_collection_asset_list # type: ignore
    del bpy.types.Scene.bfu_static_collection_asset_list # type: ignore