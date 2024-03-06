# Copyright (c) 2023, Nitecon Studios LLC.  All rights reserved.
import os

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

from AssetsBridge.bridgetools import objects, files, collections, fbx, data
from AssetsBridge.props import AssetBridgeObjectProperty
from bpy.props import PointerProperty


class BridgedExport(bpy.types.Operator):
    """AssetsBridge export to task script"""  # Use this as a tooltip for menu items and buttons.
    bl_idname = "assetsbridge.exports"  # Unique identifier for buttons and menu items to reference.
    bl_label = "Export selected items to the json task file"  # Display name in the interface.
    bl_options = {'REGISTER', 'UNDO'}  # Enable undo for the operator.

    object_name: bpy.props.StringProperty(name="Object Name", default="", description="Name of the new object")
    object_path: bpy.props.StringProperty(name="Object Path", default="", description="Path of the object file")
    apply_transformations: bpy.props.BoolProperty(name="Apply Transformations", default=False, description="Apply Transformations to the object")
    task_file_var: bpy.props.StringProperty(name="TaskFileVar", default="//AssetsBridge.json", description="Task file location")

    def execute(self, context):  # execute() is called when running the operator.
        paths = bpy.context.preferences.addons["AssetsBridge"].preferences.filepaths
        self.task_file_var = paths[0].path
        if self.task_file_var == "//AssetsBridge.json":
            self.report({"ERROR"}, "Please configure AssetsBridge Addon Preferences to point to the correct task file "
                                   "for AssetsBridge.json")
            return {'FINISHED'}
        # Get a reference to the selected object
        new_data = {'operation': 'BlenderExport', 'objects': []}
        selected_objects = bpy.context.selected_objects
        for obj in selected_objects:
            if obj.parent and obj.parent.type == 'COLLECTION':
                selected_objects.remove(obj)
        if len(selected_objects) == 0:
            self.report({'INFO'}, "Nothing selected, Please select an object to export.")
            return {'FINISHED'}
        # use report to print the amount of objects to be exported
        self.report({'INFO'}, "Exporting " + str(len(selected_objects)) + " objects.")
        for selected_item in selected_objects:
            if selected_item.type == 'COLLECTION':
                # report that this is collection processing
                self.report({'INFO'}, "Processing collection: " + selected_item.name)
                self.process_collection(selected_item)
                collection_data = self.get_collection_export_data(selected_item, self.object_name, self.object_path)
                new_data['objects'].append(collection_data)
                self.export_all_items_in_collection(selected_item, collection_data['exportLocation'])
                self.process_collection_post_export(selected_item)
            else:
                if obj.type == 'MESH':
                    self.setup_defaults(selected_item)
                #collection_data = self.get_collection_export_data(selected_item, self.object_name, self.object_path)
                ##self.report({'INFO'}, "Exporting object: " + selected_item.name)
                #parent_collection = collections.get_selected_collection()
                #objects.update_object_for_export(self.object_name, selected_item, parent_collection)
                #export_options = fbx.get_unreal_export_opts()
                #self.report({'INFO'}, "Exporting to location: " + self.get_export_path())
                #bpy.ops.export_scene.fbx(filepath=self.get_export_path(), **export_options)
                #self.process_collection_post_export(selected_item)
                #new_data['objects'].append(collection_data)

        files.write_bridge_file(new_data, self.task_file_var)
        return {'FINISHED'}

    def setup_defaults(self, obj):
        if not hasattr(obj, "AB_ExportPath"):
            obj["AB_ExportPath"] = self.get_export_path()

        if not hasattr(obj, "AB_ExportName"):
            obj["AB_ExportName"] = obj.name

            #obj["AssetsBridge"] = bpy.props.CollectionProperty(type=AssetBridgeObjectProperty, name="Asset Bridge Properties", description="Asset Bridge Properties")
            # Create a property group instance and link it to the object's ID properties
            #obj["AssetsBridge"]["export_location"] = self.get_export_path()
                # Assume AssetBridgeObjectProperty has a property named 'model'
                #asset_bridge_data.model = self.get_object_export_data(obj.parent, obj)


    def get_export_path(self):
        base_dir, filename = os.path.split(self.task_file_var)
        export_path = os.path.join(base_dir, self.object_path, self.object_name + ".fbx")
        files.recursively_create_directories(os.path.dirname(export_path))
        return export_path

    def update_values(self, context):
        # check if an object is selected
        self.report({'INFO'}, "Checking if selected and object import data exists")
        if context.active_object:
            cur_collection = collections.get_selected_collection()
            self.object_name = cur_collection.name
            data_obj = data.get_global_ab_obj_data(context)
            if data_obj is not None:
                for obj in data_obj['objects']:
                    if obj['shortName'] == cur_collection.name:
                        self.object_path = obj['internalPath']
                        break

    def invoke(self, context, event):
        self.update_values(context)
        wm = context.window_manager
        return wm.invoke_props_dialog(self)

    def draw(self, context):
        layout = self.layout
        layout.prop(self, "object_name")
        layout.prop(self, "object_path")
        layout.prop(self, "apply_transformations")

    def get_object_export_data(self, parent, in_object):
        obj_data = {
            'shortName': parent.name,
            'model': in_object['model'],
            'internalPath': parent['import_data']['internalPath'],
            'applyTransformations': self.apply_transformations,
            'stringType': "StaticMesh",
            'objectMaterials': in_object['objectMaterials'],
            'objectId': in_object['objectId'],
            'exportLocation': in_object['exportLocation'],
            'relativeExportPath': in_object['relativeExportPath'],
            'worldData': objects.get_first_mesh_transform_in_unreal_units(in_object)
        }
        # get the base path for the object
        base_obj_path = files.get_object_export_path(parent['import_data']['internalPath'])
        export_path = base_obj_path + in_object.name + ".fbx"

        self.report({'INFO'}, base_obj_path)
        self.report({'INFO'}, export_path)
        files.recursively_create_directories(base_obj_path)
        obj_data['exportLocation'] = export_path

        return obj_data

    def get_collection_export_data(self, collection, ob_name, ob_path):
        obj_data = {}
        for obj in collection.objects:
            if hasattr(obj, 'import_data'):
                obj_data['objectMaterials'] = obj['import_data']['objectMaterials']
        obj_data['shortName'] = ob_name
        obj_data['internalPath'] = ob_path
        obj_data['applyTransformations'] = self.apply_transformations
        obj_data['stringType'] = "StaticMesh"
        obj_data['worldData'] = objects.get_first_mesh_transform_in_unreal_units(collection)
        # get the base path for the object
        base_obj_path = files.get_object_export_path(ob_path)
        export_path = base_obj_path + ob_name + ".fbx"

        self.report({'INFO'}, base_obj_path)
        self.report({'INFO'}, export_path)
        files.recursively_create_directories(base_obj_path)
        obj_data['exportLocation'] = export_path

        return obj_data

    def process_collection(self, collection):
        for obj in collection.objects:
            if obj.type == 'MESH':
                # Modify the mesh data here
                objects.update_object_for_export(self.object_name, obj, collection)
            # do something with the mesh
            elif obj.type == 'EMPTY':
                # Check if the object is a collection
                if obj.instance_type == 'COLLECTION':
                    # Recursively process the collection
                    self.process_collection(obj.instance_collection)

    def process_collection_post_export(self, collection):
        for obj in collection.objects:
            if obj.type == 'MESH':
                # Modify the mesh data here
                objects.update_object_post_export(obj)
            elif obj.type == 'EMPTY':
                # Check if the object is a collection
                if obj.instance_type == 'COLLECTION':
                    # Recursively process the collection
                    self.process_collection(obj.instance_collection)

    def select_all_objects(self, collection):
        for obj in collection.objects:
            obj.select_set(True)
            if obj.type == 'EMPTY':
                if obj.instance_type == 'COLLECTION':
                    self.select_all_objects(obj.instance_collection)

    def export_all_items_in_collection(self, collection, export_path):
        # recursively select all items in the collection
        self.select_all_objects(collection)
        export_options = fbx.get_unreal_export_opts()
        self.report({'INFO'}, "Exporting to location: " + export_path)
        bpy.ops.export_scene.fbx(filepath=export_path, **export_options)
