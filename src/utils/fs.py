import os
import sys

from typing import Optional


def init_resources_path() -> str:
    res = "/".join(__file__.split("/")[:-3]) + "/data"
    if sys.platform not in {"linux", "darwin"} and res.startswith("/"):
        return res[1:]
    return res


RESOURCES = init_resources_path()


class ResourcePath:
    @classmethod
    def location_tilemap(cls, location_id: str) -> str:
        return f"{RESOURCES}/world/{location_id}.tmx"

    @classmethod
    def frame(
        cls,
        object_id: str,
        part_type: Optional[str] = None,
        part_state: Optional[str] = None,
        idx: Optional[int] = None,
    ) -> str:
        s = f"{RESOURCES}/frames/{object_id}"

        if part_type:
            s += f"/{part_type}"

        if part_state:
            s += f"/{part_state}"

        if idx:
            return f"{s}/{idx}.png"

        return s


def dir_count(dir: str) -> int:
    """Возвращает количество файлов в директории."""
    return len(next(os.walk(dir))[2])
