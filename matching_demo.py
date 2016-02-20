#!/usr/bin/env python2
# -*- coding: utf-8 -*-
import re

sent = [(u'a', u'DT', 0), (u'b', u'NNP', 1), (u'c', u'NN', 2),
        (u'd', u'DT', 3), (u'e', u'NNP', 4), (u'f', u'NN', 5),
        (u'g', u'DT', 6), (u'h', u'VBN', 7), (u'i', u'NN', 8),
        (u'j', u'DT', 9), (u'k', 'ZZZ', 10), (u'l', u'NN', 11),
        (u'm', u'VB', 12), (u'n', u'NN', 13), (u'o', u'NN', 14),
        (u'p', u'NN', 15), (u'q', u'NN', 16), (u'r', u'WRB', 17)]

query = [[(None, 'DT', None, False), (None, 'NNP', 1, False), (None, 'NN', None, False)]]


def matching(query, sent):
    start = 0
    last = 0
    matches = []
    while start != len(sent):
        full_query = len(query)  # used to check whether the query fully matched
        qmatch = []  # cache for matches, resets if the query not fully matched
        for qterm in query:
            last_matched = False
            for token in sent[start:]:
                print 'Iterating qterm:', qterm, 'token:', token, 'from start:', start, 'last:', last
                # first check if qterm index allows further search
                print 'Checking, idx limit for qterm is', qterm[2], 'current diff', token[2] - last
                if qterm[2] is not None and qterm[2] < token[2] - last:
                    last = token[2] + 1
                    print 'Limit! BREAK!'
                    break
                # if word and there is no word match just proceed to next token
                if qterm[0] is not None and not qterm[0] == token[0]:
                    print 'word not matched! continue'
                    continue
                # if tag and there is no tag match just proceed to next token
                if qterm[1] is not None and not qterm[1] == token[1]:
                    print 'POS-tag not matched! continue'
                    continue
                # if idx and there is idx match act
                print 'WORD and TAG matched, checking idx:', qterm[2]
                if qterm[2] is not None:
                    if qterm[2] >= token[2] - last:
                        print 'IDX MATCH!'
                        last = token[2] + 1
                        start = last
                        full_query -= 1
                        qmatch.append(token)
                        last_matched = True
                        # check here if the qterm was the last in a query
                        if full_query == 0:
                            # if it was append a qmatch before we break
                            matches.append(qmatch)
                            last_matched = True
                            break
                        print 'BREAK after IDX MATCH!'
                        break
                    # if idx limit does not allow a match, break
                    else:
                        print 'NO IDX MATCH!, BREAK'
                        break
                # if idx limit does not exist, add token to qmatch cache
                print 'NO IDX, adding to qmatch'
                last = token[2] + 1
                start = last
                full_query -= 1
                qmatch.append(token)
                last_matched = True
                # check again if we have fully matched the query
                if full_query == 0:
                    print 'FULL MATCH! adding to matches'
                    matches.append(qmatch)
                break
        # check if a query term was ever matched, if not, break while
        if not last_matched:
            print 'NEVER MATCHED! BREAK'
            start += 1
            break
    return matches

for q in query:
    m = matching(q, sent)
    print m
