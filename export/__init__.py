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

from AssetsBridge import utilities


class BridgedExport(bpy.types.Operator):
    """AssetsBridge export to task script"""  # Use this as a tooltip for menu items and buttons.
    bl_idname = "AssetsBridge.export.BridgedExport"  # Unique identifier for buttons and menu items to reference.
    bl_label = "Export selected items to the json task file"  # Display name in the interface.
    bl_options = {'REGISTER', 'UNDO'}  # Enable undo for the operator.

    object_name: bpy.props.StringProperty(name="Object Name", default="", description="Name of the new object")
    object_path: bpy.props.StringProperty(name="Object Path", default="", description="Path of the object file")
    apply_transformations: bpy.props.BoolProperty(name="Apply Transformations", default=False, description="Apply Transformations to the object")
    task_file_var: bpy.props.StringProperty(name="TaskFileVar", default="//AssetsBridge.json", description="Task file location")

    def update_values(self, context):
        # check if an object is selected
        if context.active_object:
            # check if the selected object has custom properties
            if bpy.context.scene.cab_obj_data is not None:
                for item in bpy.context.scene.cab_obj_data:
                    if item['shortName'] == context.active_object.name:
                        self.object_name = item['shortName']
                        self.object_path = item['internalPath']
            else:
                cur_collection = utilities.collections.get_selected_collection()
                self.object_name = cur_collection.name

    def invoke(self, context, event):
        self.update_values(context)
        wm = context.window_manager
        return wm.invoke_props_dialog(self)

    def draw(self, context):
        layout = self.layout
        layout.prop(self, "object_name")
        layout.prop(self, "object_path")
        layout.prop(self, "apply_transformations")

    def get_collection_export_data(self, collection, ob_name, ob_path):
        obj_data = {}
        if bpy.context.scene.cab_obj_data is not None:
            for obj in bpy.context.scene.cab_obj_data:
                if obj['shortName'] == collection.name:
                    obj_data['shortName'] = ob_name
                    obj_data['internalPath'] = ob_path
                    if obj['model'] is not None:
                        obj_data['model'] = obj['model']
                    if obj['objectMaterials'] is not None:
                        obj_data['objectMaterials'] = obj['objectMaterials']
                    if obj['relativeExportPath'] is not None:
                        obj_data['relativeExportPath'] = obj['relativeExportPath']
                    if obj['exportLocation'] is not None:
                        obj_data['exportLocation'] = obj['exportLocation']
                    if obj['stringType'] is not None:
                        obj_data['stringType'] = obj['stringType']
                    if obj['worldData'] is not None:
                        obj_data['worldData'] = obj['worldData']
                    return obj_data
        # TODO: populate this with internal data from the object
        obj_data['shortName'] = ob_name
        obj_data['internalPath'] = ob_path
        obj_data['applyTransformations'] = self.apply_transformations
        obj_data['stringType'] = "StaticMesh"
        # get the base path

        base_obj_path = utilities.files.get_object_export_path(ob_path)
        export_path = base_obj_path + ob_name + ".fbx"

        self.report({'INFO'}, base_obj_path)
        self.report({'INFO'}, export_path)
        utilities.files.recursively_create_directories(base_obj_path)
        obj_data['exportLocation'] = export_path

        return obj_data

    def process_collection(self, collection):
        for obj in collection.objects:
            if obj.type == 'MESH':
                # Modify the mesh data here
                self.update_object_for_export(obj, collection)
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
                self.report({'INFO'}, "This is where I rotate.")  # TODO:
                utilities.objects.update_object_post_export(obj)
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
        export_options = {
            "use_selection": True,  # only export selected objects
            "use_mesh_modifiers": True,  # apply mesh modifiers
            "use_metadata": False,  # don't include metadata
            "mesh_smooth_type": "FACE",  # don't smooth meshes
            "use_subsurf": False,  # don't apply subsurface modifiers
            "use_mesh_edges": False,  # don't include mesh edges
            "use_tspace": True,  # include texture space data
            "use_armature_deform_only": False,  # include full armature deformations
            "add_leaf_bones": True,  # add leaf bones for armatures
            "global_scale": 1.0,  # don't change the global scale
            "path_mode": "AUTO",  # set path mode to "AUTO" to automatically determine the best path mode
            "bake_space_transform": False,  # don't bake space transform matrices
            "use_custom_props": True,  # include custom properties
            "axis_forward": "X",  # set forward axis to "-Z"
            "axis_up": "Z",  # set up axis to "Y
        }
        bpy.ops.export_scene.fbx(filepath=export_path, **export_options)

    def update_object_for_export(self, obj, collection):
        # Check if the object is a collection
        collection.name = self.object_name
        utilities.collections.rename_meshes_in_collection(collection, self.object_name)
        if not obj.name.startswith("UCX"):
            obj.select_set(True)
            if hasattr(obj, 'transform_apply'):
                obj.transform_apply(location=False, rotation=True, scale=True)

    def execute(self, context):  # execute() is called when running the operator.
        task_file = self.task_file_var
        if task_file == "//AssetsBridge.json":
            self.report({"ERROR"}, "Please configure AssetsBridge Addon Preferences to point to the correct task file "
                                   "for AssetsBridge.json")
            return {'FINISHED'}
        # Get a reference to the selected object
        new_data = {'operation': 'BlenderExport', 'objects': []}
        collection = utilities.collections.get_selected_collection()
        if collection is None:
            self.report({'INFO'}, "Nothing selected, Please select an object to export.")
            return {'FINISHED'}
        self.process_collection(collection)
        new_data['objects'] = []
        collection_data = self.get_collection_export_data(collection, self.object_name, self.object_path)
        new_data['objects'].append(collection_data)
        self.export_all_items_in_collection(collection, collection_data['exportLocation'])
        utilities.files.write_bridge_file(new_data)
        self.process_collection_post_export(collection)
        return {'FINISHED'}
