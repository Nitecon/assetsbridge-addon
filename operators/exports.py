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

from .fbx import *
from .files import write_bridge_file
from .objects import *


class BridgedExport(bpy.types.Operator):
    """AssetsBridge export to task script"""  # Use this as a tooltip for menu items and buttons.
    bl_idname = "assetsbridge.exports"  # Unique identifier for buttons and menu items to reference.
    bl_label = "Export selected items to the json task file"  # Display name in the interface.
    bl_options = {'REGISTER', 'UNDO'}  # Enable undo for the operator.

    task_file_var: bpy.props.StringProperty(name="TaskFileVar", default="//AssetsBridge.json", description="Task file location")

    def execute(self, context):  # execute() is called when running the operator.
        paths = bpy.context.preferences.addons["AssetsBridge"].preferences.filepaths
        self.task_file_var = paths[0].path
        if self.task_file_var == "//AssetsBridge.json":
            self.report({"ERROR"}, "Please configure AssetsBridge Addon Preferences to point to the correct task file for AssetsBridge.json")
            return {'FINISHED'}
        # Get a reference to the selected object
        new_data = {'operation': 'BlenderExport', 'objects': []}
        selected_objects = bpy.context.selected_objects
        if len(selected_objects) == 0:
            self.report({'INFO'}, "Nothing selected, Please select an object to export.")
            return {'FINISHED'}

        self.report({'INFO'}, "Export process started")
        for selected_object in selected_objects:
            self.report({'INFO'}, "Processing object type: " + selected_object.type)
            if selected_object:
                # First check and set defaults for the currently selected object if it's a mesh
                if selected_object.type == 'MESH':
                    export_options = get_unreal_export_opts()
                    self.setup_naming(selected_object)
                    self.prepare_object(selected_object)
                    update_info = self.export_object(selected_object, export_options)
                    new_data['objects'].append(update_info)

                if selected_object.type == "EMPTY":
                    self.setup_naming(selected_object)
                    self.prepare_object(selected_object)
                    export_options = get_unreal_skeletal_export_opts()
                    # we need to unselect the current item and select all children prior to running update_object
                    bpy.ops.object.select_all(action='DESELECT')  # Deselect all objects.
                    selected_object.select_set(False)  # Ensure the selected object is deselected (redundant here but kept for clarity).
                    obj_name = selected_object.name
                    self.prepare_hierarchy(selected_object, obj_name)
                    self.select_child_hierarchy(selected_object)
                    update_info = self.export_object(selected_object, export_options)
                    new_data['objects'].append(update_info)

        write_bridge_file(new_data, self.task_file_var)
        return {'FINISHED'}

    def select_child_hierarchy(self, obj):
        """
        Recursively selects the entire hierarchy of children for a given object.

        Parameters:
            obj (bpy.types.Object): The object whose children are to be selected.
        """
        if obj.children:
            for child in obj.children:
                child.select_set(True)
                self.select_child_hierarchy(child)

    def prepare_hierarchy(self, obj, name):
        """
        Recursively prepares the object hierarchy for export by processing each child object and setting defaults.

        Parameters:
            obj (bpy.types.Object): The parent object whose hierarchy is to be prepared.
            name (str): The name to be used for the hierarchy.
        """
        for child in obj.children:
            self.report({'INFO'}, "Processing object type: " + child.type)
            self.prepare_object(child, name, True)
            if child.children:
                self.prepare_hierarchy(child, name)


    def prepare_object(self, obj, name=None, is_child=False):
        """
        Prepares the object for export by setting defaults and updating object properties.

        Parameters:
            obj (bpy.types.Object): The object to be prepared for export.
            name (str, optional): The name to be used for the object. Defaults to None.
            is_child (bool, optional): Indicates if the object is a child. Defaults to False.
        """
        if name is None:
            name = obj.name
        self.setup_defaults(obj)
        internal_path = self.get_collection_hierarchy_path(obj)
        obj["AB_exportLocation"] = self.get_export_path(obj)
        obj["AB_internalPath"] = internal_path
        obj["AB_relativeExportPath"] = internal_path

        if obj.name.startswith("SM_"):
            obj["AB_model"] = "/Script/Engine.StaticMesh'/Game/" + internal_path + "/" + name + "." + name
        elif obj.name.startswith("SKM_"):
            obj["AB_Model"] = "/Script/Engine.SkeletalMesh'/Game/" + internal_path + "/" + name + "." + name

        if is_child and obj.type != "ARMATURE":
            obj.name = name + "_" + str.lower(obj.type)

    def export_object(self, obj, export_options):
        """
        Exports the object using the provided export options.

        Parameters:
            obj (bpy.types.Object): The object to be exported.
            export_options (dict): Options for the export process.
        """
        bpy.ops.export_scene.fbx(filepath=obj["AB_exportLocation"], **export_options)
        return self.get_export_info(obj)

    def get_export_info(self, obj):
        """
        Retrieves export information for the given object.

        Parameters:
            obj (bpy.types.Object): The object for which export information is to be retrieved.

        Returns:
            dict: Export information for the object.
        """
        ob_info = {
            "model": obj["AB_model"],
            "objectId": obj["AB_objectId"],
            "internalPath": obj["AB_internalPath"],
            "relativeExportPath": obj["AB_relativeExportPath"],
            "shortName": obj.name,
            "exportLocation": obj["AB_exportLocation"],
            "stringType": obj["AB_stringType"],
            "worldData": {
                "rotation": {
                    "x": obj.rotation_euler.x,
                    "y": obj.rotation_euler.y,
                    "z": obj.rotation_euler.z
                },
                "scale": {
                    "x": obj.scale.x,
                    "y": obj.scale.y,
                    "z": obj.scale.z
                },
                "location": {
                    "x": obj.location.x,
                    "y": obj.location.y,
                    "z": obj.location.z
                }
            },
            "objectMaterials": [
                {
                    "name": "WorldGridMaterial",
                    "idx": 0,
                    "internalPath": "/Engine/EngineMaterials/WorldGridMaterial"
                }
            ],
        }

        return ob_info

    def setup_naming(self, obj):
        """
        Sets the naming prefix for an object based on the presence of an armature modifier.

        Parameters:
            obj (bpy.types.Object): The object for which the naming prefix is to be set.
        """
        has_armature = False

        for mod in obj.modifiers:
            if mod.type == 'ARMATURE':
                has_armature = True
                break

        new_prefix = "SKM_" if has_armature else "SM_"
        new_name = obj.name

        if new_name.startswith("SM_") or new_name.startswith("SKM_"):
            new_name = new_name[3:]
        obj.name = new_prefix + new_name

    def setup_defaults(self, obj):
        """
        Sets default values for object properties if not already present.

        Parameters:
            obj (bpy.types.Object): The object for which default values are to be set.
        """
        if obj.name.startswith("SM_"):
            obj["AB_model"] = obj.get("AB_model", "/Script/Engine.StaticMesh'/Game/Meshes/" + obj.name + "." + obj.name)
            obj["AB_stringType"] = "StaticMesh"
        elif obj.name.startswith("SKM_"):
            obj["AB_Model"] = obj.get("AB_Model", "/Script/Engine.SkeletalMesh'/Game/Meshes/" + obj.name + "." + obj.name)
            obj["AB_stringType"] = "SkeletalMesh"

        obj["AB_objectId"] = obj.get("AB_objectId", "")
        obj["AB_internalPath"] = obj.get("AB_internalPath", "/Game/Meshes")
        obj["AB_relativeExportPath"] = obj.get("AB_relativeExportPath", "/Game/Meshes")
        obj["AB_shortName"] = obj.get("AB_shortName", obj.name)
        obj["AB_exportLocation"] = obj.get("AB_exportLocation", "")

        default_materials = [
            {
                "name": "WorldGridMaterial",
                "idx": 0,
                "internalPath": "/Engine/EngineMaterials/WorldGridMaterial"
            }
        ]
        obj["AB_objectMaterials"] = obj.get("AB_objectMaterials", default_materials)

    def get_collection_hierarchy_path(self, obj):
        """
        Retrieves the collection hierarchy path for the given object.

        Parameters:
            obj (bpy.types.Object): The object for which the collection hierarchy path is to be retrieved.

        Returns:
            str: The collection hierarchy path for the object.
        """
        def find_collection_hierarchy(collection, hierarchy=[]):
            # Base case: If the collection is already the root, return the current hierarchy
            if collection.name == 'Master Collection':
                return hierarchy
            for coll in bpy.data.collections:
                if collection.name in coll.children.keys():
                    hierarchy.insert(0, coll.name)
                    return find_collection_hierarchy(coll, hierarchy)
            return hierarchy

        collection_path = []
        for coll in obj.users_collection:
            hierarchy = find_collection_hierarchy(coll, [coll.name])
            if hierarchy:
                collection_path.extend(hierarchy)
                break

        if collection_path and (collection_path[0] == 'Scene Collection' or collection_path[0] == 'Master Collection'):
            collection_path = collection_path[1:]
        if collection_path and collection_path[0] == 'Collection':
            collection_path[0] = 'Assets'

        return '/'.join(collection_path)

    def get_ab_base_path(self):
        """
        Retrieves the base path for the asset bridge.

        Returns:
            str: The base path for the asset bridge.
        """
        base_dir, filename = os.path.split(self.task_file_var)
        return base_dir

    def get_export_path(self, obj):
        """
        Retrieves the export path for the given object and ensures the directory structure is in place.

        Parameters:
            obj (bpy.types.Object): The object for which the export path is to be retrieved.

        Returns:
            str: The export path for the object.
        """
        base_path = self.get_ab_base_path()
        collection_path = self.get_collection_hierarchy_path(obj)
        export_path = os.path.join(base_path, collection_path, obj.name + ".fbx")
        normalized_export_path = os.path.normpath(export_path)
        os.makedirs(os.path.dirname(normalized_export_path), exist_ok=True)  # Recursively create directories if they don't exist
        return normalized_export_path

    def invoke(self, context, event):
        self.execute(context)
        return {'FINISHED'}
        # wm = context.window_manager
        # return wm.invoke_props_dialog(self)

    def draw(self, context):
        return {'FINISHED'}
        # layout = self.layout
        # layout.prop(self, "object_path")
        # layout.prop(self, "apply_transformations")
