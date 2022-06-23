from smolset import SubSet

import random
import dataclasses
import time
from pympler.asizeof import asizeof


@dataclasses.dataclass
class Thing:
    num: float


def make_a_thing():
    return Thing(random.random())


def make_set(n=1):
    s = set()
    ls = []
    for i in range(n):
        t = make_a_thing()
        s.add(id(t))
        ls.append(t)
    return s, ls


def make_smolset(n=1, thresh=0.5):
    s = SubSet()
    s.load_factor = thresh  # todo this doesn't work right because of the copy on resize thinger
    ls = []
    for i in range(n):
        t = make_a_thing()
        s.add(id(t))
        ls.append(t)
    return s, ls


def main():
    for thresh in [10, 20]:
        for exp in range(3, 7):
            n = 10**exp
            t0 = time.time()
            v, junk1 = make_smolset(n, thresh)
            t1 = time.time()
            s, junk2 = make_set(n)
            t2 = time.time()
            build_v = t1-t0
            build_s = t2-t1
            ratio = asizeof(v) / asizeof(s)
            """
            print('smol build', t1-t0)
            print('set build', t2-t1)
            """
            # check sizes
            print(f" === {n} items @ {thresh} === ")
            """
            print('smol size:', asizeof(v))
            print('set size:', asizeof(s))
            """
            # check lookups
            lookies = []
            for i in s:
                lookies.append(i)
                if len(lookies) > 100:
                    break

            t0 = time.time()
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

            print('ratio', round(1/ratio, 3))
            # print(len(v), len(s))
            # print(ratio)

main()