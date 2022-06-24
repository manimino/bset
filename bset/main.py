from pympler.asizeof import asizeof

from bset.dtypes import call_type, INT64_TYPE, FLOAT64_TYPE, STRING_TYPE, OBJECT_TYPE
from bset.typedset_linear_probe import TypedSet


class bset:

    def __init__(self, items=None):
        self.subsets = {
            INT64_TYPE: TypedSet(INT64_TYPE),
            FLOAT64_TYPE: TypedSet(FLOAT64_TYPE),
            STRING_TYPE: set(),
            OBJECT_TYPE: set()
        }
        if items:
            for i in items:
                self.add(i)

    def add(self, item):
        self.subsets[call_type(item)].add(item)

    def remove(self, item):
        self.subsets[call_type(item)].remove(item)

    def intersect(self, other):
        new_bset = bset()
        if isinstance(other, set):
            other = bset(other)
        for other_type, other_subset in other.subsets:
            new_bset.subsets[other_type] = self.subsets[other_type].intersection(other.subsets[other_type])
        return new_bset

    def union(self, other):
        new_bset = bset()
        if isinstance(other, set):
            other = bset(other)
        for other_type, other_subset in other.subsets:
            new_bset.subsets[other_type] = self.subsets[other_type].union(other.subsets[other_type])
        return new_bset

    def memsize(self):
        return asizeof(self.sset)

    def capacity(self):
        return sum(s.n_slots for s in self.subsets.values() if isinstance(s, TypedSet))

    def __contains__(self, item):
        return item in self.subsets[call_type(item)]

    def __iter__(self):
        return bset_iterator(self)

    def __len__(self):
        return sum(len(subset) for subset in self.subsets.values())

    def __bool__(self):
        return len(self) != 0


class bset_iterator:

    def __init__(self, bset):
        self.subsets = list(bset.subsets.values())
        self.pos = 0
        self.subset_iter = iter(self.subsets[self.pos])

    def __next__(self):
        while True:
            try:
                return next(self.subset_iter)
            except StopIteration:
                self.pos += 1
                if self.pos == len(self.subsets):
                    raise StopIteration
                self.subset_iter = iter(self.subsets[self.pos])
