import pytest

from bset import bset


class Object:
    pass


@pytest.mark.parametrize("val", [-1, 1, -0.5, 0.5, 'string', 'ʊռɨƈօɖɛ🎉', Object()])
def test_add_one(val):
    b = bset()
    b.add(val)
    assert val in b
    assert list(b) == [val]


@pytest.mark.parametrize("val", [-1, 1, -0.5, 0.5, 'string', 'ʊռɨƈօɖɛ🎉', Object()])
def test_remove_one(val):
    b = bset([val])
    b.remove(val)
    assert len(b) == 0
    assert not b
