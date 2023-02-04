import bpy


def set_global_ab_obj_data(context, data):
    if hasattr(bpy.context.scene, "ab_obj_data"):
       context.scene["ab_obj_data"] = data
    else:
        print("No ab_obj_data property found")


def get_global_ab_obj_data(context):
    if hasattr(bpy.context.scene, "ab_obj_data"):
        return context.scene["ab_obj_data"]
    return None
