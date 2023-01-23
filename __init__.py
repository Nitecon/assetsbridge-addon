# Copyright (c) 2023, Nitecon Studios LLC.  All rights reserved.
import sys

# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

import bpy
from bpy.props import StringProperty, CollectionProperty, BoolProperty
from bpy_types import PropertyGroup, AddonPreferences

from AssetsBridge.export import BridgedExport
from AssetsBridge.imports import BridgedImport

bl_info = {
	"name": "Assets Bridge",
	"author": "Nitecon Studios LLC.",
	"version": (1, 0, 0),
	"blender": (3, 0, 0),
	"location": "View3D > Toolbar > AssetsBridge",
	"description": "AssetsBridge provides bi directional integration with unreal engine.",
	"warning": "",
	"doc_url": "",
	"category": "AssetsBridge",
}

bpy.types.Scene.cab_obj_data = bpy.props.PointerProperty(type=bpy.types.Text)


class AssetBridgeFilePaths(PropertyGroup):
	# name: bpy.props.StringProperty()
	path: StringProperty(subtype='FILE_PATH')
	display: BoolProperty()


class AssetsBridgePreferences(AddonPreferences):
	# this must match the add-on name, use '__package__'
	# when defining this in a submodule of a python package.
	bl_idname = __name__

	filepaths: CollectionProperty(
		name="File paths",
		type=AssetBridgeFilePaths)

	def draw(self, context):
		layout = self.layout
		layout.label(text="Please browse to the AssetsBridge task file.")
		for i in self.filepaths:
			if i.display:
				layout.prop(i, "path")


filepath_list = {
	"AssetsBridge": "//AssetsBridge.json"
}


class AssetsBridgePanel(bpy.types.Panel):
	bl_label = "Assets Bridge"
	bl_idname = "OBJECT_PT_AssetsBridge"
	bl_space_type = 'VIEW_3D'
	bl_region_type = 'UI'
	bl_category = "AssetsBridge"

	def draw(self, context):
		layout = self.layout
		ob = context.object

		row = layout.row()
		row.label(text="Import items from unreal export.")
		row = layout.row()
		row.operator(BridgedImport.bl_idname, text="Import Objects", icon='SPHERE')
		row = layout.row()
		row.label(text="Export items for import in unreal")

		# add a property for export operator to use for the path name
		row = layout.row()
		row.operator(BridgedExport.bl_idname, text="Export Selected", icon='SPHERE')


_class_registers = [
	BridgedImport,
	BridgedExport,
	AssetsBridgePanel,
	AssetBridgeFilePaths,
	AssetsBridgePreferences
]


def register():
	for cls in _class_registers:
		bpy.utils.register_class(cls)
	paths = bpy.context.preferences.addons[__name__].preferences.filepaths
	if not paths:
		for key, value in filepath_list.items():
			item = paths.add()
			item.name = key
			item.path = value
			item.display = True
	bpy.types.Object.glob_object_name = bpy.props.StringProperty(name="Global Object Name", default="", description="Name of the new object")
	bpy.types.Object.glob_object_path = bpy.props.StringProperty(name="Global Object Path", default="", description="Path of the object file")
	bpy.types.Object.glob_apply_transformations = bpy.props.BoolProperty(name="Global Apply Transformations", default=False, description="Apply Transformations to the object")
	BridgedImport.task_file_var = paths[0].path
	BridgedExport.task_file_var = paths[0].path


def unregister():
	for cls in _class_registers:
		bpy.utils.unregister_class(cls)


# This allows you to run the script directly from Blender's Text editor
# to test the add-on without having to install it.
if __name__ == "__main__":
	register()
	bpy.ops.object.BridgedExport('INVOKE_DEFAULT')
