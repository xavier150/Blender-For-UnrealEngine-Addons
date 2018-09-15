#====================== BEGIN GPL LICENSE BLOCK ============================
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.	 See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.	 If not, see <http://www.gnu.org/licenses/>.
#  All rights reserved.
#
#======================= END GPL LICENSE BLOCK =============================

# ----------------------------------------------
#  This addons allows to easily export several objects at the same time in .fbx
#  for use in unreal engine 4 by removing the usual constraints
#  while respecting UE4 naming conventions and a clean tree structure.
#  It also contains a small toolkit for collisions and sockets
#  xavierloux.com
# ----------------------------------------------


bl_info = {
	'name': 'Blender for UnrealEngine',
	'description': "This add-ons allows to easily export several "
	"objects at the same time for use in unreal engine 4.",
	'author': 'Loux Xavier (BleuRaven)',
	'version': (0, 2, 0),
	'blender': (2, 79, 0),
	'location': 'View3D > Tool > Unreal Engine 4',
	'warning': '',
	"wiki_url": "https://github.com/xavier150/blender-for-unrealengine-addons",
	'tracker_url': '',
	'support': 'COMMUNITY',
	'category': 'Import-Export'}

	
import os
import bpy
import fnmatch
import time
from bpy.props import (
		StringProperty,
		BoolProperty,
		EnumProperty,
		IntProperty,
		FloatProperty,
		BoolVectorProperty,
		PointerProperty,
		CollectionProperty
		)

		
import importlib
from . import bfu_exportasset
importlib.reload(bfu_exportasset)
from . import bfu_writetext
importlib.reload(bfu_writetext)

from .bfu_basics import *
from .bfu_utils import *


class ue4ObjectPropertiesPanel(bpy.types.Panel):
	#Is Object Properties panel

	bl_idname = "panel.ue4.obj-properties"
	bl_label = "Object Properties"
	bl_space_type = "VIEW_3D"
	bl_region_type = "TOOLS"
	bl_category = "Unreal Engine 4"

	bpy.types.Object.ExportEnum = EnumProperty(
		name = "Export type",
		description	 = "Export procedure",
		items = [
			("auto", "Auto", "Exports only if one of the parents is \"Export recursive\"", "KEY_HLT", 1),
			("export_recursive", "Export recursive", "Export self object and all children", "KEYINGSET", 2),
			("dont_export", "Not exported", "Will never export", "KEY_DEHLT", 3)
			]
		)

	bpy.types.Object.exportFolderName = StringProperty(
		name = "Sub folder name",
		description	 = 'Sub folder name. No Sub folder created if left empty',
		maxlen = 64,
		default = "",
		subtype = 'FILE_NAME'
		)

	bpy.types.Object.ForceStaticMesh = BoolProperty(
		name="Force staticMesh",
		description="Force export asset like a StaticMesh if is ARMATURE type",
		default=False
		)
	
	bpy.types.Object.exportDeformOnly = BoolProperty(
		name="Export only deform Bones",
		description="Only write deforming bones (and non-deforming ones when they have deforming children)",
		default=True
		)
		
		
	def draw(self, context):


		layout = self.layout
		obj = context.object
		if obj is not None:
		
			AssetType = layout.row()
			AssetType.prop(obj, 'name', text="", icon='OBJECT_DATA')
			AssetType.label('('+ GetAssetType(obj)+')') #Show asset type
			
			ExportType = layout.column()
			ExportType.prop(obj, 'ExportEnum')
			
			if obj.ExportEnum == "export_recursive":
				folderNameProperty = layout.column()
				folderNameProperty.prop(obj, 'exportFolderName', icon='FILE_FOLDER')
				
				if obj.type == "ARMATURE":
					AssetType2 = layout.column()
					AssetType2.prop(obj, "ForceStaticMesh") #Show asset type
					if GetAssetType(obj) == "SkeletalMesh":
						AssetType2.prop(obj, 'exportDeformOnly')
		else:
			layout.label('Pleas select obj for show properties.')

			
