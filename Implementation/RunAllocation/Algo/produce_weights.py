#!/usr/bin/env python3                                                                                
# -*- coding: utf-8 -*-

import numpy as np
import random
import sys

analytic_num = int(sys.argv[1])
vers_num = int(sys.argv[2])
wfile = sys.argv[3]

with open(wfile, 'w') as wf:
    for v in range(vers_num):
        wf.write(f'{v+1}: ')
        s = np.random.random(analytic_num)
        for a in s[:-1]:
            wf.write(f'{round(a, 3)}, ')
        wf.write(f'{round(s[-1], 3)}\n')
