import esper

_cache = {}


def location_map_size(location) -> tuple[int, int]:
    if location.__class__.__name__ != "Location":
        raise TypeError("Object of type Location expected")

    map = location.map
    w, h, tile = map.width, map.height, map.tilewidth
    return w * tile, h * tile


def player(processor, *components, id=False, cache=True):
    from creature import PlayerMarker

    world: esper.World = processor.world

    if id and cache:
        key = "player_entity_id"

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
        if _cache.get(key, None) is None:
            _cache[key] = world.get_component(PlayerMarker)[0][0]

        return _cache[key]


def player_from_world(world, *components, id=False):
    fake_processor = esper.Processor()
    fake_processor.world = world
    return player(fake_processor, *components, id=id, cache=False)


def location(processor, id=False):
    """Возвращает id сущности локации и компонент локации в виде кортежа."""

    from location import Location

    world: esper.World = processor.world

    entity, location = world.get_component(Location)[0]

    if id:
        return entity, location

    return location


def solid_group(processor):
    from object import SolidGroup

    world: esper.World = processor.world
    for _, group in world.get_component(SolidGroup):
        return group
