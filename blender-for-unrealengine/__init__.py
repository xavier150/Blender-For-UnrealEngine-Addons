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
	'version': (0, 2, 3, 2), #Rev 0.2.3c
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
		CollectionProperty,
		)

from bpy.types import (
		Operator,
		)

import importlib
from . import bfu_ExportAsset
importlib.reload(bfu_ExportAsset)

from . import bfu_WriteText
importlib.reload(bfu_WriteText)

from . import bfu_Basics
importlib.reload(bfu_Basics)
from .bfu_Basics import *

from . import bfu_Utils
importlib.reload(bfu_Utils)
from .bfu_Utils import *


class BFU_AP_AddonPreferences(bpy.types.AddonPreferences):
	# this must match the addon name, use '__package__'
	# when defining this in a submodule of a python package.
	bl_idname = __name__

	skeletonRootBoneName = StringProperty(
		name='Skeleton root bone name',
		description='Name of the armature when exported. This is used to change the root bone name. If egal "Armature" Ue4 will remove the root bone but the animation will be 100 times smaller.',
		default="ArmatureRoot",
		)

	StaticSocketsImportedSize = FloatProperty(
		name='StaticMesh sockets import size',
		description='Size of the socket when imported in Unreal Engine',
		default=1.0,
		)

	SkeletalSocketsImportedSize = FloatProperty(
		name='SkeletalMesh sockets import size',
		description='Size of the socket when imported in Unreal Engine',
		default=0.01,
		)

	revertExportPath = BoolProperty(
		name='Revert all export path at each export',
		description='will remove the folder of the all export path at each export',
		default=True,
		)

	UseGeneratedScripts =  BoolProperty(
		name='Use generated script for import assets and sequencer.',
		description='If false the all properties that only works with import scripts will be disabled',
		default=True,
		)

	Use20TabScript = BoolProperty(
		name='Genrate import script for 20Tab python intergration',
		description='Genrate import script for 20Tab python intergration ( /!\ With vania python integration some features like StaticMesh Lod or SkeletalMesh Sockets integration do not work )',
		default=True,
		)



	def draw(self, context):
		layout = self.layout
		col = layout.column()
		col.prop(self, "skeletonRootBoneName")
		col.prop(self, "StaticSocketsImportedSize")
		col.prop(self, "SkeletalSocketsImportedSize")
		col.prop(self, "revertExportPath")
		col.prop(self, "UseGeneratedScripts")
		if self.UseGeneratedScripts == True:
			col.prop(self, "Use20TabScript")

