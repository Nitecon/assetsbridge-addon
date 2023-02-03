import bpy


def set_global_ab_obj_data(d):
    if hasattr(bpy.context.scene, "ab_obj_data"):
        bpy.context.scene.ab_obj_data.data = d
    else:
        print("No ab_obj_data property found")


def get_global_ab_obj_data():
    d = {}
    if hasattr(bpy.context.scene, "ab_obj_data"):
        return bpy.context.scene.ab_obj_data.data
    return d
