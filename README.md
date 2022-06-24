# bset

=== WARNING BETA, most of this readme is aspirational design stuff (i.e. not reality yet) ===

A memory-efficient Python hashset. Drop-in replacement for `set`.

*You've tried all the rest, now try the bset.*

`pip install bset`

```
from bset import bset
bset([1, 0.5, 'ascii', 'ʊռɨƈօɖɛ🎉'])
```

Supports any type. Optimized on `int`, `float`, and `string`; anything else just gets thrown in a regular `set`.

You can `add()`, `remove()`, `intersect()`, `union()`. Supports iteration and of course you can (`x in bset`).
🎉🎉
### Compared with Python set()

Bset works best for large sets (over 1000 items). 

RAM size vs. set: 6x smaller on numbers, ~10x smaller on strings.

`add()` speed: 2x faster

`x in bset`, when False: 2x faster (uses a bloom filter)

`x in bset`, when True: 10x ~ 30x slower than `set`. Ouch.
