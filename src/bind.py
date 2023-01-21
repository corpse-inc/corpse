import esper

from typing import Any
from dataclasses import dataclass as component


@component
class BindRequest:
    """Компонент-запрос на ссылку с компонентом другой сущности. Например, мы
    хотим позиционировать ноги игрока там же, где и его тело. Тогда мы можем
    сделать позицию ног ссылкой на позицию тела таким образом:

    ```python
    world.create_entity(BindingRequest(body_entity, legs_entity, Position))
    ```

    В следующем кадре BindingProcessor сделает нужную ссылку и удалит
    BindingRequest из базы данных сущностей.

    Параметры компонента:
    consumed: id сущности, у которой стоит взять компонент для ссылки
    applied: id сущности, к которой стоит добавить компонент в виде ссылки
    component: тип компонента, с которым будут производиться манипуляции."""

    consumed: int
    applied: int
    component: Any


class BindingProcessor(esper.Processor):
    def process(self, **_):
        for entity, binding in self.world.get_component(BindRequest):
            self.world.add_component(
                binding.applied,
                self.world.component_for_entity(binding.consumed, binding.component),
            )
            self.world.delete_entity(entity)
