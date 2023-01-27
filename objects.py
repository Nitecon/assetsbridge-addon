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


def update_object_post_export(obj):
    if hasattr(obj, 'transform_apply'):
        # rotate the object back to 0 in the Z
        # obj.rotation_euler.z -= 1.5708
        # obj.rotation_euler.z -= 1.5708
        # obj.rotation_euler.x -= 1.5708
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
    edges = [
        (0, 1), (1, 2), (2, 3), (3, 0),
        (4, 5), (5, 6), (6, 7), (7, 4),
        (0, 4), (1, 5), (2, 6), (3, 7)
    ]

    # Create a new mesh and link it to the scene
    mesh = bpy.data.meshes.new("Collision Box")
    shortName = obj.name.replace("SM_", "")
    collision_box_object = bpy.data.objects.new("UCX_" + shortName, mesh)
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


def rotate_object_in_degrees(obj, x, y, z):
    obj.rotation_mode = 'XYZ'
    obj.rotation_euler.x += (x * 0.0174533)
    obj.rotation_euler.y += (y * 0.0174533)
    obj.rotation_euler.z += (z * 0.0174533)