class BFU_PT_ObjectProperties(bpy.types.Panel):
	#Is Object Properties panel

	bl_idname = "BFU_PT_ObjectProperties"
	bl_label = "Object Properties"
	bl_space_type = "VIEW_3D"
	bl_region_type = "TOOLS"
	bl_category = "Unreal Engine 4"

	bpy.types.Object.ExportEnum = EnumProperty(
		name = "Export type",
		description = "Export procedure",
		items = [
			("auto", "Auto", "Exports only if one of the parents is \"Export recursive\"", "KEY_HLT", 1),
			("export_recursive", "Export recursive", "Export self object and all children", "KEYINGSET", 2),
			("dont_export", "Not exported", "Will never export", "KEY_DEHLT", 3)
			]
		)

	bpy.types.Object.exportFolderName = StringProperty(
		name = "Sub folder name",
		description = 'Sub folder name. No Sub folder created if left empty',
		maxlen = 64,
		default = "",
		subtype = 'FILE_NAME'
		)

	bpy.types.Object.ExportAsAlembic = BoolProperty(
		name="Export as Alembic animation",
		description="If true this mesh will be exported as a Alembic animation",
		default=False
		)

	bpy.types.Object.ExportAsLod = BoolProperty(
		name="Export as lod?",
		description="If true this mesh will be exported as a level of detail for another mesh",
		default=False
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
		addon_prefs = bpy.context.user_preferences.addons["blender-for-unrealengine"].preferences

		if obj is not None:

			AssetType = layout.row()
			AssetType.prop(obj, 'name', text="", icon='OBJECT_DATA')
			AssetType.label(text='('+ GetAssetType(obj)+')') #Show asset type

			ExportType = layout.column()
			ExportType.prop(obj, 'ExportEnum')

			if obj.ExportEnum == "export_recursive":
				folderNameProperty = layout.column()
				folderNameProperty.prop(obj, 'exportFolderName', icon='FILE_FOLDER')

				if obj.type != "CAMERA":
					AlembicProp = layout.column()
					AlembicProp.prop(obj, 'ExportAsAlembic')
					if obj.ExportAsAlembic == True:
						AlembicProp.label(text="(Alembic animation are exported with scene position.)")
						AlembicProp.label(text="(Use import script for use origin position.)")
					else:
						if addon_prefs.UseGeneratedScripts == True:
							LodProp = layout.column()
							LodProp.prop(obj, 'ExportAsLod')

						if obj.type == "ARMATURE":
							AssetType2 = layout.column()
							AssetType2.prop(obj, "ForceStaticMesh") #Show asset type
							if GetAssetType(obj) == "SkeletalMesh":
								AssetType2.prop(obj, 'exportDeformOnly')
			layout.label(text='(No properties to show.)')

class BFU_PT_ObjectImportProperties(bpy.types.Panel):
	#Is Object Properties panel

	bl_idname = "BFU_PT_ObjectImportProperties"
	bl_label = "Object Import Properties"
	bl_space_type = "VIEW_3D"
	bl_region_type = "TOOLS"
	bl_category = "Unreal Engine 4"

	#Lod list
	bpy.types.Object.Ue4Lod1 = PointerProperty(
		name = "LOD1",
		description = "Target objet for level of detail 01",
		type = bpy.types.Object
		)

	bpy.types.Object.Ue4Lod2 = PointerProperty(
		name = "LOD2",
		description = "Target objet for level of detail 02",
		type = bpy.types.Object
		)

	bpy.types.Object.Ue4Lod3 = PointerProperty(
		name = "LOD3",
		description = "Target objet for level of detail 03",
		type = bpy.types.Object
		)

	bpy.types.Object.Ue4Lod4 = PointerProperty(
		name = "LOD4",
		description = "Target objet for level of detail 04",
		type = bpy.types.Object
		)

	bpy.types.Object.Ue4Lod5 = PointerProperty(
		name = "LOD5",
		description = "Target objet for level of detail 05",
		type = bpy.types.Object
		)

	#ImportUI
	#https://api.unrealengine.com/INT/API/Editor/UnrealEd/Factories/UFbxImportUI/index.html

	bpy.types.Object.CreatePhysicsAsset = BoolProperty(
		name = "Create PhysicsAsset",
		description = "If checked, create a PhysicsAsset when is imported",
		default=True
		)

	#StaticMeshImportData
	#https://api.unrealengine.com/INT/API/Editor/UnrealEd/Factories/UFbxStaticMeshImportData/index.html

	bpy.types.Object.UseStaticMeshLODGroup = BoolProperty(
		name = "",
		description = '',
		default=False
		)
	bpy.types.Object.StaticMeshLODGroup = StringProperty(
		name = "LOD Group",
		description = "The LODGroup to associate with this mesh when it is imported. Default: LevelArchitecture, SmallProp, LargeProp, Deco, Vista, Foliage, HighDetail" ,
		maxlen = 32,
		default = "SmallProp"
		)

	bpy.types.Object.UseStaticMeshLightMapRes = BoolProperty(
		name = "",
		description = '',
		default=False
		)
	bpy.types.Object.StaticMeshLightMapRes = IntProperty(
		name = "Light Map resolution",
		description = " This is the resolution of the light map" ,
		soft_max = 2048,
		soft_min = 16,
		max = 4096, #Max for unreal
		min = 4, #Min for unreal
		default = 16
		)

	bpy.types.Object.GenerateLightmapUVs = BoolProperty(
		name = "Generate LightmapUVs",
		description = "If checked, UVs for Lightmap will automatically be generated." ,
		default=True,
		)

	bpy.types.Object.AutoGenerateCollision = BoolProperty(
		name = "Auto Generate Collision",
		description = "If checked, collision will automatically be generated (ignored if custom collision is imported or used)." ,
		default=True,
		)

	#SkeletalMeshImportData
	#https://api.unrealengine.com/INT/API/Editor/UnrealEd/Factories/UFbxSkeletalMeshImportData/index.html

	#UFbxTextureImportData
	#https://api.unrealengine.com/INT/API/Editor/UnrealEd/Factories/UFbxTextureImportData/index.html

	bpy.types.Object.MaterialSearchLocation = EnumProperty(
		name = "Material search location",
		description = "Specify where we should search for matching materials when importing",
		#Vania python -> #https://docs.unrealengine.com/en-US/PythonAPI/class/MaterialSearchLocation.html?highlight=materialsearchlocation
		#20tab python -> http://api.unrealengine.com/INT/API/Editor/UnrealEd/Factories/EMaterialSearchLocation/index.html
		items = [
			("Local", "Local", "Search for matching material in local import folder only.", 1),
			("UnderParent", "UnderParent", "Search for matching material recursively from parent folder.", 2),
			("UnderRoot", "UnderRoot", "Search for matching material recursively from root folder.", 3),
			("AllAssets", "AllAssets", "Search for matching material in all assets folders.", 4)
			]
		)

	bpy.types.Object.CollisionTraceFlag = EnumProperty(
		name = "Collision Complexity",
		description = "Collision Trace Flag",
		#Vania python -> https://docs.unrealengine.com/en-US/PythonAPI/class/CollisionTraceFlag.html
		#20tab python ->https://api.unrealengine.com/INT/API/Runtime/Engine/PhysicsEngine/ECollisionTraceFlag/index.html
		items = [
			("CTF_UseDefault", "Project Default", "Create only complex shapes (per poly). Use complex shapes for all scene queries and collision tests. Can be used in simulation for static shapes only (i.e can be collided against but not moved through forces or velocity.", 1),
			("CTF_UseSimpleAndComplex", "Use Simple And Complex", "Use project physics settings (DefaultShapeComplexity)", 2),
			("CTF_UseSimpleAsComplex", "Use Simple as Complex", "Create both simple and complex shapes. Simple shapes are used for regular scene queries and collision tests. Complex shape (per poly) is used for complex scene queries.", 3),
			("CTF_UseComplexAsSimple", "Use Complex as Simple", "Create only simple shapes. Use simple shapes for all scene queries and collision tests.", 4)
			]
		)


	def draw(self, context):


		layout = self.layout
		obj = context.object
		addon_prefs = bpy.context.user_preferences.addons["blender-for-unrealengine"].preferences

		if addon_prefs.UseGeneratedScripts == True:
			if obj is not None:
				if obj.ExportEnum == "export_recursive":

					#Lod selection
					if obj.ExportAsLod == False:
						if GetAssetType(obj) == "StaticMesh" or GetAssetType(obj) == "SkeletalMesh":
							LodList = layout.column()
							LodList.prop(obj, 'Ue4Lod1')
							LodList.prop(obj, 'Ue4Lod2')
							LodList.prop(obj, 'Ue4Lod3')
							LodList.prop(obj, 'Ue4Lod4')
							LodList.prop(obj, 'Ue4Lod5')

					#MaterialSearchLocation
					if obj.ExportAsLod == False:
						if GetAssetType(obj) == "StaticMesh" or GetAssetType(obj) == "SkeletalMesh" or GetAssetType(obj) == "Alembic":
							MaterialSearchLocation = layout.row()
							MaterialSearchLocation.prop(obj, 'MaterialSearchLocation')

					#StaticMesh prop
					if GetAssetType(obj) == "StaticMesh":
						if obj.ExportAsLod == False:
							StaticMeshLODGroup = layout.row()
							StaticMeshLODGroup.prop(obj, 'UseStaticMeshLODGroup', text="")
							StaticMeshLODGroupChild = StaticMeshLODGroup.column()
							StaticMeshLODGroupChild.enabled = obj.UseStaticMeshLODGroup
							StaticMeshLODGroupChild.prop(obj, 'StaticMeshLODGroup')
							StaticMeshLODGroupChild.prop(obj, 'CollisionTraceFlag')

						StaticMeshLightMapRes = layout.row()
						StaticMeshLightMapRes.prop(obj, 'UseStaticMeshLightMapRes', text="")
						StaticMeshLightMapResChild = StaticMeshLightMapRes.column()
						StaticMeshLightMapResChild.enabled = obj.UseStaticMeshLightMapRes
						StaticMeshLightMapResChild.prop(obj, 'StaticMeshLightMapRes')

						GenerateLightmapUVs = layout.row()
						GenerateLightmapUVs.prop(obj, 'GenerateLightmapUVs')

						if obj.ExportAsLod == False:
							AutoGenerateCollision = layout.row()
							AutoGenerateCollision.prop(obj, 'AutoGenerateCollision')


					#SkeletalMesh prop
					if GetAssetType(obj) == "SkeletalMesh":
						if obj.ExportAsLod == False:
							CreatePhysicsAsset = layout.row()
							CreatePhysicsAsset.prop(obj, "CreatePhysicsAsset")

				else:
					layout.label(text='(No properties to show.)')
			else:
				layout.label(text='(No properties to show.)')
		else:
			layout.label(text='(Generated scripts are deactivated.)')

class BFU_OT_ObjExportAction(bpy.types.PropertyGroup):
	name = StringProperty(name="Action data name", default="Unknown")
	use = BoolProperty(name="use this action", default=False)


class BFU_PT_AnimProperties(bpy.types.Panel):
	#Is Animation Properties panel

	bl_idname = "BFU_PT_AnimProperties"
	bl_label = "Animation Properties"
	bl_space_type = "VIEW_3D"
	bl_region_type = "TOOLS"
	bl_category = "Unreal Engine 4"

	#Animation :

	class BFU_UL_ACTIONExportTarget(bpy.types.UIList):
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

	bpy.types.Object.exportActionEnum = EnumProperty(
		name = "Action to export",
		description = "Export procedure for actions (Animations and poses)",
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
		description = "Indicate the prefix of the actions that must be exported",
		maxlen = 32,
		default = "Example_",
		)

	bpy.types.Object.AnimStartEndTimeEnum = EnumProperty(
		name = "Animation start/end time",
		description = "Set when animation starts and end",
		items = [
			("with_keyframes", "Auto", "The time will be defined according to the first and the last frame", "KEYTYPE_KEYFRAME_VEC", 1),
			("with_sceneframes", "Scene time", "Time will be equal to the scene time", "SCENE_DATA", 2),
			("with_customframes", "Custom time", 'The time of all the animations of this object is defined by you. Use "AnimCustomStartTime" and "AnimCustomEndTime"', "HAND", 3),
			]
		)

	bpy.types.Object.AddOneAdditionalFramesAtTheEnd = BoolProperty(
		name = "Additional end frame",
		description = "If checked, the animation will have an additional frame at the end. This is recommended for the sequences but it is not recommended with the cycles",
		default=False
	)

	bpy.types.Object.AnimCustomStartTime = IntProperty(
		name = "Custom start time",
		description = "Set when animation start",
		default=0
		)

	bpy.types.Object.AnimCustomEndTime = IntProperty(
		name = "Custom end time",
		description = "Set when animation end",
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

	bpy.types.Object.ExportNLA = BoolProperty(
		name="Export NLA (Nonlinear Animation)",
		description="If checked, exports the all animation of the scene with the NLA",
		default=False
		)

	bpy.types.Object.NLAAnimName = StringProperty(
		name = "NLA export name",
		description = 'Export NLA name',
		maxlen = 64,
		default = "NLA_animation",
		subtype = 'FILE_NAME'
		)

	class BFU_OT_UpdateObjActionButton(Operator):
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

	class BFU_OT_ShowActionToExport(Operator):
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
					row.label(text="- "+action.name+GetActionType(action))
			bpy.context.window_manager.popup_menu(draw, title=popup_title, icon='ACTION')
			return {'FINISHED'}


	def draw(self, context):

		layout = self.layout
		obj = context.object
		if obj is not None:
			if obj.ExportEnum == "export_recursive" and	obj.ExportAsLod == False:
				if GetAssetType(obj) == "SkeletalMesh" or GetAssetType(obj) == "Camera" or GetAssetType(obj) == "Alembic":

					#Action time
					if obj.type != "CAMERA":
						ActionTimeProperty = layout.column()
						ActionTimeProperty.prop(obj, 'AnimStartEndTimeEnum')
						if obj.AnimStartEndTimeEnum == "with_customframes":
							ActionTimePropertyChild=ActionTimeProperty = layout.row()
							ActionTimePropertyChild.prop(obj, 'AnimCustomStartTime')
							ActionTimePropertyChild.prop(obj, 'AnimCustomEndTime')
						ActionTimeProperty.prop(obj, 'AddOneAdditionalFramesAtTheEnd')
					else:
						layout.label(text="Note: animation start/end use scene frames with the camera for the sequencer.")

					if GetAssetType(obj) == "SkeletalMesh":
						#Action list
						ActionListProperty = layout.column()
						ActionListProperty.prop(obj, 'exportActionEnum')
						if obj.exportActionEnum == "export_specific_list":
							ActionListProperty.template_list(
								"BFU_UL_ACTIONExportTarget", "",  # type and unique id
								obj, "exportActionList",  # pointer to the CollectionProperty
								obj, "active_ObjectAction",	 # pointer to the active identifier
								maxrows=5,
								rows=5
							)
							ActionListProperty.operator("object.updateobjaction", icon='RECOVER_LAST')
						if obj.exportActionEnum == "export_specific_prefix":
							ActionListProperty.prop(obj, 'PrefixNameToExport')

					#Action fbx properties
					if GetAssetType(obj) != "Alembic":
						propsFbx = layout.row()
						propsFbx.prop(obj, 'SampleAnimForExport')
						propsFbx.prop(obj, 'SimplifyAnimForExport')

					#Armature export action list feedback
					if GetAssetType(obj) == "SkeletalMesh":
						ArmaturePropertyInfo = layout.row().box().split(percentage = 0.75 )
						ActionNum = len(GetActionToExport(obj))
						actionFeedback = str(ActionNum) + " Action(s) will be exported with this armature."
						ArmaturePropertyInfo.label(text=actionFeedback, icon='INFO')
						ArmaturePropertyInfo.operator("object.showobjaction")
						layout.label(text='Note: The Action with only one frame are exported like Pose.')

					if GetAssetType(obj) == "SkeletalMesh":
						NLAAnim = layout.row()
						NLAAnim.prop(obj, 'ExportNLA')
						NLAAnimChild = NLAAnim.column()
						NLAAnimChild.enabled = obj.ExportNLA
						NLAAnimChild.prop(obj, 'NLAAnimName')
				else:
					layout.label(text='(This assets is not a SkeletalMesh or Camera)')
			else:
				layout.label(text='(No properties to show.)')


class BFU_PT_AvancedObjectProperties(bpy.types.Panel):
	#Is Avanced object properties panel

	bl_idname = "BFU_PT_AvancedObjectProperties"
	bl_label = "Avanced object properties panel"
	bl_space_type = "VIEW_3D"
	bl_region_type = "TOOLS"
	bl_category = "Unreal Engine 4"

	bpy.types.Object.exportAxisForward = EnumProperty(
		name="Axis Forward",
		items=[
			('X', "X Forward", ""),
			('Y', "Y Forward", ""),
			('Z', "Z Forward", ""),
			('-X', "-X Forward", ""),
			('-Y', "-Y Forward", ""),
			('-Z', "-Z Forward", ""),
			],
		default='-Z',
		)

	bpy.types.Object.exportAxisUp = EnumProperty(
		name="Axis Up",
		items=[
			('X', "X Up", ""),
			('Y', "Y Up", ""),
			('Z', "Z Up", ""),
			('-X', "-X Up", ""),
			('-Y', "-Y Up", ""),
			('-Z', "-Z Up", ""),
			],
		default='Y',
		)

	bpy.types.Object.exportGlobalScale = IntProperty(
		name="Global scale",
		description="Scale, change is not recommended with SkeletalMesh.",
		default=1
		)

	def draw(self, context):
		scn = context.scene
		layout = self.layout
		obj = context.object
		if obj is not None:
			if obj.ExportEnum == "export_recursive":
				AxisProperty = layout.column()
				AxisProperty.prop(obj, 'exportGlobalScale')
				AxisProperty.prop(obj, 'exportAxisForward')
				AxisProperty.prop(obj, 'exportAxisUp')
		else:
			layout.label(text='(No properties to show.)')


class BFU_PT_CollisionsAndSockets(bpy.types.Panel):
	#Is Collisions And Sockets panel

	bl_idname = "BFU_PT_CollisionsAndSockets"
	bl_label = "Collisions And Sockets"
	bl_space_type = "VIEW_3D"
	bl_region_type = "TOOLS"
	bl_category = "Unreal Engine 4"

	class BFU_OT_ConvertToCollisionButtonBox(Operator):
		bl_label = "Convert to box (UBX)"
		bl_idname = "object.converttoboxcollision"
		bl_description = "Convert selected mesh(es) to Unreal collision ready for export (Boxes type)"

		def execute(self, context):
			ConvertedObj = Ue4SubObj_set("Box")
			if len(ConvertedObj) > 0 :
				self.report({'INFO'}, str(len(ConvertedObj)) + " object(s) of the selection have be converted to UE4 Box collisions." )
			else :
				self.report({'WARNING'}, "Please select two objects. (Active object is the owner of the collision)")
			return {'FINISHED'}


	class BFU_OT_ConvertToCollisionButtonCapsule(Operator):
		bl_label = "Convert to capsule (UCP)"
		bl_idname = "object.converttocapsulecollision"
		bl_description = "Convert selected mesh(es) to Unreal collision ready for export (Capsules type)"

		def execute(self, context):
			ConvertedObj = Ue4SubObj_set("Capsule")
			if len(ConvertedObj) > 0 :
				self.report({'INFO'}, str(len(ConvertedObj)) + " object(s) of the selection have be converted to UE4 Capsule collisions." )
			else :
				self.report({'WARNING'}, "Please select two objects. (Active object is the owner of the collision)")
			return {'FINISHED'}


	class BFU_OT_ConvertToCollisionButtonSphere(Operator):
		bl_label = "Convert to sphere (USP)"
		bl_idname = "object.converttospherecollision"
		bl_description = "Convert selected mesh(es) to Unreal collision ready for export (Spheres type)"

		def execute(self, context):
			ConvertedObj = Ue4SubObj_set("Sphere")
			if len(ConvertedObj) > 0 :
				self.report({'INFO'}, str(len(ConvertedObj)) + " object(s) of the selection have be converted to UE4 Sphere collisions." )
			else :
				self.report({'WARNING'}, "Please select two objects. (Active object is the owner of the collision)")
			return {'FINISHED'}


	class BFU_OT_ConvertToCollisionButtonConvex(Operator):
		bl_label = "Convert to convex shape (UCX)"
		bl_idname = "object.converttoconvexcollision"
		bl_description = "Convert selected mesh(es) to Unreal collision ready for export (Convex shapes type)"

		def execute(self, context):
			ConvertedObj = Ue4SubObj_set("Convex")
			if len(ConvertedObj) > 0 :
				self.report({'INFO'}, str(len(ConvertedObj)) + " object(s) of the selection have be converted to UE4 Convex Shape collisions.")
			else :
				self.report({'WARNING'}, "Please select two objects. (Active object is the owner of the collision)")
			return {'FINISHED'}


	class BFU_OT_ConvertToStaticSocketButton(Operator):
		bl_label = "Convert to StaticMesh socket"
		bl_idname = "object.converttostaticsocket"
		bl_description = "Convert selected Empty(s) to Unreal sockets ready for export (StaticMesh)"

		def execute(self, context):
			ConvertedObj = Ue4SubObj_set("ST_Socket")
			if len(ConvertedObj) > 0 :
				self.report({'INFO'}, str(len(ConvertedObj)) + " object(s) of the selection have be converted to to UE4 Socket." )
			else :
				self.report({'WARNING'}, "Please select two objects. (Active object is the owner of the socket)")
			return {'FINISHED'}

	class BFU_OT_ConvertToSkeletalSocketButton(Operator):
		bl_label = "Convert to SkeletalMesh socket"
		bl_idname = "object.converttoskeletalsocket"
		bl_description = "Convert selected Empty(s) to Unreal sockets ready for export (SkeletalMesh)"

		def execute(self, context):
			ConvertedObj = Ue4SubObj_set("SK_Socket")
			if len(ConvertedObj) > 0 :
				self.report({'INFO'}, str(len(ConvertedObj)) + " object(s) of the selection have be converted to to UE4 Socket." )
			else :
				self.report({'WARNING'}, "Please select two objects. (Active object is the owner of the socket)")
			return {'FINISHED'}

	def draw(self, context):

		addon_prefs = bpy.context.user_preferences.addons["blender-for-unrealengine"].preferences

		def ActiveModeIs(targetMode): #Return True is active mode ==
			obj = bpy.context.active_object
			if obj is not None:
				if obj.mode == targetMode:
					return True
			return False

		def ActiveTypeIs(targetType): #Return True is active type ==
			obj = bpy.context.active_object
			if obj is not None:
				if obj.type == targetType:
					return True
			return False


		def FoundTypeInSelect(targetType): #Return True if a specific type is found
			for obj in bpy.context.selected_objects:
				if obj != bpy.context.active_object:
					if obj.type == targetType:
						return True
			return False

		layout = self.layout
		layout.label(text="Convert selected object to Unreal collision or socket", icon='PHYSICS')

		layout.label(text="Select your collider shape(s) or Empty(s) then the owner object.")
		convertButtons = layout.row().split(percentage = 0.80 )
		convertStaticCollisionButtons = convertButtons.column()
		convertStaticCollisionButtons.enabled = ActiveModeIs("OBJECT") and ActiveTypeIs("MESH") and FoundTypeInSelect("MESH")
		convertStaticCollisionButtons.operator("object.converttoboxcollision", icon='MESH_CUBE')
		convertStaticCollisionButtons.operator("object.converttoconvexcollision", icon='MESH_ICOSPHERE')
		convertStaticCollisionButtons.operator("object.converttocapsulecollision", icon='MESH_CAPSULE')
		convertStaticCollisionButtons.operator("object.converttospherecollision", icon='SOLID')

		convertButtons = self.layout.row().split(percentage = 0.80 )
		convertStaticSocketButtons = convertButtons.column()
		convertStaticSocketButtons.enabled = ActiveModeIs("OBJECT") and ActiveTypeIs("MESH") and FoundTypeInSelect("EMPTY")
		convertStaticSocketButtons.operator("object.converttostaticsocket", icon='OUTLINER_DATA_EMPTY')

		if addon_prefs.UseGeneratedScripts == True:
			layout.label(text="Select the Empty(s) then the owner bone in PoseMode.")
			convertButtons = self.layout.row().split(percentage = 0.80 )
			convertSkeletalSocketButtons = convertButtons.column()
			convertSkeletalSocketButtons.enabled = ActiveModeIs("POSE") and ActiveTypeIs("ARMATURE") and FoundTypeInSelect("EMPTY")
			convertSkeletalSocketButtons.operator("object.converttoskeletalsocket", icon='OUTLINER_DATA_EMPTY')


class BFU_PT_Nomenclature(bpy.types.Panel):
	#Is FPS Export panel

	bl_idname = "BFU_PT_Nomenclature"
	bl_label = "Nomenclature"
	bl_space_type = "VIEW_3D"
	bl_region_type = "TOOLS"
	bl_category = "Unreal Engine 4"


	class BFU_MT_NomenclaturePresets(bpy.types.Menu):
		bl_label = 'My Presets'
		preset_subdir = 'blender-for-unrealengine/nomenclature-presets'
		preset_operator = 'script.execute_preset'
		draw = bpy.types.Menu.draw_preset

	from bl_operators.presets import AddPresetBase

	class BFU_OT_AddNomenclaturePreset(AddPresetBase, Operator):
		bl_idname = 'object.add_preset'
		bl_label = 'Add A preset'
		preset_menu = 'BFU_MT_NomenclaturePresets'

		# Common variable used for all preset values
		preset_defines = [
							'obj = bpy.context.object',
							'scene = bpy.context.scene'
						 ]

		# Properties to store in the preset
		preset_values = [
							'scene.static_prefix_export_name',
							'scene.skeletal_prefix_export_name',
							'scene.alembic_prefix_export_name',
							'scene.anim_prefix_export_name',
							'scene.pose_prefix_export_name',
							'scene.camera_prefix_export_name',
							'scene.anim_subfolder_name',
							'scene.export_static_file_path',
							'scene.export_skeletal_file_path',
							'scene.export_alembic_file_path',
							'scene.export_camera_file_path',
							'scene.export_other_file_path',
							'scene.file_export_log_name',
							'scene.file_import_asset_script_name',
							'scene.file_import_sequencer_script_name',
						]

		# Directory to store the presets
		preset_subdir = 'blender-for-unrealengine/nomenclature-presets'

	#Prefix
	bpy.types.Scene.static_prefix_export_name = bpy.props.StringProperty(
		name = "StaticMesh Prefix",
		description = "Prefix of staticMesh",
		maxlen = 32,
		default = "SM_")

	bpy.types.Scene.skeletal_prefix_export_name = bpy.props.StringProperty(
		name = "SkeletalMesh Prefix ",
		description = "Prefix of SkeletalMesh",
		maxlen = 32,
		default = "SK_")

	bpy.types.Scene.alembic_prefix_export_name = bpy.props.StringProperty(
		name = "Alembic Prefix ",
		description = "Prefix of Alembic (SkeletalMesh in unreal)",
		maxlen = 32,
		default = "SK_")

	bpy.types.Scene.anim_prefix_export_name = bpy.props.StringProperty(
		name = "AnimationSequence Prefix",
		description = "Prefix of AnimationSequence",
		maxlen = 32,
		default = "Anim_")

	bpy.types.Scene.pose_prefix_export_name = bpy.props.StringProperty(
		name = "AnimationSequence(Pose) Prefix",
		description = "Prefix of AnimationSequence with only one frame",
		maxlen = 32,
		default = "Pose_")

	bpy.types.Scene.camera_prefix_export_name = bpy.props.StringProperty(
		name = "Camera anim Prefix",
		description = "Prefix of camera animations",
		maxlen = 32,
		default = "Cam_")

	#Sub folder
	bpy.types.Scene.anim_subfolder_name = bpy.props.StringProperty(
		name = "Animations sub folder name",
		description = "name of sub folder for animations",
		maxlen = 32,
		default = "Anim")

	#File path
	bpy.types.Scene.export_static_file_path = bpy.props.StringProperty(
		name = "StaticMesh export file path",
		description = "Choose a directory to export StaticMesh(s)",
		maxlen = 512,
		default = os.path.join("//","ExportedFbx","StaticMesh"),
		subtype = 'DIR_PATH')

	bpy.types.Scene.export_skeletal_file_path = bpy.props.StringProperty(
		name = "SkeletalMesh export file path",
		description = "Choose a directory to export SkeletalMesh(s)",
		maxlen = 512,
		default = os.path.join("//","ExportedFbx","SkeletalMesh"),
		subtype = 'DIR_PATH')

	bpy.types.Scene.export_alembic_file_path = bpy.props.StringProperty(
		name = "Alembic export file path",
		description = "Choose a directory to export Alembic(s)",
		maxlen = 512,
		default = os.path.join("//","ExportedFbx","Alembic"),
		subtype = 'DIR_PATH')

	bpy.types.Scene.export_camera_file_path = bpy.props.StringProperty(
		name = "Camera export file path",
		description = "Choose a directory to export Camera(s)",
		maxlen = 512,
		default = os.path.join("//","ExportedFbx","Sequencer"),
		subtype = 'DIR_PATH')

	bpy.types.Scene.export_other_file_path = bpy.props.StringProperty(
		name = "Other export file path",
		description = "Choose a directory to export text file and other",
		maxlen = 512,
		default = os.path.join("//","ExportedFbx"),
		subtype = 'DIR_PATH')

	#File name
	bpy.types.Scene.file_export_log_name = bpy.props.StringProperty(
		name = "Export log name",
		description = "Export log name",
		maxlen = 64,
		default = "ExportLog.txt")

	bpy.types.Scene.file_import_asset_script_name = bpy.props.StringProperty(
		name = "Import asset script name",
		description = "Import asset script name",
		maxlen = 64,
		default = "ImportAssetScript.py")

	bpy.types.Scene.file_import_sequencer_script_name = bpy.props.StringProperty(
		name = "Import sequencer script Name",
		description = "Import sequencer script name",
		maxlen = 64,
		default = "ImportSequencerScript.py")


	def draw(self, context):
		scn = context.scene
		addon_prefs = bpy.context.user_preferences.addons["blender-for-unrealengine"].preferences

		#Presets
		row = self.layout.row(align=True)
		row.menu('BFU_MT_NomenclaturePresets', text='Presets')
		row.operator('object.add_preset', text='', icon='ZOOMIN')
		row.operator('object.add_preset', text='', icon='ZOOMOUT').remove_active = True

		#Prefix
		propsPrefix = self.layout.row()
		propsPrefix = propsPrefix.column()
		propsPrefix.prop(scn, 'static_prefix_export_name', icon='OBJECT_DATA')
		propsPrefix.prop(scn, 'skeletal_prefix_export_name', icon='OBJECT_DATA')
		propsPrefix.prop(scn, 'alembic_prefix_export_name', icon='OBJECT_DATA')
		propsPrefix.prop(scn, 'anim_prefix_export_name', icon='OBJECT_DATA')
		propsPrefix.prop(scn, 'pose_prefix_export_name', icon='OBJECT_DATA')
		propsPrefix.prop(scn, 'camera_prefix_export_name', icon='OBJECT_DATA')

		#Sub folder
		propsSub = self.layout.row()
		propsSub = propsSub.column()
		propsSub.prop(scn, 'anim_subfolder_name', icon='FILE_FOLDER')

		#File path
		filePath = self.layout.row()
		filePath = filePath.column()
		filePath.prop(scn, 'export_static_file_path')
		filePath.prop(scn, 'export_skeletal_file_path')
		filePath.prop(scn, 'export_alembic_file_path')
		filePath.prop(scn, 'export_camera_file_path')
		filePath.prop(scn, 'export_other_file_path')

		#File name
		fileName = self.layout.row()
		fileName = fileName.column()
		fileName.prop(scn, 'file_export_log_name', icon='FILE')
		if addon_prefs.UseGeneratedScripts == True:
			fileName.prop(scn, 'file_import_asset_script_name', icon='FILE')
			fileName.prop(scn, 'file_import_sequencer_script_name', icon='FILE')


class BFU_PT_ImportScript(bpy.types.Panel):
	#Is Import script panel

	bl_idname = "BFU_PT_ImportScript"
	bl_label = "Import Script"
	bl_space_type = "VIEW_3D"
	bl_region_type = "TOOLS"
	bl_category = "Unreal Engine 4"

	bpy.types.Scene.unreal_import_location = bpy.props.StringProperty(
		name = "Unreal import location",
		description = "Unreal assets import location in /Game/",
		maxlen = 512,
		default = 'ImportedFbx')

	bpy.types.Scene.unreal_levelsequence_import_location = bpy.props.StringProperty(
		name = "Unreal sequencer import location",
		description = "Unreal sequencer import location in /Game/",
		maxlen = 512,
		default = r'ImportedFbx/Sequencer')

	bpy.types.Scene.unreal_levelsequence_name = bpy.props.StringProperty(
		name = "Unreal sequencer name",
		description = "Unreal sequencer name",
		maxlen = 512,
		default = 'MySequence')

	def draw(self, context):
		scn = context.scene
		addon_prefs = bpy.context.user_preferences.addons["blender-for-unrealengine"].preferences

		#Sub folder
		if addon_prefs.UseGeneratedScripts == True:
			propsSub = self.layout.row()
			propsSub = propsSub.column()
			propsSub.prop(scn, 'unreal_import_location', icon='FILE_FOLDER')
			propsSub.prop(scn, 'unreal_levelsequence_import_location', icon='FILE_FOLDER')
			propsSub.prop(scn, 'unreal_levelsequence_name', icon='FILE')
		else:
			self.layout.label(text='(Generated scripts are deactivated.)')


class BFU_OT_UnrealExportedAsset(bpy.types.PropertyGroup):
	#[AssetName , AssetType , ExportPath, ExportTime]
	assetName = StringProperty(default="None")
	assetType = StringProperty(default="None") #return from GetAssetType()
	exportPath = StringProperty(default="None")
	exportTime = FloatProperty(default=0)
	object = PointerProperty(type=bpy.types.Object)


class BFU_OT_UnrealPotentialError(bpy.types.PropertyGroup):
	type = IntProperty(default=0) #0:Info, 1:Warning, 2:Error
	object = PointerProperty(type=bpy.types.Object)
	vertexErrorType = StringProperty(default="None") #0:Info, 1:Warning, 2:Error
	itemName = StringProperty(default="None")
	text = StringProperty(default="Unknown")
	correctRef = StringProperty(default="None")
	correctlabel = StringProperty(default="Fix it !")
	correctDesc = StringProperty(default="Correct target error")


class BFU_PT_Export(bpy.types.Panel):
	#Is Export panel

	bl_idname = "BFU_PT_Export"
	bl_label = "Export"
	bl_space_type = "VIEW_3D"
	bl_region_type = "TOOLS"
	bl_category = "Unreal Engine 4"


	class BFU_OT_ShowAssetToExport(Operator):
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
					if asset.obj is not None:
						if asset.action is not None:
							if (type(asset.action) is bpy.types.Action): #Action name
								action = asset.action.name
							elif (type(asset.action) is bpy.types.AnimData): #Nonlinear name
								action = asset.obj.NLAAnimName
							else:
								action = "..."
							row.label(text="- ["+asset.obj.name+"] --> "+action+" ("+asset[2]+")")
						else:
							row.label(text="- "+asset.obj.name+" ("+asset.type+")")
					else:
						row.label(text="- ("+asset.type+")")
			bpy.context.window_manager.popup_menu(draw, title=popup_title, icon='EXTERNAL_DATA')
			return {'FINISHED'}


	class BFU_OT_CheckPotentialErrorPopup(Operator):
		bl_label = "Check potential errors"
		bl_idname = "object.checkpotentialerror"
		bl_description = "Check potential errors"
		correctedProperty = 0

		class BFU_OT_FixitTarget(Operator):
			bl_label = "Fix it !"
			bl_idname = "object.fixit_objet"
			bl_description = "Correct target error"
			errorIndex = bpy.props.IntProperty(default=-1)

			def execute(self, context):
				result = TryToCorrectPotentialError(self.errorIndex)
				self.report({'INFO'}, result)
				return {'FINISHED'}

		class BFU_OT_SelectObjetButton(Operator):
			bl_label = "Select"
			bl_idname = "object.select_error_objet"
			bl_description = "Select target objet."
			errorIndex = bpy.props.IntProperty(default=-1)

			def execute(self, context):
				result = SelectPotentialErrorObject(self.errorIndex)
				return {'FINISHED'}

		class BFU_OT_SelectVertexButton(Operator):
			bl_label = "Select(Vertex)"
			bl_idname = "object.select_error_vertex"
			bl_description = "Select target vertex."
			errorIndex = bpy.props.IntProperty(default=-1)

			def execute(self, context):
				result = SelectPotentialErrorVertex(self.errorIndex)
				return {'FINISHED'}

		def execute(self, context):
			self.correctedProperty = CorrectBadProperty()
			UpdateNameHierarchy()
			UpdateUnrealPotentialError()
			return {'FINISHED'}

		def invoke(self, context, event):
			self.correctedProperty = CorrectBadProperty()
			UpdateNameHierarchy()
			UpdateUnrealPotentialError()
			wm = context.window_manager
			return wm.invoke_popup(self, width = 1020)

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

			layout.label(text=popup_title)
			layout.label(text="Hierarchy names updated and " + CheckInfo)
			layout.separator()
			row = layout.row()
			col = row.column()
			for x in range(len(bpy.context.scene.potentialErrorList)):
				error = bpy.context.scene.potentialErrorList[x]

				myLine = col.box().split(percentage = 0.85 )
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
				TextLine = myLine.column()
				splitedText = errorFullMsg.split("\n")

				for text, Line in enumerate(splitedText):
					if (text<1):
						TextLine.label(text=Line, icon=msgIcon)
					else:
						TextLine.label(text=Line)

				ButtonLine = myLine.column()
				if (error.correctRef != "None"):
					props = ButtonLine.operator("object.fixit_objet", text=error.correctlabel)
					props.errorIndex = x
				if (error.object is not None):
					props = ButtonLine.operator("object.select_error_objet")
					props.errorIndex = x
					if (error.vertexErrorType != "None"):
						props = ButtonLine.operator("object.select_error_vertex")
						props.errorIndex = x


	class BFU_OT_ExportForUnrealEngineButton(Operator):
		bl_label = "Export for UnrealEngine 4"
		bl_idname = "object.exportforunreal"
		bl_description = "Export all assets of this scene."

		def execute(self, context):
			scene = bpy.context.scene
			def GetIfOneTypeCheck():
				if (scene.static_export
				or scene.skeletal_export
				or scene.anin_export
				or scene.alembic_export
				or scene.camera_export):
					return True
				else:
					return False

			if GetIfOneTypeCheck():
				#Primary check	if file is saved to avoid windows PermissionError
				if bpy.data.is_saved:
					scene.UnrealExportedAssetsList.clear()
					start_time = time.process_time()
					UpdateNameHierarchy()
					bfu_ExportAsset.ExportForUnrealEngine()
					bfu_WriteText.WriteAllTextFiles()

					if len(scene.UnrealExportedAssetsList) > 0:
						self.report({'INFO'}, "Export of "+str(len(scene.UnrealExportedAssetsList))+
						" asset(s) has been finalized in "+str(time.process_time()-start_time)+" sec. Look in console for more info.")
						print("========================= Exported asset(s) =========================")
						print("")
						for line in bfu_WriteText.WriteExportLog().splitlines():
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

	bpy.types.Scene.alembic_export = bpy.props.BoolProperty(
		name = "Alembic animation(s)",
		description = "Check mark to export Alembic animation(s)",
		default = False
		)

	bpy.types.Scene.camera_export = bpy.props.BoolProperty(
		name = "Camera(s)",
		description = "Check mark to export Camera(s)",
		default = False
		)

	#Additional file
	bpy.types.Scene.text_ExportLog = bpy.props.BoolProperty(
		name = "Export Log",
		description = "Check mark to write export log file",
		default = True
		)

	bpy.types.Scene.text_ImportAssetScript = bpy.props.BoolProperty(
		name = "Import assets script",
		description = "Check mark to write import asset script file",
		default = True
		)

	bpy.types.Scene.text_ImportSequenceScript = bpy.props.BoolProperty(
		name = "Import sequence script",
		description = "Check mark to write import sequencer script file",
		default = True
		)

	#exportProperty
	bpy.types.Scene.export_ExportOnlySelected = bpy.props.BoolProperty(
		name = "Export only select",
		description = "Check mark to export only selected export group. (export_recursive objects and auto childs) " ,
		default = False
		)


	def draw(self, context):
		scn = context.scene

		#Categories :
		layout = self.layout
		row = layout.row()
		col = row.column()

		#Assets
		AssetsCol = row.column()
		AssetsCol.label(text="Asset types to export", icon='PACKAGE')
		AssetsCol.prop(scn, 'static_export')
		AssetsCol.prop(scn, 'skeletal_export')
		AssetsCol.prop(scn, 'anin_export')
		AssetsCol.prop(scn, 'alembic_export')
		AssetsCol.prop(scn, 'camera_export')
		layout.separator()
		#Additional file
		FileCol = row.column()
		FileCol.label(text="Additional file", icon='PACKAGE')
		FileCol.prop(scn, 'text_ExportLog')
		FileCol.prop(scn, 'text_ImportAssetScript')
		FileCol.prop(scn, 'text_ImportSequenceScript')


		#Feedback info :
		AssetNum = len(GetFinalAssetToExport())
		AssetInfo = layout.row().box().split(percentage = 0.75 )
		AssetFeedback = str(AssetNum) + " Asset(s) will be exported."
		AssetInfo.label(text=AssetFeedback, icon='INFO')
		AssetInfo.operator("object.showasset")

		#Export button :
		checkButton = layout.row()
		checkButton.operator("object.checkpotentialerror", icon='FILE_TICK')

		#exportProperty
		exportOnlySelect = layout.row()
		exportOnlySelect.prop(scn, 'export_ExportOnlySelected')

		exportButton = layout.row()
		exportButton.scale_y = 2.0
		exportButton.operator("object.exportforunreal", icon='EXPORT')


class BFU_PT_Clipboard(bpy.types.Panel):
	#Is Clipboard panel

	bl_idname = "BFU_PT_Clipboard"
	bl_label = "Clipboard Copy"
	bl_space_type = "VIEW_3D"
	bl_region_type = "TOOLS"
	bl_category = "Unreal Engine 4"


	class BFU_OT_CopyImportAssetScriptCommand(Operator):
		bl_label = "ImportAssetScript"
		bl_idname = "object.copy_importassetscript_command"
		bl_description = "Copy Import Asset Script command"

		def execute(self, context):
			scn = context.scene
			setWindowsClipboard(GetImportAssetScriptCommand())
			self.report({'INFO'}, "command for "+scn.file_import_asset_script_name+" copied")
			return {'FINISHED'}

	class BFU_OT_CopyImportSequencerScriptCommand(Operator):
		bl_label = "ImportSequencerScript"
		bl_idname = "object.copy_importsequencerscript_command"
		bl_description = "Copy Import Sequencer Script command"

		def execute(self, context):
			scn = context.scene
			setWindowsClipboard(GetImportSequencerScriptCommand())
			self.report({'INFO'}, "command for "+scn.file_import_sequencer_script_name+" copied")
			return {'FINISHED'}

	def draw(self, context):
		scn = context.scene
		layout = self.layout
		addon_prefs = bpy.context.user_preferences.addons["blender-for-unrealengine"].preferences

		if addon_prefs.UseGeneratedScripts == True:
			layout.label(text="Click on one of the buttons to copy the import command.", icon='INFO')
			copyButton = layout.row()
			copyButton.operator("object.copy_importassetscript_command")
			copyButton.operator("object.copy_importsequencerscript_command")
			layout.label(text="Then you can paste it into the python console of unreal", icon='INFO')
		else:
			layout.label(text='(Generated scripts are deactivated.)')


#############################[...]#############################


classes = (
	BFU_AP_AddonPreferences,

	BFU_PT_ObjectProperties,
	BFU_PT_ObjectImportProperties,

	BFU_OT_ObjExportAction,
	BFU_PT_AnimProperties,
	BFU_PT_AnimProperties.BFU_UL_ACTIONExportTarget,
	BFU_PT_AnimProperties.BFU_OT_UpdateObjActionButton,
	BFU_PT_AnimProperties.BFU_OT_ShowActionToExport,

	BFU_PT_AvancedObjectProperties,

	BFU_PT_CollisionsAndSockets,
	BFU_PT_CollisionsAndSockets.BFU_OT_ConvertToCollisionButtonBox,
	BFU_PT_CollisionsAndSockets.BFU_OT_ConvertToCollisionButtonCapsule,
	BFU_PT_CollisionsAndSockets.BFU_OT_ConvertToCollisionButtonSphere,
	BFU_PT_CollisionsAndSockets.BFU_OT_ConvertToCollisionButtonConvex,
	BFU_PT_CollisionsAndSockets.BFU_OT_ConvertToStaticSocketButton,
	BFU_PT_CollisionsAndSockets.BFU_OT_ConvertToSkeletalSocketButton,

	BFU_PT_Nomenclature,
	BFU_PT_Nomenclature.BFU_MT_NomenclaturePresets,
	BFU_PT_Nomenclature.BFU_OT_AddNomenclaturePreset,

	BFU_PT_ImportScript,

	BFU_OT_UnrealExportedAsset,
	BFU_OT_UnrealPotentialError,
	BFU_PT_Export,
	BFU_PT_Export.BFU_OT_ShowAssetToExport,
	BFU_PT_Export.BFU_OT_CheckPotentialErrorPopup,
	BFU_PT_Export.BFU_OT_CheckPotentialErrorPopup.BFU_OT_FixitTarget,
	BFU_PT_Export.BFU_OT_CheckPotentialErrorPopup.BFU_OT_SelectObjetButton,
	BFU_PT_Export.BFU_OT_CheckPotentialErrorPopup.BFU_OT_SelectVertexButton,
	BFU_PT_Export.BFU_OT_ExportForUnrealEngineButton,

	BFU_PT_Clipboard,
	BFU_PT_Clipboard.BFU_OT_CopyImportAssetScriptCommand,
	BFU_PT_Clipboard.BFU_OT_CopyImportSequencerScriptCommand,
)

def register():
	from bpy.utils import register_class
	for cls in classes:
		register_class(cls)

	bpy.types.Object.exportActionList = CollectionProperty(type=BFU_OT_ObjExportAction)
	bpy.types.Scene.UnrealExportedAssetsList = CollectionProperty(type=BFU_OT_UnrealExportedAsset)
	bpy.types.Scene.potentialErrorList = CollectionProperty(type=BFU_OT_UnrealPotentialError)

def unregister():
	from bpy.utils import unregister_class
	for cls in reversed(classes):
		unregister_class(cls)

if __name__ == "__main__":
	register()