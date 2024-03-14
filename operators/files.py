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
import os
import json


def read_bridge_file(file_path):
    with open(file_path, 'r') as f:
        return json.load(f)


def write_bridge_file(obj, file_path):
    with open(file_path, 'w') as f:
        json.dump(obj, f, indent=4)


def recursively_create_directories(path):
    if not os.path.exists(path):
        os.makedirs(path)


def clean_path(path):
    return path.replace('\\', '/').replace('//', '/')


def get_object_export_path(ob_path):
    base_obj_path = get_asset_root()
    if base_obj_path.endswith('/'):
        base_obj_path = base_obj_path[:-1]
    if not ob_path.startswith('/'):
        ob_path = '/' + ob_path
    if not ob_path.endswith('/'):
        ob_path = ob_path + '/'
    return base_obj_path + ob_path


def get_asset_root():
    return clean_path(os.path.dirname(bpy.context.preferences.addons['AssetsBridge'].preferences.filepaths[0].path))
