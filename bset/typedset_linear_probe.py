"""
implements a 1D array set. Uses linear probing on collision.

This performs so much worse than chaining.
If you constrain by load factor and set it high, you'll see slow lookups.
If you constrain by max probe length instead, the load factor will be unusably low. (dumb idea anyway, but I tried it.)

@ load factor of 0.5, got:
 === 1000000 items ===
lookup slow: 20.5x slower than set()
ratio 3.847x more RAM efficient, so that's nice
capacity 2097152
fillrate 0.477

# If I cut off ALL probing, it's still slower than a set.
 === 1000000 items ===
lookup slow: 4.0
ratio 1.924
capacity 4194304
fillrate 0.238

Doing the same experiment on a standalone function, I get a 10x speedup or better. Class methods may just
be really slow.

# Linear probing just isn't a great algorithm.
# Maybe we are not seeing the cache efficiency here in Python that C would?

# Clustering problems:
Say your probe length is 10.
You will get "runs" of filled space like:
.........X....X.....XXXX.XXXX..X..X.........
                    ^^^^.^^^^ <-- this crap
they build up little traps that will increase probe length.
at a pretty low load factor. Especially as load > 50%.

yeah good blog post on this here
http://www.idryman.org/blog/2017/07/04/learn-hash-table-the-hard-way/
http://www.idryman.org/blog/2017/07/18/learn-hash-table-the-hard-way-2/
http://www.idryman.org/blog/2017/08/06/learn-hash-table-the-hard-way-3/

There are lots of hacks to diminish it, but they each cost during add, remove, or (worst) lookup.
Robinhood, backsliding, cuckoo hashing, double hashing, quadratic probing... no free lunches.
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
        self.dtype = dtype
        if dtype in [INT32_TYPE, INT64_TYPE]:
            self.arr = array(dtype, [0]*n_slots)
        else:
            self.arr = array(dtype, [0.0]*n_slots)
        self.full = bitarray([False]*n_slots)
        self.deleted = bitarray([False]*n_slots)
        self.n_slots = n_slots
        self.mask = n_slots-1
        self.size = 0
        self.load_factor = load_factor
        if items is not None:
            for item in items:
                self.add(item)

    def add(self, item):
        pos, found = self._look_for_next_empty_or_item_when_adding(item)
        if found:
            return
        self.full[pos] = True
        self.arr[pos] = item
        self.size += 1
        if self.size / self.n_slots >= self.load_factor:
            self._expand()

    def remove(self, item):
        delete_pos, found = self._look_for_next_empty_or_item(item)
        if not found:
            raise KeyError(item)
        self.full[delete_pos] = False
        self.deleted[delete_pos] = True
        self.size -= 1
        if self._sparse():
            self._shrink()

    def _copy_from(self, other):
        self.full = other.full
        self.arr = other.arr
        self.size = other.size
        self.n_slots = other.n_slots
        self.mask = other.mask
        self.deleted = other.deleted

    def _expand(self):
        """Increase capacity. Rehashes all items."""
        new_size = self.n_slots * 2
        other = TypedSet(self.dtype, items=self, n_slots=new_size, load_factor=self.load_factor)
        self._copy_from(other)

    def _sparse(self):
        return self.size / self.n_slots < 0.1  # arbitrary

    def _shrink(self):
        """Decrease capacity. Rehashes all items."""
        new_size = self.n_slots // 2
        other = TypedSet(self.dtype, items=self, n_slots=new_size, load_factor=self.load_factor)
        self._copy_from(other)

    def _look_for_next_empty_or_item(self, item=None) -> tuple[int, bool]:
        # for contains() checks and removing
        start = hash(item) & self.mask
        if self.full[start] and self.arr[start] == item:  # item found
            return start, True
        if not self.full[start] and not self.deleted[start]:  # empty
            return start, False
        # start wasn't our item, and it's deleted or full. Let's probe.
        p = start + 1
        while True:
            if p == self.n_slots:
                p = 0
            if self.full[p] and self.arr[p] == item:  # item found
                return p, True
            if not self.full[p] and not self.deleted[p]:  # empty (and never been deleted from)
                return p, False
            if p == start:
                # prevent infinite loop. We scanned the whole list and didn't find the item.
                return p, False
            p += 1

    def _look_for_next_empty_or_item_when_adding(self, item=None) -> tuple[int, bool]:
        # only used when adding. Same logic, just that it doesn't care about the 'deleted' flag.
        start = hash(item) & self.mask
        if self.full[start] and self.arr[start] == item:  # item found
            return start, True
        elif not self.full[start]:  # empty (insertable)
            return start, False
        # full and didn't match... so we start probing
        p = start+1
        while True:
            if p == self.n_slots:
                p = 0
            if not self.full[p]:  # empty
                return p, False
            elif self.arr[p] == item:  # item found
                return p, True
            if p == start:
                # prevent infinite loop
                raise Exception("Insertion failed. Don't specify a load_factor above 1 next time.")
            p += 1

    def __contains__(self, item):
        _, is_item = self._look_for_next_empty_or_item(item)
        return is_item

    def __iter__(self):
        return TypedSetIterator(self)

    def __len__(self):
        return self.size

    def __str__(self):
        kd = []
        for i in range(self.n_slots):
            if self.full[i]:
                kd.append('F')
            elif self.deleted[i]:
                kd.append('x')
            else:
                kd.append('.')
        return ''.join(kd)


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
    print(list(ss))
    print(sum(1 for i in ss.full if i) / ss.n_slots)
    for item in list(ss):
        print(list(ss))
        print(str(ss))
        print('removing', item)
        ss.remove(item)


if __name__ == '__main__':
    for i in range(100):
        main()
