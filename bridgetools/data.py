import bpy


def set_global_ab_obj_data(d):
    bpy.context.scene.ab_obj_data = d


def get_global_ab_obj_data():
    d = {}
    if hasattr(bpy.context.scene, "ab_obj_data"):
        return bpy.context.scene.ab_obj_data
    return d
