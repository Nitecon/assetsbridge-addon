import bpy
from bpy.props import FloatProperty
from bpy_types import PropertyGroup

class AssetBridgeVector(PropertyGroup):
    x: FloatProperty(name="X", default=0.0)
    y: FloatProperty(name="Y", default=0.0)
    z: FloatProperty(name="Z", default=0.0)


class AssetBridgeWorldData(PropertyGroup):
    rotation: bpy.props.PointerProperty(type=AssetBridgeVector, name="Rotation")
    location: bpy.props.PointerProperty(type=AssetBridgeVector, name="Translation")
    scale: bpy.props.PointerProperty(type=AssetBridgeVector, name="Scale")


class AssetBridgeMaterialProperty(PropertyGroup):
    name = bpy.props.StringProperty(name="Name", default="None")
    idx = bpy.props.IntProperty(name="Index", default=0)
    internalPath = bpy.props.StringProperty(name="Internal Path", default="None")


class AssetBridgeObjectProperty(PropertyGroup):
    model = bpy.props.StringProperty(name="Model", default="None")
    objectId = bpy.props.StringProperty(name="Object ID", default="None")
    objectMaterials = bpy.props.CollectionProperty(name="Materials", type=AssetBridgeMaterialProperty)
    internalPath = bpy.props.StringProperty(name="Internal Path", default="None")
    relativeExportPath = bpy.props.StringProperty(name="Relative Export Path", default="None")
    shortName = bpy.props.StringProperty(name="Short Name", default="None")
    exportLocation = bpy.props.StringProperty(name="Export Location", default="None")
    stringType = bpy.props.StringProperty(name="Type", default="None")
    worldData = bpy.props.PointerProperty(type=AssetBridgeWorldData)


class AssetBridgeProperty(PropertyGroup):
    operation = bpy.props.StringProperty(name="Operation", default="Import")
    # objects = bpy.props.PointerProperty(type=bpy.types.ID)
    objects = bpy.props.CollectionProperty(name="Objects", type=bpy.types.Object)


_prop_registers = [
    AssetBridgeVector,
    AssetBridgeWorldData,
    AssetBridgeMaterialProperty,
    AssetBridgeObjectProperty,
    AssetBridgeProperty,
]


def register():
    for cls in _prop_registers:
        bpy.utils.register_class(cls)


def unregister():
    for cls in _prop_registers:
        bpy.utils.unregister_class(cls)
