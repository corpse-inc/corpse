import esper
import utils
from dataclasses import dataclass as component
from item import Inventory


class ComplitingLevelProcessor(esper.Processor):
    def process(self, **_):
        self.finished_level = False 
        for _, inv in self.world.get_component(Inventory):
            count_magic_item = 0
            for item in inv.slots:
                if item is None: continue
                if item.get_component(FinishItem):
                    count_magic_item += 1

            print(count_magic_item)
            if count_magic_item >= 3:
                # utils.consts.CURRENT_MAP += 1               
                print('Игра пройдена!')
                

@component()
class FinishItem:
    pass

