![image](https://user-images.githubusercontent.com/104511335/214185748-a3026176-3d4d-4bbd-bf38-dabc50aae0c1.png)

**Corpse is an easy to get on with full-featured cross-platform modular TDS game engine.**

## What makes corpse stand out from other game engines?

- Corpse's a game engine driven on top of the **ECS pattern** totally, which's one of the most efficient game architecture patterns for smooth development experience. ECS driven engine makes game architecturing process as pleasant as possible. Corpse uses [esper](https://github.com/benmoran56/esper), a lightweight ECS module for Python, with a focus on performance.
- **Modularity**. It's extremely easy to append new functionality to the game being developed as everything one needs to do is just create a separate Python file with needed components and systems and register them in the executor one. ECS on top of Python makes modular development pretty straightforward.
- **Cross-platform**. Corpse-made games can run on any Python-supporting operating systems such as Windows and *nix ones. In the some of multiverses' future it's planned to append mobile platforms support.
- **Convenient GUI level-editing** via [Tiled](https://www.mapeditor.org/) built-in support. _«Tiled is a free and open source, easy to use, and flexible level editor»_.
- **Perfomance**. You didn't hear wrong. Yeah, the engine's written in Python, a slow programming language, on top of esper, which uses just loops and raw caching mechanism underline. Therefore, corpse provides its own perfomant so-called _chunk-system_ to optimize ECS-component pipeline **heavily**. The presence of this system softens perfomance disadvantages of the selected stack, we repeat, **heavily**.
- **Simplicity**. Almost everyone out there knows Python, seriously. An evening, and one'll've already known of the ECS principles. Another evening appends Tiled to the stack and... That's it! Really! Anyone can start prototyping their own games with corpse almost from scratch in short periods of time without need of a complex tech background.
- **Simplicity, again**. Again, _C#_ and _Unity_ **do take time to start**; _C++_ and _Unreal Engine_ **do take time to start**; _GDScript_ and _Godot_ **do take time to start**. At least a somewhat heavy game engine **do take time to start**. **Corpse doesn't**—this's its one of the heaviest advantage, which completes this fancy seven-point list.

We hope, this list clearly shows how the corpse stands out from the rest of the engines and why you should try it out.

## Corpse capabilities

As said before, corpse uses entity-component-system as an underlying pattern to work with game objects. Thus, the completed game made on top of it is just a bunch of sequence of processors (or systems if you will), which are pipelined to process game components. The thing is that corpse already has the big amount of the needed systems and components implemented, so one can construct their own game with them.

See the root directory of the package source code for available modules. Here's list of them with short description:
- **ai** (enemy route-making module)
- **animation** (everything related to pipelining sprite states)
- **bind** (provides system to pin player legs to his body, for examples)
- **camera** (centring camera to the player)
- **chrono** (daylight-cycle)
- **chunk** (chunk system to optimize and lighten up game when it has pipeline of hundreds of components)
- **creature** (systems and comps for making entities like player, zombie and so on)
- **effect** (effects like redding the screen when player bleeds)
- **event** (handle key-related events, like keyboard presses and mouse clicks)
- **item** (handle item collision, provides full-featured inventory system and fire-weapon-related processors, also has item-registry initializer and storage)
- **location** (makes it able to build a game on top of [Tiled](https://www.mapeditor.org)-made map containing the most of needed objects already)
- **menu** (game menu with background and the needed buttons to start and pause the game, set it up and so on)
- **meta** (provides entity metadata components like `id` and `about` one)
- **movement** (systems to move, rotate and direct movable entities)
- **object** (object-related components like `size`, `solid` and `invisible` flags and so on)
- **render** (corpse rendering module; responds for displaying game objects as sprites properly, saving collissions, synchronizing animations and so on; one of the heaviest and most important and interesting module to explore)
- **roof** (roof component and processor to hide a roof object when player  goes under)
- **shoot** (fire weapon shooting markers and a processor; provides bullet physics and logic underline)
- **size** (provides simple size components with width and height fields)
- **ui** (logic related to placing and drawing game-related ui components on the screen, like inventory, tips and so on)
- **utils** (a bunch of utility functions to development easier; constants, math, filesystems, creature-making functions and so on)

Demonstration of some of the engine mechanics:

![player damage](https://github.com/markmelix/corpse/blob/main/data/demo/damage.gif?raw=true)
![inventory demo](https://github.com/markmelix/corpse/blob/main/data/demo/inventory.gif?raw=true)
![enemy kill](https://github.com/markmelix/corpse/blob/main/data/demo/kill.gif?raw=true)

## Running game engine in sandbox mode

If you want to test engine capabilities, you may edit `./data/world/sandbox/map.tmx` file via [Tiled](https://www.mapeditor.org/) (not essential) and run sandbox world with these commands:

``` sh
poetry install
poetry run python corpse/sandbox.py
```

## Creating own game on top of the corpse engine

Fork the repo and go ahead! See related [sandbox world](./corpse/sandbox.py) file for the reference.

## Corpse's corpsed?

Formerly, corpse was a try to create a TDS RPG game in the post-apocalyptic genre called *the Corpse Inc*. For now, it's the engine which's planned to be rewritten in Rust sometime as esper's ECS implementation in Python is too slow despite the chunk-system and has no alternatives.

## Can I contribute?

Of course you can! Just [fork](https://github.com/markmelix/corpse/fork) the repo and do the thing.

## Credits

Mark Meliksetyan (<markmelix@gmail.com>), Anton Grishin (<anton.ingrish@gmail.com>).

## License

[MIT](./LICENSE).
