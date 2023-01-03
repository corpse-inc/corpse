from dataclasses import dataclass as component


@component
class Id:
    """Компонент, обозначающий уникальный строковый идентификатор сущности."""

    id: str
