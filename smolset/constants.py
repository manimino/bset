from array import array

# Map friendly typecodes like 'uint64' and 'float64' to the single-letter ones needed by array
# See https://docs.python.org/3/library/array.html for letter code examples
DTYPE_TO_ARRAY_TYPE = {
    'int8': None,
    'uint8': None,
    'int16': None,
    'uint16': None,
    'int32': None,
    'uint32': None,
    'int64': None,
    'uint64': None,
    'float32': None,
    'float64': None
}

# fill in the dtypes dynamically because this is platform-specific
for int_type in 'bhilq':
    size = array(int_type).itemsize * 8
    DTYPE_TO_ARRAY_TYPE[f'int{size}'] = int_type
    DTYPE_TO_ARRAY_TYPE[f'uint{size}'] = int_type.upper()

for float_type in 'fd':
    size = array(float_type).itemsize * 8
    DTYPE_TO_ARRAY_TYPE[f'float{size}'] = float_type
