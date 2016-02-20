#!/usr/bin/env python2
# -*- coding: utf-8 -*-


sent = [(u'a', u'DT', 0), (u'b', u'NNP', 1), (u'c', u'NN', 2),
        (u'd', u'DT', 3), (u'e', u'NNP', 4), (u'f', u'NN', 5),
        (u'g', u'DT', 6), (u'h', u'VBN', 7), (u'i', u'NN', 8),
        (u'j', u'DT', 9), (u'k', 'ZZZ', 10), (u'l', u'NN', 11),
        (u'm', u'VB', 12), (u'n', u'NN', 13), (u'o', u'NN', 14),
        (u'p', u'NN', 15), (u'q', u'NN', 16), (u'r', u'WRB', 17)]

query = [[('a', 'DT', None, False), (None, 'NN', 1, False), ('d', 'DT', 0, False)]]


def matching(query, sent):
    start = 0
    last = 0
    matches = []
    while start != len(sent):
        full_query = len(query)  # used to check whether the query fully matched
        qmatch = []  # cache for matches, resets if the query not fully matched
        for qterm in query:
            last_matched = False
            for token in sent:
                # first check if qterm index allows further search
                # if word and there is no word match just proceed to next token
                # if tag and there is no tag match just proceed to next token
                # if idx and there is no idx match act

                # check here if the qterm was the last in a query, if it was append a qmatch before we break
                pass


        # check if a query term was ever matched, if not, break while
        if not last_matched:
            start += 1
            break
    return matches

for q in query:
    m = matching(q, sent)
    print m
