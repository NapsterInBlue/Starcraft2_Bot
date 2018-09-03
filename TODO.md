# TODO

## Mechanics

- Figure out why I'm getting a lot of double actions (e.g. two expansions at the same time)
- Better unit organization

   - Attackers
   - Scouters
   - Squads?

- Better handling of zergling to baneling transformations

- Cleaner stage-in-game mechanisms than timestamped `if` statements
- Explore debugging opportunities
- [Creep Coverage](https://github.com/BurnySc2/burny-bots-python-sc2/blob/master/CreepyBot/CreepyBot.py#L755-L775)
- Bot sleep for debug

``` python
if something_interesting_happens:  # Slow down for debug
    self._client.game_step = 1
    await asyncio.sleep(0.02)
```

## Strategy

- Build non-zergling units, lol
- Scale number of queens
- Determine useful scouting global variables and how to use them
- Park Overlords on expansions and drop creep
