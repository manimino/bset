from array import array
from typing import Any


# Map friendly typecodes like 'uint64' and 'float64' to the single-letter ones needed by array
# See https://docs.python.org/3/library/array.html for letter code examples
# This has to be done at runtime to account for platform differences

UINT32_TYPE = None
UINT64_TYPE = None

INT32_TYPE = None
INT64_TYPE = None

FLOAT32_TYPE = None
FLOAT64_TYPE = None

STRING_TYPE = 'S'
OBJECT_TYPE = 'O'


for int_type in 'bhilq':
    size = array(int_type).itemsize * 8
    if size == 32:
        INT32_TYPE = int_type
        UINT32_TYPE = int_type.upper()
    elif size == 64:
        INT64_TYPE = int_type
        UINT64_TYPE = int_type.upper()

for float_type in 'fd':
    size = array(float_type).itemsize * 8
    if size == 32:
        FLOAT32_TYPE = float_type
    elif size == 64:
        FLOAT64_TYPE = float_type


def call_type(item: Any) -> str:
    if isinstance(item, int):
        return INT64_TYPE
    if isinstance(item, float):
        return FLOAT64_TYPE
    if isinstance(item, str):
        return STRING_TYPE
    return OBJECT_TYPE