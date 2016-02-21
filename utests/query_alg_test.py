#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Tests for query matching algorithm
"""
import re
import unittest
import os
import sys
sys.path.insert(0, os.pardir)
import matching_demo_opt as demo


SENT = [(u'a', u'DT', 0), (u'b', u'NNP', 1), (u'c', u'NN', 2),
        (u'd', u'DT', 3), (u'e', u'NNP', 4), (u'f', u'NN', 5),
        (u'g', u'DT', 6), (u'h', u'VBN', 7), (u'i', u'NN', 8),
        (u'j', u'DT', 9), (u'k', 'ZZZ', 10), (u'l', u'NN', 11),
        (u'm', u'VB', 12), (u'n', u'NN', 13), (u'o', u'NN', 14),
        (u'p', u'NN', 15), (u'q', u'NN', 16), (u'r', u'WRB', 17)]

TEST_QUERIES = [
    [(None, 'VB', None, False), (None, 'NN', 1, False), (None, 'WRB', 0, True)],
    [(None, 'NNP', None, False), (None, 'DT', 2, False),
     (u'f', None, None, False)],
    [(None, 'NNP', 1, False), (None, 'DT', 2, False), ('f', None, None, False)],
    [(None, 'DT', None, False), (None, 'ZZZ', 10, False),
     (None, 'NN', 0, False)],
    [('g', None, 10, False), (None, 'ZZZ', 3, False), (None, 'NN', 0, False)],
    [('j', None, None, False), (None, 'WRB', None, False)],
    [(None, 'DT', 0, False), ('r', None, 16, False)],
    [(None, 'DT', None, False), (None, 'ZZZ', 10, False),
     ('r', None, None, False)],
    [(None, 'NNP', None, False), (None, 'NN', 10, False)],
    [(None, 'NN', None, False), (None, 'NN', None, False)]
    ]

GOLD = [
    [(u'm', u'VB', 12), (u'n', u'NN', 13), (u'o', u'NN', 14)],
    [(u'b', u'NNP', 1), (u'd', u'DT', 3), (u'f', u'NN', 5)],
    [(u'b', u'NNP', 1), (u'd', u'DT', 3), (u'f', u'NN', 5)],
    [(u'a', u'DT', 0), (u'k', 'ZZZ', 10), (u'l', u'NN', 11)],
    [(u'g', u'DT', 6), (u'k', 'ZZZ', 10), (u'l', u'NN', 11)],
    [(u'j', u'DT', 9), (u'r', u'WRB', 17)],
    [(u'a', u'DT', 0), (u'r', u'WRB', 17)],
    [(u'a', u'DT', 0), (u'k', 'ZZZ', 10), (u'r', u'WRB', 17)],
    [[(u'b', u'NNP', 1), (u'c', u'NN', 2)],
     [(u'e', u'NNP', 4), (u'f', u'NN', 5)]],
    [[(u'c', u'NN', 2), (u'f', u'NN', 5)],
     [(u'i', u'NN', 8), (u'l', u'NN', 11)],
     [(u'n', u'NN', 13), (u'o', u'NN', 14)],
     [(u'p', u'NN', 15), (u'q', u'NN', 16)]]
    ]


def query_alg_test():
    results = []
    for query in TEST_QUERIES:
        results.append(demo.matching(query, SENT))
    tests = []
    for gold, result in zip(GOLD, results):
        if len(result) == 1:
            for g, r in zip(gold, result[0]):
                 tests.append(g == r)
        else:
            for g, r in zip(gold, result):
                tests.append(g == r)
    if all(tests):
        print 'TESTS PASSED!'
    else:
        print 'TESTS FAILED!'


if __name__ == '__main__':
    query_alg_test()
