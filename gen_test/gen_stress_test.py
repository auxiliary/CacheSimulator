#!/usr/bin/env python
import random

n_addresses = 10000
address_length = 8
with open('stress_trace', 'w') as f:
    for i in range(n_addresses):
        address = ''
        for j in range(address_length):
            address += random.choice('0 1 2 3 4 5 6 7 8 9 a b c d e f'.split())

        f.write(address + ' ' + random.choice(['R', 'W']) + '\n')
