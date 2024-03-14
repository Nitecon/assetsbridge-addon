import bpy
from .imports import BridgedImport
from .exports import BridgedExport

def register():
    bpy.utils.register_class(BridgedImport)
    bpy.utils.register_class(BridgedExport)


def unregister():
    bpy.utils.unregister_class(BridgedImport)
    bpy.utils.unregister_class(BridgedExport)


