import bpy
from .. import bfu_basics
from .. import bfu_utils
from .. import bfu_ui
from .. import bfu_camera
from .. import bfu_spline
from .. import bfu_collision
from .. import bfu_socket


class BFU_PT_BlenderForUnrealTool(bpy.types.Panel):
    # Tool panel

    bl_idname = "BFU_PT_BlenderForUnrealTool"
    bl_label = "Tool"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Unreal Engine"






    class BFU_OT_ComputAllLightMap(bpy.types.Operator):
        bl_label = "Calculate all surface area"
        bl_idname = "object.computalllightmap"
        bl_description = (
            "Click to calculate the surface of the all object in the scene"
            )

        def execute(self, context):
            updated = bfu_utils.UpdateAreaLightMapList()
            self.report(
                {'INFO'},
                "The light maps of " + str(updated) +
                " object(s) have been updated."
                )
            return {'FINISHED'}

    def draw(self, context):

        
        layout = self.layout
        scene = bpy.context.scene


        
        

        bfu_camera.bfu_camera_ui_and_props.draw_ui_scene_camera(layout)
        bfu_spline.bfu_spline_ui_and_props.draw_ui_scene_spline(layout)

        bfu_collision.bfu_collision_ui_and_props.draw_ui_scene_collision(layout)
        bfu_socket.bfu_socket_ui_and_props.draw_ui_scene_socket(layout)

        scene.bfu_lightmap_expanded.draw(layout)
        if scene.bfu_lightmap_expanded.is_expend():
            checkButton = layout.column()
            checkButton.operator("object.computalllightmap", icon='TEXTURE')

# -------------------------------------------------------------------
#   Register & Unregister
# -------------------------------------------------------------------

classes = (
    BFU_PT_BlenderForUnrealTool,
    BFU_PT_BlenderForUnrealTool.BFU_OT_ComputAllLightMap,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
