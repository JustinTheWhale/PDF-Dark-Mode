import numpy as np
cimport numpy as np
cimport cython

DTYPE = np.uint8
ctypedef np.uint8_t DTYPE_t

@cython.boundscheck(False)
@cython.wraparound(False)
def parse_png(np.ndarray [DTYPE_t, ndim=3] color_array, int length,  int width):
    cdef np.ndarray [DTYPE_t, ndim=3] array = color_array
    cdef np.ndarray [DTYPE_t, ndim=1] changed = np.full(shape=3, fill_value=100, dtype=np.uint8)
    for i in range(0, length):
        for j in range(0, width):
            if array[i, j].tolist() == [0,0,0]:
                array[i, j] = changed
    return array
    