class ue4ObjectImportPropertiesPanel(bpy.types.Panel):
	#Is Object Properties panel

	bl_idname = "panel.ue4.obj-import-properties"
	bl_label = "Object Import Properties"
	bl_space_type = "VIEW_3D"
	bl_region_type = "TOOLS"
	bl_category = "Unreal Engine 4"
	
	#ImportUI
	#https://api.unrealengine.com/INT/API/Editor/UnrealEd/Factories/UFbxImportUI/index.html
	
	bpy.types.Object.CreatePhysicsAsset = BoolProperty(
		name = "Create PhysicsAsset",
		description	 = "If checked, create a PhysicsAsset when is imported",
		default=True
		)
	
	#StaticMeshImportData
	#https://api.unrealengine.com/INT/API/Editor/UnrealEd/Factories/UFbxStaticMeshImportData/index.html
	
	bpy.types.Object.UseStaticMeshLODGroup = BoolProperty(
		name = "",
		description	 = '',
		default=False
		)
	bpy.types.Object.StaticMeshLODGroup = StringProperty(
		name = "LOD Group",
		description	 = "The LODGroup to associate with this mesh when it is imported. Default: LevelArchitecture, SmallProp, LargeProp, Deco, Vista, Foliage, HighDetail" ,
		maxlen = 32,
		default = "SmallProp"
		)
		
	bpy.types.Object.UseStaticMeshLightMapRes = BoolProperty(
		name = "",
		description	 = '',
		default=False
		)
	bpy.types.Object.StaticMeshLightMapRes = IntProperty(
		name = "Light Map resolution",
		description	 = " This is the resolution of the light map" ,
		soft_max = 2048,
		soft_min = 16,
		max = 4096, #Max for unreal
		min = 4, #Min for unreal
		default = 16
		)

	bpy.types.Object.GenerateLightmapUVs = BoolProperty(
		name = "Generate LightmapUVs",
		description	 = "" ,
		default=True,
		)
	
	#SkeletalMeshImportData
	#https://api.unrealengine.com/INT/API/Editor/UnrealEd/Factories/UFbxSkeletalMeshImportData/index.html
	
	#UFbxTextureImportData
	#https://api.unrealengine.com/INT/API/Editor/UnrealEd/Factories/UFbxTextureImportData/index.html
	
	bpy.types.Object.MaterialSearchLocation = EnumProperty(
		name = "Material search location",
		description	 = "Specify where we should search for matching materials when importing",
		items = [
			("Local", "Local", "Search for matching material in local import folder only.", 1),
			("UnderParent", "UnderParent", "Search for matching material recursively from parent folder.", 2),
			("UnderRoot", "UnderRoot", "Search for matching material recursively from root folder.", 3),
			("AllAssets", "AllAssets", "Search for matching material in all assets folders.", 4)
			]
		)

	

	def draw(self, context):


		layout = self.layout
		obj = context.object
		if obj is not None:
			if obj.ExportEnum == "export_recursive":
			
				#StaticMesh and SkeletalMesh prop
				if GetAssetType(obj) == "StaticMesh" or GetAssetType(obj) == "SkeletalMesh":
					MaterialSearchLocation = layout.row()
					MaterialSearchLocation.prop(obj, 'MaterialSearchLocation')
				
				#StaticMesh prop
				if GetAssetType(obj) == "StaticMesh":
					StaticMeshLODGroup = layout.row()
					StaticMeshLODGroup.prop(obj, 'UseStaticMeshLODGroup', text="")
					StaticMeshLODGroupChild = StaticMeshLODGroup.column()
					StaticMeshLODGroupChild.enabled = obj.UseStaticMeshLODGroup
					StaticMeshLODGroupChild.prop(obj, 'StaticMeshLODGroup')
					
					StaticMeshLightMapRes = layout.row()
					StaticMeshLightMapRes.prop(obj, 'UseStaticMeshLightMapRes', text="")
					StaticMeshLightMapResChild = StaticMeshLightMapRes.column()
					StaticMeshLightMapResChild.enabled = obj.UseStaticMeshLightMapRes
					StaticMeshLightMapResChild.prop(obj, 'StaticMeshLightMapRes')
					
					GenerateLightmapUVs = layout.row()
					GenerateLightmapUVs.prop(obj, 'GenerateLightmapUVs')
										
					
				#SkeletalMesh prop
				if GetAssetType(obj) == "SkeletalMesh":
					CreatePhysicsAsset = layout.row()
					CreatePhysicsAsset.prop(obj, "CreatePhysicsAsset")
					layout.label('...')

			else:
				layout.label('...')
		layout.label('Pleas select obj for show properties.')
			
	
