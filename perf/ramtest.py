from bset.typedset_linear_probe import TypedSet
from bset.dtypes import INT64_TYPE
from cykhash import Int64Set
from array import array
from bitarray import bitarray
import random
import dataclasses
import time
from pympler.asizeof import asizeof
from sys import getsizeof


@dataclasses.dataclass
class Thing:
    num: float


def make_a_thing():
    return Thing(random.random())


def make_set(n=1):
    s = set()
    g = 10**40
    for i in range(n):
        s.add(int(random.random()*10**10) + g)
    return s


def make_bset(n, load_factor):
    s = TypedSet(INT64_TYPE, load_factor=load_factor)
    g = 10**40
    for i in range(n):
        s.add(int(random.random()*10**10) + g)
    return s


def make_cykset(n):
    s = Int64Set()
    g = 10**10
    for i in range(n):
        s.add(int(random.random()*10**10) + g)
    return s


def main():
    for exp in range(3, 8):
        n = 10**exp
        t0 = time.time()
        #v = make_bset(n, load_factor=16)
        v = make_cykset(n)
        t1 = time.time()
        s = make_set(n)
        t2 = time.time()

        build_v = t1-t0
        build_s = t2-t1
        ratio = asizeof(v) / asizeof(s)
        """
        print('smol build', t1-t0)
        print('set build', t2-t1)
        """
        # check sizes
        print(f" === {n} items === ")
        """
        print('smol size:', asizeof(v))
        print('set size:', asizeof(s))
        """
        # check lookups
        lookies = set()
        for i in v:
            lookies.add(i)
            if len(lookies) > 100:
                break

        b = array('Q', [0]*len(s))
        f = bitarray([True] * len(s))
        def _in_a_function(b, f, i):
            pos = hash(i) % len(b)
            if f[pos]:
                return b[pos] == i

        t0 = time.time()
        # _ = [_in_a_function(b, f, i) or i in lookies]
        _ = [i in v for i in lookies]
        t1 = time.time()
        _ = [i in s for i in lookies]
        t2 = time.time()

        smol_look = t1-t0
        set_look = t2-t1
        if set_look > 0:
            print('lookup slow:', round(smol_look / set_look, 1))

        """
        # check add speed
        lookies = []
        t0 = time.time()
        v.add(o2_id)
        t1 = time.time()
        s.add(o2_id)
        t2 = time.time()
        print('smol add:', t1-t0)
        print('set add:', t2-t1)
        """

        print('size improvement', round(1/ratio, 3))
        print('build slowdown', build_v / build_s)
        #print('capacity', v.n_slots)
        #print('fillrate', round(len(v) / v.n_slots, 3))
        # print(len(v), len(s))
        # print(ratio)


if __name__ == '__main__':
    main()
