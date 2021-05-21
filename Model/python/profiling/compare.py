import numpy as np
import time
from bitarray import bitarray

x = np.zeros(50584, dtype=int)
y = np.zeros(50584, dtype=int)

count = 0
start_time = time.perf_counter_ns()
for idx, (my_bit, other_bit) in enumerate(zip(x, y)):
    count += 1 if my_bit == other_bit else 0
end_time = time.perf_counter_ns()

zip_time = end_time - start_time

count = 0
start_time = time.perf_counter_ns()
idx = 0
while idx < 50584:
    count += 1 if x[idx] == y[idx] else 0
    idx += 1
end_time = time.perf_counter_ns()

loop_time = end_time - start_time

x = bitarray(50584)
x.setall(0)
y = bitarray(50584)
y.setall(0)

count = 0
start_time = time.perf_counter_ns()
differences = ~x & y
for idx, bit in enumerate(differences):
    if bit == 1:
        count += 1
end_time = time.perf_counter_ns()
bitlist_time = end_time - start_time

print(zip_time)
print(loop_time)
print(bitlist_time)
