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

from . import collections


def setup_import(obj, item, operation):
    if obj is None or not hasattr(obj, "type"):
        return
    if operation == "UnrealExport":
        update_object_for_unreal_import(obj, item)
    update_for_general_import(obj, item)


def update_for_general_import(obj, item):
    if obj.type == "MESH":
        # select the object
        obj.select_set(True)
        bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
        bpy.context.view_layer.objects.active = obj
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.tris_convert_to_quads()
        bpy.ops.object.mode_set(mode='OBJECT')
        # Print the name of the object
    if obj.name.startswith("UCX"):
        obj.display.show_shadows = False
        obj.color = (0, 0.2, 1, 1)
        obj.display_type = 'WIRE'
        obj.hide_render = True
    if "worldData" in item:
        if item['worldData'] is not None:
            if item['worldData']['translation'] is not None:
                obj.location.x = item['worldData']['translation']['x'] * 0.01
                obj.location.y = item['worldData']['translation']['y'] * 0.01
                obj.location.z = item['worldData']['translation']['z'] * 0.01
            if item['worldData']['rotation'] is not None:
                rotate_object_in_degrees(obj, item['worldData']['rotation']['x'], item['worldData']['rotation']['y'], item['worldData']['rotation']['z'])
            if item['worldData']['scale3D'] is not None:
                obj.scale.x = item['worldData']['scale3D']['x'] * obj.scale.x
                obj.scale.y = item['worldData']['scale3D']['y'] * obj.scale.y
                obj.scale.z = item['worldData']['scale3D']['z'] * obj.scale.z


def update_object_for_unreal_import(obj, item):
    # rotate_object_in_degrees(obj, 0, 0, 90)
    rotate_object_in_degrees(obj, 0, 0, 0)


def update_object_for_export(name, obj, collection):
    # Check if the object is a collection
    collection.name = name
    collections.rename_meshes_in_collection(collection, name)
    obj.select_set(True)
    if hasattr(obj, 'transform_apply'):
        obj.transform_apply(location=False, rotation=True, scale=True)


def update_object_post_export(obj):
    if hasattr(obj, 'transform_apply'):
        obj.transform_apply(location=False, rotation=True, scale=True)


def create_collision_box(obj):
    # Get the object's collision box data
    collision_box = obj.bound_box

    # Create a list of vertices for the collision box mesh
    vertices = [
        collision_box[0], collision_box[1], collision_box[2],
        collision_box[3], collision_box[4], collision_box[5],
        collision_box[6], collision_box[7]
    ]

    # Create a list of edges for the collision box mesh
    edges = [(0, 1), (1, 2), (2, 3), (3, 0),(4, 5), (5, 6), (6, 7), (7, 4),(0, 4), (1, 5), (2, 6), (3, 7)]

    # Create a new mesh and link it to the scene
    mesh = bpy.data.meshes.new("Collision Box")
    short_name = obj.name.replace("SM_", "")
    collision_box_object = bpy.data.objects.new("UCX_" + short_name, mesh)
    bpy.context.collection.objects.link(collision_box_object)

    # Set the vertices and edges of the mesh
    mesh.from_pydata(vertices, edges, [])

    # Scale the bounding box mesh down until it closely matches the size of the object
    scale_factor = 0.9
    while collision_box_object.dimensions[0] < obj.dimensions[0] * scale_factor \
            or collision_box_object.dimensions[1] < obj.dimensions[1] * scale_factor \
            or collision_box_object.dimensions[2] < obj.dimensions[2] * scale_factor:
        collision_box_object.scale *= scale_factor

    # Update the scene
    bpy.context.view_layer.update()


# get the first object in collection that is a mesh's transform in unreal units
def get_first_mesh_transform_in_unreal_units(collection):
    for obj in collection.objects:
        if obj.type == "MESH":
            return get_object_transform_in_unreal_units(obj)
    return None


# get object transform in unreal units
def get_object_transform_in_unreal_units(obj):
    transform = {'translation': {'x': obj.location.x * 0.01, 'y': obj.location.y * 0.01, 'z': obj.location.z * 0.01},
                 'rotation': get_object_rotation_in_degrees(obj),
                 'scale3D': {'x': obj.scale.x, 'y': obj.scale.y, 'z': obj.scale.z}}
    return transform


# get object rotation in degrees
def get_object_rotation_in_degrees(obj):
    rotation = {'x': obj.rotation_euler.x * 57.2958, 'y': obj.rotation_euler.y * 57.2958, 'z': obj.rotation_euler.z * 57.2958}
    return rotation


def rotate_object_in_degrees(obj, x, y, z):
    obj.rotation_mode = 'XYZ'
    obj.rotation_euler.x += (x * 0.0174533)
    obj.rotation_euler.y += (y * 0.0174533)
    obj.rotation_euler.z += (z * 0.0174533)

