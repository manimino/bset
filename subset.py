from array import array

SINGLE_VAL = True


class SubSet:

    def __init__(self, items=None, dtype='Q', nslots=1):
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
        self.dtype = dtype
        self.nslots = nslots
        self.single = array(dtype, [0] * self.nslots)
        self.manager = [None] * self.nslots
        self.size = 0
        for item in items:
            self.add(item)

    def _copy_from(self, other):
        self.nslots = other.nslots
        self.single = other.single
        self.manager = other.manager
        self.size = other.size

    def add(self, item):
        print(self.single, self.manager)
        print('adding', item)
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
            return False
        elif self.manager[pos] == SINGLE_VAL:
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

    def __contains__(self, item):
        pos = hash(item) % self.nslots
        if self.manager[pos] is None:
            return False
        elif self.manager[pos] == SINGLE_VAL:
            return self.single[pos] is item
        else:
            return item in self.manager[pos]

    def _full(self) -> bool:
        return self.size > self.nslots / 2

    def _expand(self):
        print('expanding')
        """Increase capacity. Rehashes all items."""
        other = SubSet(self, self.dtype, self.nslots * 10)
        self._copy_from(other)

    def _sparse(self):
        return self.size < self.nslots / 100

    def _shrink(self):
        print('shrinking')
        """Decrease capacity. Rehashes all items."""
        other = SubSet(self.dtype, self.nslots // 10)
        for i in self:
            other.add(i)
        self._copy_from(other)

    def __iter__(self):
        return SubSetIterator(self)


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
    ss = SubSet(int(random.random() * 999) for _ in range(50))
    print(list(ss))

main()