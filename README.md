# smolset
A memory-efficient Python hashset

Python's `set` is great but very expensive on RAM. A `set` of 1000 integers is 64,984 bytes - over 64 bytes per integer.

A `smolset` of integers is 10,000 bytes, a 6x memory saving. Basic operations such as `add` are also faster probably.

`smolset`