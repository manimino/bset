"""
implements a 2D array shaped set

Needs a load factor of 10 or 20 to be space efficient (7x ~ 8x), but
then the lookup speed is 20x slower than python set().

"""

from smolset.constants import DTYPE_TO_ARRAY_TYPE
from array import array


class SubSet:

    def __init__(self, items=None, dtype=DTYPE_TO_ARRAY_TYPE['uint64'], nslots=1, load_factor=10):
        """
        A SubSet is a basic implementation of set.
        Added items are hashed modulo capacity to get a pos.

        If there are zero items at that pos:
            - self.listy[pos] will be a None

        If there's only one item at that pos:
            - self.listy[pos] will contain the item

        If there's multiple items with the same hash:
            - self.listy[pos] stores an array of all items at that pos.
        """
        # TODO oh right, the multi level hash thing was to keep build times down, cool idea there
        # TODO because the remake is kinda expensive right
        # TODO rather have 1000 sub-sets of 1000 slots each than have 1 1M-slot set when rebuilding
        self.dtype = dtype
        self.nslots = nslots
        self.listy = [None] * self.nslots
        self.size = 0
        self.load_factor = load_factor
        if items is not None:
            for item in items:
                self.add(item)

    def add(self, item):
        if item in self:
            return
        if self._full():
            self._expand()
        pos = hash(item) % self.nslots
        if self.listy[pos] is None:
            self.listy[pos] = item
        elif isinstance(self.listy[pos], array):
            self.listy[pos].append(item)
        else:
            self.listy[pos] = array(self.dtype, [self.listy[pos], item])
        self.size += 1

    def remove(self, item):
        pos = hash(item) % self.nslots
        if self.listy[pos] is None:
            raise KeyError(item)
        elif isinstance(self.listy[pos], array):
            if item in self.listy[pos]:
                self.listy[pos] = array(self.dtype, [i for i in self.listy[pos] if i != item])
                self.size -= 1
            else:
                raise KeyError(str(item))
        else:
            if self.listy[pos] != item:
                raise KeyError(item)
            self.listy[pos] = None
            self.size -= 1
        if self._sparse():
            self._shrink()

    def _copy_from(self, other):
        self.nslots = other.nslots
        self.listy = other.listy
        self.size = other.size

    def _full(self) -> bool:
        return self.size / self.nslots > self.load_factor

    def _expand(self):
        """Increase capacity. Rehashes all items."""
        if self.nslots < 10000:
            new_size = self.nslots * 10
        else:
            new_size = int(self.nslots * 2.5)
        other = SubSet(self, self.dtype, new_size, self.load_factor)
        self._copy_from(other)

    def _sparse(self):
        return self.size / self.nslots < 0.05  # todo tune this

    def _shrink(self):
        """Decrease capacity. Rehashes all items."""
        other = SubSet(self, self.dtype, max(self.nslots // 10, 1))
        self._copy_from(other)

    def __contains__(self, item):
        pos = hash(item) % self.nslots
        if self.listy[pos] is None:
            return False
        elif isinstance(self.listy[pos], array):
            return item in self.listy[pos]
        else:
            return self.listy[pos] == item

    def __iter__(self):
        return SubSetIterator(self)

    def __len__(self):
        return self.size


class SubSetIterator:

    def __init__(self, subset):
        self.subset = subset
        self.pos = 0
        self.arr_pos = 0

    def __next__(self):
        item = None
        while item is None:
            if self.pos == len(self.subset.listy):
                raise StopIteration

            if self.subset.listy[self.pos] is None:
                self.pos += 1
            elif isinstance(self.subset.listy[self.pos], array):
                arr = self.subset.listy[self.pos]
                if self.arr_pos == len(arr):
                    self.arr_pos = 0
                    self.pos += 1
                else:
                    item = arr[self.arr_pos]
                    self.arr_pos += 1
            else:
                item = self.subset.listy[self.pos]
                self.pos += 1
        return item


def main():
    import random
    ss = SubSet(int(random.random() * 10) for _ in range(10))
    #print('======== FULL ========')
    #print(list(ss))
    for item in list(ss):
        ss.remove(item)
    #print('======= EMPTY =========')
    #print('remaining:', list(ss))

main()