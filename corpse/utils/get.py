import esper
import utils
import pygame_menu

_cache = {}


def location_map_size(location) -> tuple[int, int]:
    if location.__class__.__name__ != "Location":
        raise TypeError("Object of type Location expected")

    map = location.map
    w, h, tile = map.width, map.height, map.tilewidth
    return w * tile, h * tile


def player(source, *components, id=False, cache=True):
    from creature import PlayerMarker

    world: esper.World = (
        source if source.__class__.__name__ == "World" else source.world
    )

    if id and cache:
        key = "player_entity_id"

    try:
        if len(components) == 1:
            comps = world.get_components(PlayerMarker, *components)[0]

            if cache and id and _cache.get(key, None) is None:
                _cache[key] = comps[0]

            return (comps[0], comps[1][1]) if id else comps[1][1]
        elif len(components) != 0:
            comps = world.get_components(PlayerMarker, *components)[0]

            if cache and id and _cache.get(key, None) is None:
                _cache[key] = comps[0]

            return (comps[0], comps[1][1:]) if id else comps[1][1:]
        elif cache:
            key = "player_entity_id"
            if _cache.get(key, None) is None:
                _cache[key] = world.get_component(PlayerMarker)[0][0]

            return _cache[key]
    except IndexError:
        return None


def equips(source, entity):
    from item import Inventory, Equipment

    world: esper.World = (
        source if source.__class__.__name__ == "World" else source.world
    )

    if not (
        (inv := world.try_component(entity, Inventory))
        and inv.slots
        and (equip := world.try_component(entity, Equipment))
    ):
        return None

    return inv.slots[equip.item]


def player_equips(source, *components):
    from item import Inventory, Equipment

    world: esper.World = (
        source if source.__class__.__name__ == "World" else source.world
    )

    if not (ret := utils.get.player(world, Inventory, Equipment)):
        return

    inv, equip = ret

    if not (inv.slots and (item := inv.slots[equip.item])):
        return

    if len(components) == 0:
        return inv, equip

    if len(components) == 1:
        return inv, equip, world.try_component(item, *components)

    return inv, equip, *world.try_components(item, *components)


def location(source, id=False):
    """Возвращает id сущности локации и компонент локации в виде кортежа."""

    from location import Location

    world: esper.World = (
        source if source.__class__.__name__ == "World" else source.world
    )

    entity, location = world.get_component(Location)[0]

    if id:
        return entity, location

    return location


def menu(source, id: str) -> pygame_menu.Menu:
    from meta import Id

    world: esper.World = (
        source if source.__class__.__name__ == "World" else source.world
    )

    for _, (menu_id, menu) in world.get_components(Id, pygame_menu.Menu):
        if menu_id.id == id:
            return menu
