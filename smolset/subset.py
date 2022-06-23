"""
implements a fringe-shaped subset

"""

from smolset.constants import DTYPE_TO_ARRAY_TYPE
from array import array

SINGLE_VAL = True


class SubSet:

    def __init__(self, items=None, dtype=DTYPE_TO_ARRAY_TYPE['uint64'], nslots=1, load_thresh=10):
        """
        A SubSet is a basic implementation of set.
        Added items are hashed modulo capacity to get a pos.

        If there are zero items at that pos:
            - self.manager[pos] will be a None

        If there's only one item at that pos:
            - store it in self.single[pos]
            - self.manager[pos] will contain a True

        If there's multiple items with the same hash:
            - self.single is ignored.
            - self.manager[pos] stores an array of all items at that pos.
        """
        # TODO we're gonna keep a high load factor (like 100) so the "single" array can get axed prolly?
        # TODO oh right, the multi level hash thing was to keep build times down, cool idea there
        # TODO because the remake is kinda expensive right
        # TODO rather have 1000 sub-sets of 1000 slots each than have 1 1M-slot set when rebuilding
        self.dtype = dtype
        self.nslots = nslots
        self.single = array(dtype, [0] * self.nslots)
        self.manager = [None] * self.nslots
        self.size = 0
        self.load_thresh = load_thresh
        if items is not None:
            for item in items:
                self.add(item)

    def add(self, item):
        #print(self.single, self.manager)
        #print('adding', item)
        if item in self:
            return
        if self._full():
            self._expand()
        pos = hash(item) % self.nslots
        if self.manager[pos] is None:
            self.single[pos] = item
            self.manager[pos] = SINGLE_VAL
        elif isinstance(self.manager[pos], array):
            self.manager[pos].append(item)
        else:
            self.manager[pos] = array(self.dtype, [self.single[pos], item])
        self.size += 1

    def remove(self, item):
        pos = hash(item) % self.nslots
        if self.manager[pos] is None:
            raise KeyError(item)
        elif self.manager[pos] == SINGLE_VAL:
            if self.single[pos] != item:
                raise KeyError(item)
            self.manager[pos] = None
            self.size -= 1
        else:
            if item in self.manager[pos]:
                self.manager[pos] = array(self.dtype, [i for i in self.manager[pos] if i != item])
                self.size -= 1
            else:
                raise KeyError(str(item))
        if self._sparse():
            self._shrink()

    def _copy_from(self, other):
        self.nslots = other.nslots
        self.single = other.single
        self.manager = other.manager
        self.size = other.size

    def _full(self) -> bool:
        return self.size / self.nslots > self.load_thresh

    def _expand(self):
        #print('expanding')
        """Increase capacity. Rehashes all items."""
        if self.nslots < 10000:
            new_size = self.nslots * 10
        else:
            new_size = int(self.nslots * 2.5)
        other = SubSet(self, self.dtype, new_size, self.load_thresh)
        self._copy_from(other)

    def _sparse(self):
        return self.size / self.nslots < 0.05  # todo tune this

    def _shrink(self):
        #print('shrinking')
        """Decrease capacity. Rehashes all items."""
        other = SubSet(self, self.dtype, max(self.nslots // 10, 1))
        self._copy_from(other)

    def __contains__(self, item):
        pos = hash(item) % self.nslots
        if self.manager[pos] is None:
            return False
        elif self.manager[pos] == SINGLE_VAL:
            return self.single[pos] is item
        else:
            return item in self.manager[pos]

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
            if self.pos == len(self.subset.manager):
                raise StopIteration

            if self.subset.manager[self.pos] == SINGLE_VAL:
                item = self.subset.single[self.pos]
                self.pos += 1
            elif self.subset.manager[self.pos] is None:
                self.pos += 1
            else:
                arr = self.subset.manager[self.pos]
                if self.arr_pos == len(arr):
                    self.arr_pos = 0
                    self.pos += 1
                else:
                    item = arr[self.arr_pos]
                    self.arr_pos += 1
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