class ue4AnimPropertiesPanel(bpy.types.Panel):
	#Is Animation Properties panel

	bl_idname = "panel.ue4.Anim-properties"
	bl_label = "Animation Properties"
	bl_space_type = "VIEW_3D"
	bl_region_type = "TOOLS"
	bl_category = "Unreal Engine 4"
	
	#Animation :

	class ACTION_UL_ExportTarget(bpy.types.UIList):
		def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
			ActionIsValid = False
			try:
				bpy.data.actions[item.name]
				ActionIsValid = True
			except:
				pass

			if self.layout_type in {'DEFAULT', 'COMPACT'}:
				if ActionIsValid: #If action is valid
					#layout.prop(item, "name", text="", emboss=False, icon="ACTION") #Debug only for see target line
					layout.prop(bpy.data.actions[item.name], "name", text="", emboss=False, icon="ACTION")
					layout.prop(item, "use", text="")
				else:
					dataText = ('Action data named "' + item.name + '" Not Found. Please clic on update')
					layout.label(text=dataText, icon="ERROR")
			# Not optimised for 'GRID' layout type.
			elif self.layout_type in {'GRID'}:
				layout.alignment = 'CENTER'
				layout.label(text="", icon_value=icon)
				
	class ObjExportAction(bpy.types.PropertyGroup):
		name = StringProperty(name="Action data name", default="Unknown")
		use = BoolProperty(name="use this action", default=False)

	bpy.utils.register_class(ACTION_UL_ExportTarget)
	bpy.utils.register_class(ObjExportAction)
	
	bpy.types.Object.exportActionList = CollectionProperty(
	#properties used with ""export_specific_list" on exportActionEnum
		type=ObjExportAction
		)

	bpy.types.Object.exportActionEnum = EnumProperty(
		name = "Action to export",
		description	 = "Export procedure for actions (Animations and poses)",
		items = [
			("export_auto", "Export auto", "Export all actions connected to the bones names", "FILE_SCRIPT", 1),
			("export_specific_list", "Export specific list", "Export only actions that are checked in the list", "LINENUMBERS_ON", 2),
			("export_specific_prefix", "Export specific prefix", "Export only actions with a specific prefix or the beginning of the actions names", "SYNTAX_ON", 3),
			("dont_export", "Not exported", "No action will be exported", "MATPLANE", 4)
			]
		)
		
	bpy.types.Object.active_ObjectAction = IntProperty(
		name="Active Scene Action",
		description="Index of the currently active object action",
		default=0
		)
	

	bpy.types.Object.PrefixNameToExport = StringProperty(
	#properties used with ""export_specific_prefix" on exportActionEnum
		name = "Prefix name",
		description	 = "Indicate the prefix of the actions that must be exported",
		maxlen = 32,
		default = "Example_",
		)
	
	bpy.types.Object.AnimStartEndTimeEnum = EnumProperty(
		name = "Animation start/end time",
		description	 = "Set when animation starts and end",
		items = [
			("with_keyframes", "Auto", "The time will be defined according to the first and the last frame", "KEYTYPE_KEYFRAME_VEC", 1),
			("with_sceneframes", "Scene time", "Time will be equal to the scene time", "SCENE_DATA", 2),
			("with_customframes", "Custom time", 'The time of all the animations of this object is defined by you. Use "AnimCustomStartTime" and "AnimCustomEndTime"', "HAND", 3),
			]
		)
		
	bpy.types.Object.AnimCustomStartTime = IntProperty(
		name = "Custom start time",
		description	 = "Set when animation start",
		default=0
		)
	
	bpy.types.Object.AnimCustomEndTime = IntProperty(
		name = "Custom end time",
		description	 = "Set when animation end",
		default=1
		)


	bpy.types.Object.SampleAnimForExport = FloatProperty(
		name="Sampling Rate",
		description="How often to evaluate animated values (in frames)",
		min=0.01, max=100.0,
		soft_min=0.01, soft_max=100.0,
		default=1.0,
		)
		
	bpy.types.Object.SimplifyAnimForExport = FloatProperty(
		name="Simplify animations",
		description="How much to simplify baked values (0.0 to disable, the higher the more simplified)",
		min=0.0, max=100.0,	 # No simplification to up to 10% of current magnitude tolerance.
		soft_min=0.0, soft_max=10.0,
		default=0.0,
		)
	
	class UpdateObjActionButton(bpy.types.Operator):
		bl_label = "Update action list"
		bl_idname = "object.updateobjaction"
		bl_description = "Update action list"
		
		def execute(self, context):
			def UpdateExportActionList(obj):
				#Update the provisional action list known by the object

				def SetUseFromLast(list, ActionName):
					for item in list:
						if item[0] == ActionName:
							if item[1] == True:
								return True
					return False

				AnimSave = [["", False]]
				for Anim in obj.exportActionList: #CollectionProperty
					name = Anim.name
					use = Anim.use
					AnimSave.append([name, use])
				obj.exportActionList.clear()
				for action in bpy.data.actions:
					obj.exportActionList.add().name = action.name
					obj.exportActionList[action.name].use = SetUseFromLast(AnimSave, action.name)
			UpdateExportActionList(bpy.context.object)
			return {'FINISHED'}

	class ShowActionToExport(bpy.types.Operator):
		bl_label = "Show action(s)"
		bl_idname = "object.showobjaction"
		bl_description = "Click to show actions that are to be exported with this armature."

		def execute(self, context):
			obj = context.object
			actions = GetActionToExport(obj)
			popup_title = "Action list"
			if len(actions) > 1:
				popup_title = str(len(actions))+' action(s) found for obj named "'+obj.name+'".'
			else:
				popup_title = 'No actions found for obj named "'+obj.name+'".'

			def draw(self, context):
				col = self.layout.column()
				for action in actions:
					row = col.row()
					row.label("- "+action.name+GetActionType(action))
			bpy.context.window_manager.popup_menu(draw, title=popup_title, icon='ACTION')
			return {'FINISHED'}
		
	
	def draw(self, context):

		layout = self.layout
		obj = context.object
		if obj is not None:
			if obj.ExportEnum == "export_recursive":
				if GetAssetType(obj) == "SkeletalMesh" or GetAssetType(obj) == "Camera":
				
					#Action time
					ActionTimeProperty = layout.column()
					if obj.type != "CAMERA":
						ActionTimeProperty.prop(obj, 'AnimStartEndTimeEnum')
						if obj.AnimStartEndTimeEnum == "with_customframes":
							ActionTimePropertyChild=ActionTimeProperty = layout.row()
							ActionTimePropertyChild.prop(obj, 'AnimCustomStartTime')
							ActionTimePropertyChild.prop(obj, 'AnimCustomEndTime')
					else:
						layout.label("Note: animation start/end use scene frames with the camera for the sequencer.")
					
					if GetAssetType(obj) == "SkeletalMesh":	
						#Action list
						ActionListProperty = layout.column()
						ActionListProperty.prop(obj, 'exportActionEnum')
						if obj.exportActionEnum == "export_specific_list":
							ActionListProperty.template_list(
								"ACTION_UL_ExportTarget", "",  # type and unique id
								obj, "exportActionList",  # pointer to the CollectionProperty
								obj, "active_ObjectAction",	 # pointer to the active identifier
								maxrows=5,
								rows=5
							)
							ActionListProperty.operator("object.updateobjaction", icon='RECOVER_LAST')
						if obj.exportActionEnum == "export_specific_prefix":
							ActionListProperty.prop(obj, 'PrefixNameToExport')

					#Action fbx properties
					propsFbx = layout.row()
					propsFbx.prop(obj, 'SampleAnimForExport')
					propsFbx.prop(obj, 'SimplifyAnimForExport')
					
					#Armature export action list feedback
					if GetAssetType(obj) == "SkeletalMesh":
						ArmaturePropertyInfo = layout.row().box().split(percentage = 0.75 )
						ActionNum = len(GetActionToExport(obj))
						actionFeedback = str(ActionNum) + " Action(s) will be exported with this armature."
						ArmaturePropertyInfo.label( actionFeedback, icon='INFO')
						ArmaturePropertyInfo.operator("object.showobjaction")
						layout.label('Note: The Action with only one frame are exported like Pose.')
				else:
					layout.label('This assets is not a SkeletalMesh or Camera')
			else:
				layout.label('...')

				
