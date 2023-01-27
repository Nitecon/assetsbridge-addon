# Copyright (c) 2023, Nitecon Studios LLC.  All rights reserved.

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

from AssetsBridge.bridgetools import objects, files, collections, fbx


class BridgedImport(bpy.types.Operator):
    """AssetsBridge import from task script"""  # Use this as a tooltip for menu items and buttons.
    bl_idname = "assetsbridge.imports"  # Unique identifier for buttons and menu items to reference.
    bl_label = "Import items from the json task file"  # Display name in the interface.
    bl_options = {'REGISTER', 'UNDO'}  # Enable undo for the operator.
    task_file_var: bpy.props.StringProperty(name="TaskFileVar", default="//AssetsBridge.json", description="Task file location")

    def set_task_file(self, task_file):
        self.task_file_var = task_file

    def process_collection(self, collection, item, operation):
        for obj in collection.objects:
            if obj.type == 'MESH':
                # Modify the mesh data here
                objects.setup_import(obj, item, collection, operation)
                # do something with the mesh
            elif obj.type == 'EMPTY':
                # Check if the object is a collection
                if obj.instance_type == 'COLLECTION':
                    # Recursively process the collection
                    self.process_collection(obj.instance_collection)

    def execute(self, context):  # execute() is called when running the operator.
        paths = bpy.context.preferences.addons["AssetsBridge"].preferences.filepaths
        self.task_file_var = paths[0].path
        if self.task_file_var == "//AssetsBridge.json":
            self.report({"ERROR"}, "Please configure AssetsBridge Addon Preferences to point to the correct task file "
                                   "for AssetsBridge.json")
            return {'FINISHED'}
        if self.task_file_var == "":
            self.report({"ERROR"}, "Error reading preferences, tasks file appear to be empty.")
            return {'FINISHED'}
        app_data = files.read_bridge_file(self.task_file_var)

        # check if app_data is empty:
        if not app_data:
            self.report({"ERROR"}, "No data found in the task file")
            return {'FINISHED'}
        if app_data['operation'] != "":
            for item in app_data['objects']:
                if collections.has_collection(item['shortName']):
                    # if it has a collection remove it first (re-import)
                    collection = bpy.data.collections.get(item['shortName'])
                    for obj in collection.objects:
                        bpy.data.objects.remove(obj, do_unlink=True)
                    bpy.data.collections.remove(collection)
                collection = bpy.data.collections.new(item['shortName'])
                bpy.context.scene.collection.children.link(collection)
                layer_collection = bpy.context.view_layer.layer_collection.children[collection.name]
                bpy.context.view_layer.active_layer_collection = layer_collection
                import_options = fbx.get_unreal_import_opts(item['stringType'])
                bpy.ops.import_scene.fbx(filepath=item['exportLocation'], **import_options)
                # Iterate over the objects in the collection
                self.process_collection(collection, item, app_data['operation'])
        return {'FINISHED'}  # Lets Blender know the operator finished successfully.

