#!/usr/bin/env python2
"""
Test for query matching algorithm.
"""
import os
import sys
sys.path.insert(0, os.path.join(os.pardir, 'nn_search2'))
import query_temp as query
from test_data.query_tests import QUERIES, SENTS, GOLD

# run test queries
OUT = []
for sent in SENTS:
    for que in QUERIES:
        OUT.append(query.find_matches(que, sent))

# check the output results
for o1, o2 in zip(GOLD, OUT):
    assert o1 == o2

print 'Query test successful!'