class ue4CollisionsAndSocketsPanel(bpy.types.Panel):
	#Is Collisions And Sockets panel

	bl_idname = "panel.ue4.collisionsandsockets"
	bl_label = "Collisions And Sockets"
	bl_space_type = "VIEW_3D"
	bl_region_type = "TOOLS"
	bl_category = "Unreal Engine 4"

	class ConvertToUECollisionButtonBox(bpy.types.Operator):
		bl_label = "Convert to box (UBX)"
		bl_idname = "object.converttoboxcollision"
		bl_description = "Convert selected mesh(es) to Unreal collision ready for export (Boxes type)"

		def execute(self, context):
			ConvertedObj = ConvertToUe4SubObj("Box", bpy.context.selected_objects, True)
			if len(ConvertedObj) > 0 :
				self.report({'INFO'}, str(len(ConvertedObj)) + " object(s) of the selection have be converted to UE4 Box collisions." )
			else :
				self.report({'WARNING'}, "Please select two objects. (Active object is the owner of the collision)")
			return {'FINISHED'}


	class ConvertToUECollisionButtonCapsule(bpy.types.Operator):
		bl_label = "Convert to capsule (UCP)"
		bl_idname = "object.converttocapsulecollision"
		bl_description = "Convert selected mesh(es) to Unreal collision ready for export (Capsules type)"

		def execute(self, context):
			ConvertedObj = ConvertToUe4SubObj("Capsule", bpy.context.selected_objects, True)
			if len(ConvertedObj) > 0 :
				self.report({'INFO'}, str(len(ConvertedObj)) + " object(s) of the selection have be converted to UE4 Capsule collisions." )
			else :
				self.report({'WARNING'}, "Please select two objects. (Active object is the owner of the collision)")
			return {'FINISHED'}


	class ConvertToUECollisionButtonSphere(bpy.types.Operator):
		bl_label = "Convert to sphere (USP)"
		bl_idname = "object.converttospherecollision"
		bl_description = "Convert selected mesh(es) to Unreal collision ready for export (Spheres type)"

		def execute(self, context):
			ConvertedObj = ConvertToUe4SubObj("Sphere", bpy.context.selected_objects, True)
			if len(ConvertedObj) > 0 :
				self.report({'INFO'}, str(len(ConvertedObj)) + " object(s) of the selection have be converted to UE4 Sphere collisions." )
			else :
				self.report({'WARNING'}, "Please select two objects. (Active object is the owner of the collision)")
			return {'FINISHED'}


	class ConvertToUECollisionButtonConvex(bpy.types.Operator):
		bl_label = "Convert to convex shape (UCX)"
		bl_idname = "object.converttoconvexcollision"
		bl_description = "Convert selected mesh(es) to Unreal collision ready for export (Convex shapes type)"

		def execute(self, context):
			ConvertedObj = ConvertToUe4SubObj("Convex", bpy.context.selected_objects, True)
			if len(ConvertedObj) > 0 :
				self.report({'INFO'}, str(len(ConvertedObj)) + " object(s) of the selection have be converted to UE4 Convex Shape collisions.")
			else :
				self.report({'WARNING'}, "Please select two objects. (Active object is the owner of the collision)")
			return {'FINISHED'}


	class ConvertToUESocketButton(bpy.types.Operator):
		bl_label = "Convert to socket (SOCKET)"
		bl_idname = "object.converttosocket"
		bl_description = "Convert selected Empty(s) to Unreal sockets ready for export"

		def execute(self, context):
			ConvertedObj = ConvertToUe4SubObj("Socket", bpy.context.selected_objects, True)
			if len(ConvertedObj) > 0 :
				self.report({'INFO'}, str(len(ConvertedObj)) + " object(s) of the selection have be converted to to UE4 Socket." )
			else :
				self.report({'WARNING'}, "Please select two objects. (Active object is the owner of the collision)")
			return {'FINISHED'}

	def draw(self, context):

		def FoundTypeInSelect(targetType): #Return True is a specific type is found
			for obj in bpy.context.selected_objects:
				if obj != bpy.context.active_object:
					if obj.type == targetType:
						return True
			return False

		self.layout.label("Convert selected object to Unreal collision or socket (Static Mesh only)", icon='PHYSICS')

		convertMeshButtons = self.layout.row().split(percentage = 0.80 )
		convertMeshButtons = convertMeshButtons.column()
		convertMeshButtons.enabled = FoundTypeInSelect("MESH")
		convertMeshButtons.operator("object.converttoboxcollision", icon='MESH_CUBE')
		convertMeshButtons.operator("object.converttoconvexcollision", icon='MESH_ICOSPHERE')
		convertMeshButtons.operator("object.converttocapsulecollision", icon='MESH_CAPSULE')
		convertMeshButtons.operator("object.converttospherecollision", icon='SOLID')

		convertMeshButtons = self.layout.row().split(percentage = 0.80 )
		convertEmptyButtons = convertMeshButtons.column()
		convertEmptyButtons.enabled = FoundTypeInSelect("EMPTY")
		convertEmptyButtons.operator("object.converttosocket", icon='OUTLINER_DATA_EMPTY')


