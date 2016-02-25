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
#from query import match_query

SENT = [(u'a', u'DT', 0), (u'b', u'NNP', 1), (u'c', u'NN', 2),
        (u'd', u'DT', 3), (u'e', u'NNP', 4), (u'f', u'NN', 5),
        (u'g', u'DT', 6), (u'h', u'VBN', 7), (u'i', u'NN', 8),
        (u'j', u'DT', 9), (u'k', 'ZZZ', 10), (u'l', u'NN', 11),
        (u'm', u'VB', 12), (u'n', u'NN', 13), (u'o', u'NN', 14),
        (u'p', u'NN', 15), (u'q', u'NN', 16), (u'r', u'WRB', 17),
        (u'p', u'FF', 18), (u'q', u'FF', 19), (u'r', u'TT', 20)]

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
    [(None, 'NN', None, False), (None, 'NN', None, False)],
    [(None, 'FF', None, False), (None, 'TT', 2, False)]
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
     [(u'p', u'NN', 15), (u'q', u'NN', 16)]],
    [(u'p', u'FF', 18), (u'r', u'TT', 20)]
    ]

SENT1 = {0: [(u'The', u'DT', 0), (u'Prose', u'NNP', 1), (u'or', u'CC', 2),
             (u'Younger', u'NNP', 3), (u'Edda', u'NNP', 4), (u'was', u'VBD', 5),
             (u'written', u'VBN', 6), (u'in', u'IN', 7), (u'the', u'DT', 8),
             (u'early', u'JJ', 9), (u'13th', u'JJ', 10), (u'century', u'NN', 11),
             (u'by', u'IN', 12), (u'Snorri', u'NNP', 13), (u'Sturluson', u'NNP', 14),
             (u',', 'PUNC', 15), (u'who', u'WP', 16), (u'was', u'VBD', 17),
             (u'a', u'DT', 18), (u'leading', u'VBG', 19), (u'skald', u'NN', 20),
             (u',', 'PUNC', 21), (u'chieftain', u'NN', 22), (u',', 'PUNC', 23),
             (u'and', u'CC', 24), (u'diplomat', u'NN', 25), (u'in', u'IN', 26),
             (u'Iceland', u'NNP', 27), (u'.', 'PUNC', 28)],
        1: [(u'It', u'PRP', 0), (u'may', u'MD', 1), (u'be', u'VB', 2),
            (u'thought', u'VBN', 3), (u'of', u'IN', 4), (u'primarily', u'RB', 5),
            (u'as', u'IN', 6), (u'a', u'DT', 7), (u'handbook', u'NN', 8),
            (u'for', u'IN', 9), (u'aspiring', u'VBG', 10),
            (u'skalds', u'NNS', 11), (u'.', 'PUNC', 12)]
        }

#TEST_QUERIES1 = [[(None, 'DT', None, False), (None, 'NN', 2, False)]]
TEST_QUERIES1 = [[(None, 'DT', None, False)]]
#TEST_QUERIES1 = [[(None, 'NNP', None, False), (None, 'NNP', 2, False), (None, 'VBD', 2, False)]]

