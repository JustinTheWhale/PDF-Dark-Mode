import numpy as np
from numba import jit, uint8


@jit(nopython=True, cache=True, fastmath={'fast'})
def speed(a):
    grey = np.full((3), fill_value=70, dtype=np.uint8)
    for i in range(len(a)):
        for j in range(len(a[0])):
            if np.sum(a[i, j]) == 0:
                a[i, j] = grey
    return a