class ue4NomenclaturePanel(bpy.types.Panel):
	#Is FPS Export panel

	bl_idname = "panel.ue4.exportnomenclature"
	bl_label = "Nomenclature"
	bl_space_type = "VIEW_3D"
	bl_region_type = "TOOLS"
	bl_category = "Unreal Engine 4"

	
	#Prefix
	bpy.types.Scene.static_prefix_export_name = bpy.props.StringProperty(
		name = "StaticMesh Prefix",
		description	 = "Prefix of staticMesh",
		maxlen = 32,
		default = "SM_")

	bpy.types.Scene.skeletal_prefix_export_name = bpy.props.StringProperty(
		name = "SkeletalMesh Prefix ",
		description	 = "Prefix of SkeletalMesh",
		maxlen = 32,
		default = "SK_")

	bpy.types.Scene.anim_prefix_export_name = bpy.props.StringProperty(
		name = "AnimationSequence Prefix",
		description	 = "Prefix of AnimationSequence",
		maxlen = 32,
		default = "Anim_")

	bpy.types.Scene.pose_prefix_export_name = bpy.props.StringProperty(
		name = "AnimationSequence(Pose) Prefix",
		description	 = "Prefix of AnimationSequence with only one frame",
		maxlen = 32,
		default = "Pose_")

	bpy.types.Scene.camera_prefix_export_name = bpy.props.StringProperty(
		name = "Camera anim Prefix",
		description	 = "Prefix of camera animations",
		maxlen = 32,
		default = "Cam_")

	#Sub folder
	bpy.types.Scene.anim_subfolder_name = bpy.props.StringProperty(
		name = "Animations sub folder name",
		description	 = "name of sub folder for animations",
		maxlen = 32,
		default = "Anim")
	
	#File path
	bpy.types.Scene.export_static_file_path = bpy.props.StringProperty(
		name = "StaticMesh export file path",
		description = "Choose a directory to export StaticMesh(s)",
		maxlen = 512,
		default = "//ExportedFbx\StaticMesh\\",
		subtype = 'DIR_PATH')

	bpy.types.Scene.export_skeletal_file_path = bpy.props.StringProperty(
		name = "SkeletalMesh export file path",
		description = "Choose a directory to export SkeletalMesh(s)",
		maxlen = 512,
		default = "//ExportedFbx\SkeletalMesh\\",
		subtype = 'DIR_PATH')

	bpy.types.Scene.export_camera_file_path = bpy.props.StringProperty(
		name = "Camera export file path",
		description = "Choose a directory to export Camera(s)",
		maxlen = 512,
		default = "//ExportedFbx\Sequencer\\",
		subtype = 'DIR_PATH')
		
	bpy.types.Scene.export_other_file_path = bpy.props.StringProperty(
		name = "Other export file path",
		description = "Choose a directory to export text file and other",
		maxlen = 512,
		default = "//ExportedFbx\Other\\",
		subtype = 'DIR_PATH')


	def draw(self, context):
		scn = context.scene
		
		#Prefix
		propsPrefix = self.layout.row()
		propsPrefix = propsPrefix.column()
		propsPrefix.prop(scn, 'static_prefix_export_name', icon='OBJECT_DATA')
		propsPrefix.prop(scn, 'skeletal_prefix_export_name', icon='OBJECT_DATA')
		propsPrefix.prop(scn, 'anim_prefix_export_name', icon='OBJECT_DATA')
		propsPrefix.prop(scn, 'pose_prefix_export_name', icon='OBJECT_DATA')
		propsPrefix.prop(scn, 'camera_prefix_export_name', icon='OBJECT_DATA')
		
		#Sub folder
		propsSub = self.layout.row()
		propsSub = propsSub.column()
		propsSub.prop(scn, 'anim_subfolder_name', icon='FILE_FOLDER')
		
		#File path
		propsPath = self.layout.row()
		propsPath = propsPath.column()
		propsPath.prop(scn, 'export_static_file_path')
		propsPath.prop(scn, 'export_skeletal_file_path')
		propsPath.prop(scn, 'export_camera_file_path')
		propsPath.prop(scn, 'export_other_file_path')
		

