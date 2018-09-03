# Buggers Bot

A `python-sc2` bot that builds a Zerg army and perhaps eventually will do it well!

## Inspirations

- Initially started doing this because of [Sentdex's tutorial series](https://pythonprogramming.net/starcraft-ii-ai-python-sc2-tutorial/)

- Looking at a lot of [CreepyBot](https://github.com/BurnySc2/burny-bots-python-sc2/tree/master/CreepyBot) to figure out translating Zerg strategy to `python-sc2`

- **Heavily** leveraging [h3nnn4n's design pattern](https://github.com/h3nnn4n/h3nnn4n-sc2-ai) in the construction of my bot

- Opener written to match [this build](https://www.reddit.com/r/allthingszerg/comments/3wzi14/welcome_to_lotv_heres_my_writeup_of_solid/?utm_content=title&utm_medium=browse&utm_source=reddit&utm_name=allthingszerg)

## Design Overview

- All of my code is organized into a Main/Controller/Helper scheme where, generally:

    - The Main object is the one the game runs and is where we call all of the `self.bot.*()` methods from
    - All of the Controllers are where I abstract away different areas of decision making, including micro, build order, scouting, and strategy

        - There will likely be a good deal of nesting in this structure, eventually

    - Helper objects are mostly there to carry useful global state variables, handle consistent checks, and provide other generic-enough functions that rely on game state

- The actual work is being done not by pure `asyncio`-- like a lot of other `python-sc2` project I've been seeing-- but by queueing everything up into a EventManager object at the start. This gives each Controller an async pass, resulting in more internal async calls, or a `self.bot.do()` call that triggers some action at the top level
