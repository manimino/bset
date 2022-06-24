"""
implements a 1D array set. uses linear probing on collision.

This performs so badly.
If you constrain the probe length to, say, <10, the load factor will be dreadful.
If you constrain by load factor and set it high, you'll see slow lookups.

@ load factor of 0.5, got:
 === 1000000 items ===
lookup slow: 20.5x slower than set()
ratio 3.847x more RAM efficient, so that's nice
capacity 2097152
fillrate 0.477

# Cutting off ALL linear probing and giving incorrect results still results in a slowdown:
 === 1000000 items ===
lookup slow: 4.0
ratio 1.924
capacity 4194304
fillrate 0.238

# But that's not true of just a function that checks dummy arrays of the appropriate size, so maybe it's a
# class method slowdown thing, like 10x worth.

Say your probe length is 10.
You will get "runs" of filled space like:
.........X....X.....XXXX.XXXX..X..X.........
                    ^^^^.^^^^ <-- this crap
they build up little traps that will trip an _expand() call
at a pretty low load factor. Can't imagine this getting past 50% load.
No idea what those tutorials are talking about, their results defy probability.
"clustering" is the word for this in the literature.

yeah good blog post on this here
http://www.idryman.org/blog/2017/07/04/learn-hash-table-the-hard-way/
http://www.idryman.org/blog/2017/07/18/learn-hash-table-the-hard-way-2/
http://www.idryman.org/blog/2017/08/06/learn-hash-table-the-hard-way-3/
"""
from array import array
from bitarray import bitarray
from bset.dtypes import INT32_TYPE, INT64_TYPE


class TypedSet:

    def __init__(self, dtype, items=None, n_slots=1, load_factor=0.3):
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
        start = hash(item) % self.n_slots
        p = 0
        while True:
            pos = (start + p) % self.n_slots
            if not self.full[pos]:
                self.full[pos] = True
                self.arr[pos] = item
                break
            p += 1
        self.size += 1
        if self.size / self.n_slots > self.load_factor:
            self._expand()

    def remove(self, item):
        # TODO: This is broken / buggy. Probably no point in fixing it though
        # since chaining is faster anyway
        if item not in self:
            raise KeyError(item)
        start = hash(item) % self.n_slots
        p = 0
        while True:
            pos = (p + start) % self.n_slots
            if self.full[pos] and self.arr[pos] == item:
                self.full[pos] = False
                break
            p += 1
        # we just deleted from pos
        # time to do backshift - check if something should go in this spot.
        for i in range(1, self.n_slots):
            pos2 = (pos+i) % self.n_slots
            if not self.full[pos2]:
                # we know nothing needs to be shifted backwards
                break
            if self.full[pos2]:
                wanted_loc = hash(self.arr[pos2]) % self.n_slots  # where did that thing want to go?
                # does moving it to this slot help it get closer to where it wanted to go?
                # if pos2 == wanted_loc, it's right where it wants to be.
                wanted_dist = 0
                if wanted_loc < pos2:
                    # it wants to be back from where it is. But how far? is pos a good spot for it?
                    wanted_dist = pos2-wanted_loc
                elif wanted_loc > pos2:
                    # it wants to be forward from where it is. The only way that makes sense is
                    # if we're wrapping around the end here.
                    wanted_dist = self.n_slots-wanted_loc + pos2
                if wanted_dist >= i:
                    # moving this thing back will help it.
                    # Backshift it.
                    # Note that this can recurse.
                    item = self.arr[pos2]
                    self.remove(item)
                    self.add(item)

        self.size -= 1
        #if self._sparse():
        #    self._shrink()

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
        if self.full[start] and self.arr[start] == item:
            return True
        return False
        """
        p = 0
        while True:
            pos = (start + p) % self.n_slots
            if not self.full[pos]:
                return False
            elif self.arr[pos] == item:
                return True
            p += 1
        """

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
    ss = TypedSet(INT64_TYPE, [int(random.random() * 99) for _ in range(10)], load_factor=0.5)
    #print(list(ss))
    kd = []
    for x in ss.full:
        if x:
            kd.append('X')
        else:
            kd.append('.')
    #print(''.join(kd))
    #print(sum(1 for i in ss.full if i) / ss.n_slots)
    for item in list(ss):
        ss.remove(item)


if __name__ == '__main__':
    for i in range(100):
        main()
