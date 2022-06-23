from pympler.asizeof import asizeof

from subset2d import SubSet


class BSet():

    def __init__(self):
        self.sset = SubSet()

    def add(self, item):
        self.sset.add(item)

    def remove(self, item):
        self.sset.remove(item)

    def memsize(self):
        return asizeof(self.sset)

    def __contains__(self, item):
        return item in self.sset

    def __iter__(self):
        return iter(self.sset)

    def __len__(self):
        return self.sset.size