def match_query(query, sent):
    """
    Run user query through the sentences and find all matched substrings.
    <The function is huge, make sure you clearly understand what you're doing
    before changing anything.>

    Args:
        | *query* -- a list of preprocessed query tuples
        | *sent* -- a list of sentence token tuples as returned by POS-tagger

    Returns:
        | *matched* -- a list of tuples of matched sentence substrings

    """
    def update_cache(token, qmatch, full_query, neg=False):
        """
        Update temp cache that accumulates successful query matches.

        Args:
            | *token* -- sentence token tuple
            | *qmatch* -- temp cache for successful matches
            | *full_query* -- int of query lenght that gets reduced with each
              successful term match
            | *neg* (optional) -- True if we handle negation query term

        Returns:
            a list of updated parameters

        """
        last = token[2] + 1
        start = last
        full_query -= 1
        last_matched = True
        negation = False
        if neg:
            negation = True
        if not neg:
            qmatch.append(token)
        return [last, start, full_query, last_matched, negation, qmatch]

    print 'query:', query
    print 'sent:', sent
    start = 0  # starting idx
    last = 0  # last iterated idx
    negation = False
    matches = []
    sent_len = len(sent)
    token = [None, None, 0]  # use dummy token for first iteration
    while start != sent_len:
        full_query = len(query)  # used to check whether the query fully matched
        qmatch = []  # cache for matches, reset if the query not fully matched
        for qterm in query:
            if sent_len - token[2] == 1:
                start = sent_len
                break
            # if ! negation, we must break into while and restart query loop
            if negation:
                negation = False
                break
            # True if last qterm match was found, also remember last mastch idx
            last_matched = False
            for token in sent[start:]:
                # first check if qterm index allows further search
                if qterm[2] is not None and qterm[2] < token[2] - last:
                    # if negation, we add to qmatch and break
                    if qterm[3]:
                        last, start, full_query, last_matched, negation, \
                            qmatch = update_cache(token, qmatch, full_query)
                        break
                    last = token[2] + 1
                    break
                # if word and there is no word match just proceed to next token
                if qterm[0] is not None and not qterm[0] == token[0] and \
                   not qterm[3]:
                    print qterm, token, last_matched
                    print 'NO WORD MATCH, CONTINUE!'
                    continue
                # if tag and there is no tag match just proceed to next token
                if qterm[1] is not None and not qterm[1] == token[1] and \
                   not qterm[3]:
                    print qterm, token, last_matched
                    print 'NO TAG MATCH, CONTINUE!', token[2], sent_len
                    continue
                # check ! negation and handle all options accordingly
                if qterm[3] and (qterm[0] == token[0] or qterm[1] == token[1]):
                    print 'NEGATION with WORD AND TAG MATCH DETECTED!'
                    if qterm[2] is not None:
                        if qterm[2] >= token[2] - last:
                            last, start, full_query, last_matched, negation, \
                             qmatch = update_cache(token, qmatch,
                                                   full_query, True)
                            print 'NEGATION IDX MATCH, BREAK!'
                            break
                        else:
                            last, start, full_query, last_matched, negation, \
                             qmatch = update_cache(token, qmatch, full_query)
                            # check here if the qterm was the last in a query
                            if full_query == 0:
                                # if it was append a qmatch before we break
                                print '================', [sent.index(qmatch[0]), sent.index(qmatch[-1])]
                                s, e = [sent.index(qmatch[0]), sent.index(qmatch[-1])]
                                matches.append(sent[s:e+1])
                                print '>>>0', last_matched
                                last_matched = True
                                print '>>>1', last_matched
                                break
                            break
                    else:
                        last, start, full_query, last_matched, negation, \
                         qmatch = update_cache(token, qmatch, full_query, True)
                        break
                # if idx and there is idx match act
                if qterm[2] is not None:
                    print 'WORD AND TAG MATCH DETECTED, checking IDX!'
                    if qterm[2] >= token[2] - last:
                        print 'IDX MATCH!'
                        last, start, full_query, last_matched, negation, qmatch\
                            = update_cache(token, qmatch, full_query)
                        # check here if the qterm was the last in a query
                        if full_query == 0:
                            print 'FULL QUER MATCH!'
                            # if it was append a qmatch before we break
                            print '================', [sent.index(qmatch[0]), sent.index(qmatch[-1])]
                            s, e = [sent.index(qmatch[0]), sent.index(qmatch[-1])]
                            matches.append(sent[s:e+1])
                            print '>>>2', last_matched
                            last_matched = True
                            print '>>>3', last_matched
                            break
                        break
                    # if idx limit does not allow a match, break
                    else:
                        break
                # check here for ! negation node, disallow adding to qmatch
                if qterm[3]:
                    last, start, full_query, last_matched, negation, \
                     qmatch = update_cache(token, qmatch, full_query, True)
                    break
                # if idx limit does not exist, add token to qmatch cache
                last, start, full_query, last_matched, negation, \
                    qmatch = update_cache(token, qmatch, full_query)
                # check again if we have fully matched the query
                if full_query == 0:
                    print 'FULL QUER MATCH!'
                    print '================', [sent.index(qmatch[0]), sent.index(qmatch[-1])]
                    s, e = [sent.index(qmatch[0]), sent.index(qmatch[-1])]
                    matches.append(sent[s:e+1])
                break
        # Check if a query term was ever matched
        # We handling various cases of breaking out of the loop here.
        # Check if we have any matches and see if the first qterm has no limit.
        print 'CHECKING END', query, last_matched
        if not last_matched and not query[0][2]:
            # check if the last term has a limit and compare qterm sum + limit
            # with the sent length, break if it is bigger
            print 'CHECK LAST QTERM', start, '+', query[-1][2], '+', len(query), sent_len
            if query[-1][2] and start + query[-1][2] + len(query) >= sent_len:
                print 'NEVER MATCHED!!!'
                start = sent_len
                break
        # now qterm has a limit and we need to make sure that the sent was fully
        # checked by comparing the start idx with the last token idx
        elif not last_matched and query[0][2]:
            start += 1
            break
    return matches

def query_alg_test():
    results = []
    """
    for query in TEST_QUERIES:
        results.append(match_query(query, SENT))
    print results
    """
    for key in SENT1:
        for query in TEST_QUERIES1:
            results.append(match_query(query, SENT1[key]))
        print results

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
