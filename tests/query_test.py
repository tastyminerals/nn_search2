#!/usr/bin/env python2
"""
Test for query matching algorithm.
"""
import os
import sys
sys.path.insert(0, os.path.join(os.pardir, 'nn_search2'))
import query
from test_data.query_tests import QUERIES, SENTS, GOLD

# run test queries
OUT = []
for sent in SENTS:
    for que in QUERIES:
        out = query.find_matches(que, sent)
        OUT.append(out)

# check the output results
flat_out = [d for a in OUT for b in a[0] for c in b for d in c]
flat_gold = [d for a in GOLD for b in a for c in b for d in c]

print 'Query test: %s!' % (flat_out == flat_gold)
