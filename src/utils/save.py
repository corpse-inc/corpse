import os
import json
import esper
import pygame

SAVES_DIR = "/".join(__file__.split("/")[:-3]) + "/saves"


def save_game(world: esper.World):
    from meta import Id
    from bind import BindRequest
    from location import LocationInitRequest

    def serialize_vector2(obj):
        return obj.x, obj.y

    def serialize_surface(obj):
        return str(pygame.image.tostring(obj, "RGBA"))

    def serialize_rect(obj):
        return {"x": obj.x, "y": obj.y, "w": obj.w, "h": obj.h}

    def serialize_sprite(obj):
        return {"image": serialize_surface(obj.image), "rect": serialize_rect(obj.rect)}

    def serialize_set(obj):
        return tuple(obj)

    def serialize_enum(obj):
        return {"value": obj.name}

    SERIALIZERS = {
        "Vector2": serialize_vector2,
        "Surface": serialize_surface,
        "Rect": serialize_rect,
        "Sprite": serialize_sprite,
        "set": serialize_set,
        "EnumMeta": serialize_enum,
        "StateType": serialize_enum,
        "PartType": serialize_enum,
    }

    def serialize(obj):
        typename = type(obj).__name__

        if typename in SERIALIZERS:
            return {"type_name": typename, "class_fields": SERIALIZERS[typename](obj)}

        return {"type_name": typename, "class_fields": obj.__dict__}

    data = {}

    for id, comps in world._entities.items():
        data[id] = []
        for comp in comps.values():
            compname = type(comp).__name__
            match compname:
                case "Location":
                    comp = LocationInitRequest(world.component_for_entity(id, Id).id)
                case "BindRequest":
                    comp = BindRequest(
                        comp.consumed,
                        comp.applied,
                        str(comp.component).split("'")[1].split(".")[-1],
                    )
                case "SolidGroup":
                    continue
            data[id].append(comp)

    try:
        os.mkdir(SAVES_DIR)
    except FileExistsError:
        pass

    with open(f"{SAVES_DIR}/world.json", mode="w", encoding="utf-8") as file:
        file.write(json.dumps(data, default=serialize, indent=4))
