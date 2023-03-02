import numpy as np
import time

l = list(range(120010))
t1 = time.time()
a = l[-1000::]
# print(a)
print((time.time() - t1))
