import bpy

from .imports import BridgedImport


def register():
    bpy.utils.register_class(BridgedImport)


def unregister():
    bpy.utils.unregister_class(BridgedImport)
