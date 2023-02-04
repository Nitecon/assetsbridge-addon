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


def has_collection(name):
    for myCol in bpy.data.collections:
        print(myCol.name)
        if myCol.name == name:
            return True
    return False


def get_collection_by_name(name):
    for myCol in bpy.data.collections:
        if myCol.name == name:
            layer_collection = bpy.context.view_layer.layer_collection.children[myCol.name]
            bpy.context.view_layer.active_layer_collection = layer_collection
            return myCol


def get_selected_collection():
    active_obj = bpy.context.active_object
    if active_obj is None:
        return None
    else:
        # Check if the active object is a collection
        if active_obj.type == 'COLLECTION':
            return active_obj
        else:
            # Get the collection that the active object is part of
            for collection in bpy.data.collections:
                for obj in collection.all_objects:
                    if obj == active_obj:
                        return collection
    return None


def collection_has_existing_mesh_matching_world_data(collection, world_data):
    for obj in collection.all_objects:
        if obj.type == 'MESH':
            if hasattr(obj, "ab_obj_data"):
                if obj.ab_obj_data.data == world_data:
                    return True
    return False


# check to see if a collection exists by name, and if it does not exist create it and set it active, else set it active and return existing collection.
def get_or_create_collection(name):
    collection = get_collection_by_name(name)
    if collection is not None:
        return collection
    else:
        return create_collection_and_set_active(name)


def find_collection_data_by_name(name):
    if hasattr(bpy.context.scene, "ab_obj_data"):
        for obj in bpy.context.scene.ab_obj_data.objects:
            if obj.shortName == name:
                return obj


def create_collection_and_set_active(name):
    collection = bpy.data.collections.new(name)
    bpy.context.scene.collection.children.link(collection)
    layer_collection = bpy.context.view_layer.layer_collection.children[collection.name]
    bpy.context.view_layer.active_layer_collection = layer_collection
    return collection


def delete_collection_by_name(name):
    collection = get_collection_by_name(name)
    if collection is not None:
        empty_collection(collection)
        bpy.data.collections.remove(collection)


def empty_collection_by_name(name):
    collection = get_collection_by_name(name)
    if collection is not None:
        empty_collection(collection)


def empty_collection(collection):
    for obj in collection.objects:
        collection.objects.unlink(obj)


def collection_has_ucx_object(collection, object_name):
    # Iterate over the objects in the collection
    for obj in collection.objects:
        # Check if the object's name starts with "UCX"
        if obj.name.startswith("UCX"):
            if obj.name.contains(object_name):
                # Return True if the object's name starts with "UCX"
                return True
    # Return False if no objects in the collection have a name that starts with "UCX"
    return False


def rename_meshes_in_collection(collection, new_name):
    for obj in collection.objects:
        if obj.type == 'MESH':
            if obj.name.startswith("SM_"):
                obj.name = "SM_" + new_name.replace("SM_", "")
            if obj.name.startswith("UCX_"):
                obj.name = "UCX_" + new_name.replace("SM_", "")
        elif obj.type == 'EMPTY':
            if obj.instance_type == 'COLLECTION':
                rename_meshes_in_collection(obj.instance_collection)
