# SPDX-FileCopyrightText: Xavier Loux (BleuRaven)
#
# SPDX-License-Identifier: GPL-3.0-or-later

# ----------------------------------------------
#  Blender For UnrealEngine
#  https://github.com/xavier150/Blender-For-UnrealEngine-Addons
# ----------------------------------------------


import bpy
from .. import bfu_ui
from .. import bbpl
from .. import bfu_static_mesh
from .. import bfu_skeletal_mesh
from .. import bfu_export_control
from .. import bfu_addon_prefs
from ..bfu_skeletal_mesh.bfu_export_procedure import BFU_FileTypeEnum
from .. import bfu_lod
from . import bfu_vertex_color_utils
from . import bfu_vertex_color_props
from .bfu_vertex_color_props import BFU_VertexColorImportOptionEnum




def draw_ui_object(layout: bpy.types.UILayout, context: bpy.types.Context, obj: bpy.types.Object):

    scene = bpy.context.scene 
    addon_prefs = bfu_addon_prefs.get_addon_preferences()

    # Hide filters
    if addon_prefs.useGeneratedScripts is False:
        return
    if bfu_export_control.bfu_export_control_utils.is_not_export_self(obj):
        return
    if bfu_lod.bfu_lod_props.get_object_export_as_lod_mesh(obj):
        return

    if bfu_ui.bfu_ui_utils.DisplayPropertyFilter("OBJECT", "MISC"):

        accordion = bbpl.blender_layout.layout_accordion.get_accordion(scene, "bfu_object_vertex_color_properties_expanded")
        if accordion:
            _, panel = accordion.draw(layout)
            if panel:
                # Vertex color
                bfu_vertex_color_settings = panel.column()
                bbpl.blender_layout.layout_doc_button.add_doc_page_operator(bfu_vertex_color_settings, text="About Vertex Color", url="https://github.com/xavier150/Blender-For-UnrealEngine-Addons/wiki/Vertex-Color")
                bfu_vertex_color_settings.prop(obj, 'bfu_vertex_color_import_option')
                if bfu_vertex_color_props.get_object_vertex_color_import_option(obj).value == BFU_VertexColorImportOptionEnum.OVERRIDE.value:
                    bfu_vertex_color_settings_color = bfu_vertex_color_settings.row()
                    bfu_vertex_color_settings_color.prop(obj, 'bfu_vertex_color_override_color')
                
                if bfu_vertex_color_props.get_object_vertex_color_import_option(obj) == BFU_VertexColorImportOptionEnum.REPLACE.value:
                    StaticMeshVertexColorImportOptionIndex = bfu_vertex_color_settings.row()
                    StaticMeshVertexColorImportOptionIndex.prop(obj, 'bfu_vertex_color_to_use')
                    if bfu_vertex_color_props.get_object_vertex_color_to_use(obj) == "CustomIndex":
                        StaticMeshVertexColorImportOptionIndexCustom = bfu_vertex_color_settings.row()
                        StaticMeshVertexColorImportOptionIndexCustom.prop(obj, 'bfu_vertex_color_index_to_use')

                    StaticMeshVertexColorFeedback = bfu_vertex_color_settings.row()
                    if obj.type == "MESH":
                        vced = bfu_vertex_color_utils.VertexColorExportData(obj)
                        if vced.export_type == "REPLACE":
                            my_text = f'Vertex color named {vced.name} will be used.'
                            StaticMeshVertexColorFeedback.label(text=my_text, icon='INFO')
                        else:
                            my_text = 'No vertex color found at this index.'
                            StaticMeshVertexColorFeedback.label(text=my_text, icon='ERROR')
                    else:
                        my_text = 'Vertex color property will be applied on the children.'
                        StaticMeshVertexColorFeedback.label(text=my_text, icon='INFO')
                
                # Add 'colors_type' parameter if Blender version is 3.4 or above
                blender_version = bpy.app.version

                if bfu_skeletal_mesh.bfu_skeletal_mesh_utils.is_skeletal_mesh(obj):
                    export_type: BFU_FileTypeEnum = bfu_skeletal_mesh.bfu_export_procedure.get_obj_export_file_type(obj)
                else:
                    export_type: BFU_FileTypeEnum = bfu_static_mesh.bfu_export_procedure.get_obj_export_file_type(obj)

                if export_type.value == BFU_FileTypeEnum.FBX.value:
                    if blender_version >= (3, 4, 0):
                        bfu_vertex_color_settings.prop(obj, 'bfu_vertex_color_type')
                            

def draw_ui_scene_collision(layout: bpy.types.UILayout):
    pass