class ue4ImportScriptPanel(bpy.types.Panel):
	#Is Import script panel

	bl_idname = "panel.ue4.importScript"
	bl_label = "Import Script"
	bl_space_type = "VIEW_3D"
	bl_region_type = "TOOLS"
	bl_category = "Unreal Engine 4"

	bpy.types.Scene.unreal_import_location = bpy.props.StringProperty(
		name = "Unreal import location",
		description	 = "Unreal import location in /Game/",
		maxlen = 512,
		default = 'ImportedFbx')
		
	bpy.types.Scene.unreal_levelsequence_reference = bpy.props.StringProperty(
		name = "Unreal LevelSequence reference",
		description	 = "Copy Reference from unreal ine Content Browser",
		maxlen = 512,
		default = "LevelSequence'/Game/ImportedFbx/MySequence.MySequence'")

	def draw(self, context):
		scn = context.scene
		
		#Sub folder
		propsSub = self.layout.row()
		propsSub = propsSub.column()
		propsSub.prop(scn, 'unreal_import_location', icon='FILE_FOLDER')
		propsSub.prop(scn, 'unreal_levelsequence_reference', icon='FILE_FOLDER')

		
class ue4ExportPanel(bpy.types.Panel):
	#Is Export panel

	bl_idname = "panel.ue4.export"
	bl_label = "Export"
	bl_space_type = "VIEW_3D"
	bl_region_type = "TOOLS"
	bl_category = "Unreal Engine 4"
	
	class UnrealExportedAsset(bpy.types.PropertyGroup):
		#[AssetName , AssetType , ExportPath, ExportTime]
		assetName = StringProperty(default="None")
		assetType = StringProperty(default="None") #return from GetAssetType()
		exportPath = StringProperty(default="None")
		exportTime = FloatProperty(default=0)
		object = PointerProperty(type=bpy.types.Object)
		
	bpy.utils.register_class(UnrealExportedAsset)
	bpy.types.Scene.UnrealExportedAssetsList = CollectionProperty(
		type=UnrealExportedAsset
		)
		
	class UnrealPotentialError(bpy.types.PropertyGroup):
		type = IntProperty(default=0) #0:Info, 1:Warning, 2:Error
		object = PointerProperty(type=bpy.types.Object)
		itemName = StringProperty(default="None")
		text = StringProperty(default="Unknown")
		correctRef = StringProperty(default="None")
		correctlabel = StringProperty(default="Fix it !")
		correctDesc = StringProperty(default="Correct target error")
		
	bpy.utils.register_class(UnrealPotentialError)
	bpy.types.Scene.potentialErrorList = CollectionProperty(
		type=UnrealPotentialError
		)

	class ShowAssetToExport(bpy.types.Operator):
		bl_label = "Show asset(s)"
		bl_idname = "object.showasset"
		bl_description = "Click to show assets that are to be exported."

		def execute(self, context):
			obj = context.object
			assets = GetFinalAssetToExport()
			popup_title = "Assets list"
			if len(assets) > 0:
				popup_title = str(len(assets))+' asset(s) will be exported.'
			else:
				popup_title = 'No exportable assets were found.'

			def draw(self, context):
				col = self.layout.column()
				for asset in assets:
					row = col.row()
					if asset[0] is not None:
						if asset[1] is not None:
							row.label("      --> "+asset[1].name+" ("+asset[2]+")")
						else:
							row.label("- "+asset[0].name+" ("+asset[2]+")")
					else:
						row.label("- ("+asset[2]+")")
			bpy.context.window_manager.popup_menu(draw, title=popup_title, icon='EXTERNAL_DATA')
			return {'FINISHED'}

				
	class CheckPotentialErrorPopup(bpy.types.Operator):
		bl_label = "Check potential errors"
		bl_idname = "object.checkpotentialerror"
		bl_description = "Check potential errors"
		correctedProperty = 0
				
		class CorrectButton(bpy.types.Operator):
			bl_label = "Fix it !"
			bl_idname = "object.fixit"
			bl_description = "Correct target error"
			errorIndex = bpy.props.IntProperty(default=-1)
			
			def execute(self, context):
				result = TryToCorrectPotentialError(self.errorIndex)
				self.report({'INFO'}, result)
				return {'FINISHED'}
		
		def execute(self, context):
			self.report({'INFO'}, "ok")
			return {'FINISHED'}
	 
		def invoke(self, context, event):	
			def CorrectBadProperty():
			#Corrects bad properties
				UpdatedProp = 0
				for obj in GetAllCollisionAndSocketsObj():
					if obj.ExportEnum == "export_recursive":
						obj.ExportEnum = "auto"
						UpdatedProp += 1
				return UpdatedProp
		
			def UpdateNameHierarchy():
			#Updates hierarchy names
				for obj in GetAllCollisionAndSocketsObj():
					if fnmatch.fnmatchcase(obj.name, "UBX*"):
						ConvertToUe4SubObj("Box", [obj])
					if fnmatch.fnmatchcase(obj.name, "UCP*"):
						ConvertToUe4SubObj("Capsule", [obj])
					if fnmatch.fnmatchcase(obj.name, "USP*"):
						ConvertToUe4SubObj("Sphere", [obj])
					if fnmatch.fnmatchcase(obj.name, "UCX*"):
						ConvertToUe4SubObj("Convex", [obj])
					if fnmatch.fnmatchcase(obj.name, "SOCKET*"):
						ConvertToUe4SubObj("Socket", [obj])
						
			self.correctedProperty = CorrectBadProperty()
			UpdateNameHierarchy()
			UpdateUnrealPotentialError()
			wm = context.window_manager
			return wm.invoke_popup(self, width = 900)
	 
		def check(self, context):
			return True
			
		def draw(self, context):
			

			layout = self.layout
			if len(bpy.context.scene.potentialErrorList) > 0 :
				popup_title = str(len(bpy.context.scene.potentialErrorList))+" potential error(s) found!"
			else:
				popup_title = "No potential error to correct!"
			
			if self.correctedProperty > 0 :
				CheckInfo = str(self.correctedProperty) + " properties corrected."
			else:
				CheckInfo = "no properties to correct."
				
			layout.label(popup_title)
			layout.label("Hierarchy names updated and " + CheckInfo)
			layout.separator()
			row = layout.row()
			col = row.column()
			for x in range(len(bpy.context.scene.potentialErrorList)):
				error = bpy.context.scene.potentialErrorList[x]
				
				myLine = col.box().split(percentage = 0.85 )
				#myLine = col.split(percentage = 0.85 )
				#----
				if error.type == 0:
					msgType = 'INFO'
					msgIcon = 'INFO'
				elif error.type == 1:
					msgType = 'WARNING'
					msgIcon = 'ERROR'
				elif error.type == 2:
					msgType = 'ERROR'
					msgIcon = 'CANCEL'
				#----
				errorFullMsg = msgType+": "+error.text
				myLine.label(text=errorFullMsg, icon=msgIcon)
				if error.correctRef != "None":
					props = myLine.operator("object.fixit", text=error.correctlabel)
					props.errorIndex = x

	
	class ExportForUnrealEngineButton(bpy.types.Operator):
		bl_label = "Export for UnrealEngine 4"
		bl_idname = "object.exportforunreal"
		bl_description = "Export all assets of this scene."

		def execute(self, context):
			scene = bpy.context.scene
			def GetIfOneTypeCheck():
				if (scene.static_export 
				or scene.skeletal_export 
				or scene.anin_export 
				or scene.pose_export 
				or scene.camera_export):
					return True
				else:
					return False

			if GetIfOneTypeCheck():
				#Primary check	if file is saved to avoid windows PermissionError  
				if bpy.data.is_saved:
					scene.UnrealExportedAssetsList.clear()
					start_time = time.process_time()
					bfu_exportasset.ExportForUnrealEngine()
					bfu_writetext.WriteAllTextFiles()
				
					if len(scene.UnrealExportedAssetsList) > 0:
						self.report({'INFO'}, "Export of "+str(len(scene.UnrealExportedAssetsList))+
						" asset(s) has been finalized in "+str(time.process_time()-start_time)+" sec. Look in console for more info.")
						print("========================= Exported asset(s) =========================")
						print("")
						for line in bfu_writetext.WriteExportLog().splitlines():
							print(line)
						print("")
						print("========================= ... =========================")
					else:
						self.report({'WARNING'}, "Not found assets. with \"Export and child\" properties.")
				else:
					self.report({'WARNING'}, "Please save this blend file before export")
			else:
				self.report({'WARNING'}, "No asset type is checked.")
			return {'FINISHED'}


	#Categories :
	bpy.types.Scene.static_export = bpy.props.BoolProperty(
		name = "StaticMesh(s)",
		description = "Check mark to export StaticMesh(es)",
		default = True
		)

	bpy.types.Scene.skeletal_export = bpy.props.BoolProperty(
		name = "SkeletalMesh(s)",
		description = "Check mark to export SkeletalMesh(es)",
		default = True
		)

	bpy.types.Scene.anin_export = bpy.props.BoolProperty(
		name = "Animation(s)",
		description = "Check mark to export Animation(s)",
		default = True
		)

	bpy.types.Scene.pose_export = bpy.props.BoolProperty(
		name = "Pose(s)",
		description = "Check mark to export Pose(s)",
		default = True
		)

	bpy.types.Scene.camera_export = bpy.props.BoolProperty(
		name = "Camera(s)",
		description = "Check mark to export Camera(s)",
		default = False
		)

	#Additional file
	bpy.types.Scene.text_exportLog = bpy.props.BoolProperty(
		name = "Export Log",
		description = "Check mark to write export log in file",
		default = True
		)
		
	bpy.types.Scene.text_ImportAssetScript = bpy.props.BoolProperty(
		name = "Import assets script",
		description = "Check mark to write import assets script in file",
		default = True
		)
		
	bpy.types.Scene.text_ImportSequenceScript = bpy.props.BoolProperty(
		name = "Import sequence script",
		description = "Check mark to write import sequence script in file",
		default = True
		)


	def draw(self, context):
		scn = context.scene

		#Categories :
		layout = self.layout
		row = layout.row()
		col = row.column()
		
		#Assets
		AssetsCol = row.column()
		AssetsCol.label("Asset types to export", icon='EXTERNAL_DATA')
		AssetsCol.prop(scn, 'static_export')
		AssetsCol.prop(scn, 'skeletal_export')
		AssetsCol.prop(scn, 'anin_export')
		AssetsCol.prop(scn, 'pose_export')
		AssetsCol.prop(scn, 'camera_export')
		layout.separator()
		#Additional file
		FileCol = row.column()
		FileCol.label("Additional file", icon='EXTERNAL_DATA')
		FileCol.prop(scn, 'text_exportLog')
		FileCol.prop(scn, 'text_ImportAssetScript')
		FileCol.prop(scn, 'text_ImportSequenceScript')

		#Feedback info :
		AssetNum = len(GetFinalAssetToExport())
		AssetInfo = layout.row().box().split(percentage = 0.75 )
		AssetFeedback = str(AssetNum) + " Asset(s) will be exported."
		AssetInfo.label( AssetFeedback, icon='INFO')
		AssetInfo.operator("object.showasset")
		#Export button :
		checkButton = layout.row()
		checkButton.operator("object.checkpotentialerror", icon='FILE_TICK')
		exportButton = layout.row()
		exportButton.scale_y = 2.0
		exportButton.operator("object.exportforunreal", icon='EXPORT')


#############################[...]#############################


def register():
    bpy.utils.register_module(__name__)

def unregister():
    bpy.utils.unregister_module(__name__)