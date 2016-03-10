#!/usr/bin/env python2
"""
Test for query matching algorithm.
"""
import os
import sys
sys.path.insert(0, os.path.join(os.pardir, 'nn_search2'))
import query_temp as query
from test_data.query_tests import QUERIES, SENTS

# run test queries
for sent in SENTS:
    for que in QUERIES:
        print query.find_matches(que, sent)

# check the output results
