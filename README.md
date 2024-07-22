![image](https://user-images.githubusercontent.com/104511335/214185748-a3026176-3d4d-4bbd-bf38-dabc50aae0c1.png)

Formerly, corpse was a try to create a TDS RPG game in the post-apocalyptic genre called *the Corpse Inc*. For now, corpse is just raw useless game engine, which's planned to be rewritten in Rust sometime. Corpse's corpsed.

A team-making of the own game engine on top of pygame, esper and tiled was an amazing experience, which showed us that gamedev sucks. Thanks Yandex Lyceum for making us trying so.

## Corpse capabilities

Corpse uses entity-component-system as an underlying pattern to work with game objects. Thus, the completed game made on top of it is just a bunch of sequence of processors (or systems if you will), which are pipelined to process game components. The thing is that corpse already has the big amount of the needed systems and components implemented, so one can construct their own game with them.

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

## Running game engine in sandbox mode

If you want to test engine capabilities, you may edit `./data/world/sandbox/map.tmx` file via [Tiled](https://www.mapeditor.org/) (not essential) and run sandbox world with these commands:

``` sh
poetry install
poetry run python corpse/sandbox.py
```

## Creating own game on top of the corpse engine

Fork the repo and go ahead! See related [sandbox world](./corpse/sandbox.py) file for the reference.
