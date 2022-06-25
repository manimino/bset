# bset

Making a set of `int`s in Python takes some 60 bytes per entry, which is absurd. An int is 4 bytes. 

This project implements two hashsets. One uses separate chaining and gets a 7-8x memory usage improvement.
The other uses linear probing and gets a 3x-4x improvement (depending on load factor).

Both are slower on build and access time, versus the Python `set` implementation. 
They are pure-Python; converting them to cython could help.

### Status

Development paused. 

[tighthash](https://github.com/realead/tighthash) and [cykhash](https://github.com/realead/cykhash) address this problem
already. It is unlikely that this implementation will outperform those by any significant amount, as the approach
here is similar. Just use cykhash, it's great.

Cykhash is excellent. Maybe a [abseil's swiss table](https://abseil.io/about/design/swisstables) could surpass it,
but not by much.