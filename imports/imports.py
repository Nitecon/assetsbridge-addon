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

from AssetsBridge.bridgetools import objects, files, collections, fbx, data


class BridgedImport(bpy.types.Operator):
    """AssetsBridge import from task script"""  # Use this as a tooltip for menu items and buttons.
    bl_idname = "assetsbridge.imports"  # Unique identifier for buttons and menu items to reference.
    bl_label = "Import items from the json task file"  # Display name in the interface.
    bl_options = {'REGISTER', 'UNDO'}  # Enable undo for the operator.
    task_file_var: bpy.props.StringProperty(name="TaskFileVar", default="//AssetsBridge.json", description="Task file location")

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

        # read the task file (all validation of the import task file is done):
        file_data = files.read_bridge_file(self.task_file_var)
        # check if app_data is empty:
        if not file_data:
            self.report({"ERROR"}, "No data found in the task file")
            return {'FINISHED'}

        if file_data['operation'] != "":
            data.set_global_ab_obj_data(context, file_data)
            app_data = data.get_global_ab_obj_data(context)
            if app_data is None:
                self.report({"ERROR"}, "Data did not import correctly")
                return {'FINISHED'}
            for item in app_data['objects']:
                # create a collection where the new import files will be stored
                collection = collections.get_or_create_collection(item["shortName"])
                import_options = fbx.get_general_import_opts(item["stringType"])
                if app_data['operation'] == "UnrealExport":
                    import_options = fbx.get_unreal_import_opts(item["stringType"])
                # create a temporary collection to store the imported objects
                temp_collection = collections.get_or_create_collection(item["objectId"])
                bpy.ops.import_scene.fbx(filepath=item["exportLocation"], **import_options)
                # add the imported objects to the temporary collection
                for obj in bpy.data.collections[item["shortName"]].objects:
                    temp_collection.objects.link(obj)
                # iterate over objects in the temporary collection and move them to the new collection
                for obj in temp_collection.objects:
                    new_name = item["shortName"] + "_" + temp_collection.name
                    if app_data['operation'] == "UnrealExport":
                        objects.rotate_object_in_degrees(obj, 0, 0, 90)
                        bpy.ops.object.transform_apply(location=False, rotation=True, scale=False)
                    # check if an existing object exists with the same name
                    if bpy.data.objects.get(new_name):
                        self.report({"INFO"}, "An object with the name " + new_name + "already exists, just setting "
                                                                                      "world data")
                        # set the world data of the existing object
                    else:
                        obj.name = new_name
                        temp_collection.objects.unlink(obj)  # Remove the object from its current collection
                        collection.objects.link(obj)  # Add the object to the new collection
                    objects.set_world_scale(obj, item, app_data["operation"])
                    objects.set_world_rotation(obj, item, app_data["operation"])
                    objects.set_world_location(obj, item, app_data["operation"])
                # delete any remaining objects in the temporary collection
                for obj in temp_collection.objects:
                    bpy.data.objects.remove(obj)
                # delete the temporary collection
                bpy.data.collections.remove(temp_collection)
                # Iterate over the objects in the collection
                self.process_collection(collection, item, app_data["operation"])
        return {'FINISHED'}  # Lets Blender know the operator finished successfully.

    def process_collection(self, collection, item, operation):
        for obj in collection.objects:
            if obj.type == 'MESH':
                # Modify the mesh data here
                objects.setup_import(obj, item, operation)
                # do something with the mesh
            elif obj.type == 'EMPTY':
                # Check if the object is a collection
                if obj.instance_type == 'COLLECTION':
                    # Recursively process the collection
                    self.process_collection(obj.instance_collection)
