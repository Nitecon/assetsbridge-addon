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

def get_unreal_import_opts(type_string):
    import_options = {}
    if type_string == "StaticMesh":
        import_options = {
            "use_custom_normals": True,
            "axis_forward": "X",  # set forward axis to "-Z"
            "axis_up": "Z",  # set up axis to "Y
        }
    elif type_string == "SkeletalMesh":
        import_options = {
            "use_custom_normals": True,
            "use_custom_props": True,
            "use_image_search": True,
            "use_anim": True,
            "use_anim_action_all": True,
            "use_default_take": True,
            "use_anim_optimize": True,
            "anim_optimize_precision": 6.0,
            "path_mode": "AUTO",
            "axis_forward": "X",  # set forward axis to "-Z"
            "axis_up": "Z",  # set up axis to "Y
        }

    return import_options
