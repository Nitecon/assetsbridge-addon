import bpy

from .exports import BridgedExport


def register():
    bpy.utils.register_class(BridgedExport)


def unregister():
    bpy.utils.unregister_class(BridgedExport)
