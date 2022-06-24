"""
implements a 1D array set. uses quadratic probing on collision.

About as bad as linear probing. This is dumb. We're not gonna get a decent load factor out of any of these craps.
The trouble is that as the size increases, the probability of collision goes up. So you need longer and longer
probes at scale.

And it's not like we can resolve the scaling problems by just using lots of small sets. It's bad even at small
sets.

A related idea is to have an "overflow space", when there's a collision, just throw it in the other space.
That's got the same "scales with size of set" problem.
"""
from array import array
from bitarray import bitarray
from bset.dtypes import INT32_TYPE, INT64_TYPE


class TypedSet:

    def __init__(self, dtype, items=None, n_slots=1, load_factor=0.7):
        """
        A set of the given dtype.
        Added items are hashed modulo capacity to get a pos.
        """
        # TODO oh right, the multi level hash thing was to keep build times down, cool idea there
        # TODO because the remake is kinda expensive right
        # TODO rather have 1000 sub-sets of 1000 slots each than have 1 1M-slot set when rebuilding
        self.dtype = dtype
        if dtype in [INT32_TYPE, INT64_TYPE]:
            self.arr = array(dtype, [0]*n_slots)
        else:
            self.arr = array(dtype, [0.0]*n_slots)
        self.full = bitarray([False]*n_slots)
        self.n_slots = n_slots
        self.size = 0
        self.load_factor = load_factor
        if items is not None:
            for item in items:
                self.add(item)

    def add(self, item):
        if item in self:
            return
        if self.size / self.n_slots > self.load_factor:
            self._expand()
        start = hash(item) % self.n_slots
        slot = -1
        for p in range(self.n_slots):
            pos = (start + p**2) % self.n_slots
            if not self.full[pos]:
                slot = pos
                break
        if slot == -1:
            self._expand()
        self.full[slot] = True
        self.arr[slot] = item
        self.size += 1

    def remove(self, item):
        start = hash(item) % self.n_slots
        if item not in self:
            raise KeyError(item)
        for p in range(self.n_slots):
            pos = (start + p**2) % self.n_slots
            if self.arr[pos] == item:
                self.full[pos] = False
                break
        self.size -= 1
        if self._sparse():
            self._shrink()

    def _copy_from(self, other):
        self.full = other.full
        self.arr = other.arr
        self.size = other.size
        self.n_slots = other.n_slots

    def _expand(self):
        """Increase capacity. Rehashes all items."""
        new_size = self.n_slots * 2
        other = TypedSet(self.dtype, items=self, n_slots=new_size, load_factor=self.load_factor)
        self._copy_from(other)

    def _sparse(self):
        return self.size / self.n_slots < 0.05  # todo tune this

    def _shrink(self):
        """Decrease capacity. Rehashes all items."""
        other = TypedSet(self.dtype, items=self, n_slots=max(self.n_slots // 10, 1), load_factor=self.load_factor)
        self._copy_from(other)

    def __contains__(self, item):
        start = hash(item) % self.n_slots
        for p in range(self.n_slots):
            pos = (start + p**2) % self.n_slots
            if not self.full[pos]:
                return False
            elif self.arr[pos] == item:
                return True
        return False

    def __iter__(self):
        return TypedSetIterator(self)

    def __len__(self):
        return self.size


class TypedSetIterator:

    def __init__(self, tset):
        self.tset = tset
        self.pos = 0

    def __next__(self):
        item = None
        while item is None:
            if self.pos == self.tset.n_slots:
                raise StopIteration
            if self.tset.full[self.pos]:
                item = self.tset.arr[self.pos]
            self.pos += 1
        return item


def main():
    import random
    ss = TypedSet(INT64_TYPE, [int(random.random() * 9999999) for _ in range(100000)], load_factor=0.8)
    z = sum(1 for i in ss.full if i) / ss.n_slots
    print(z)


if __name__ == '__main__':
    main()
