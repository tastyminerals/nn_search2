#!/usr/bin/env python2
# -*- coding: utf-8 -*-
import re

# convert sent
def preformat_tagged_sent(sent):
    """
    Create a tuple of ('"word"POS-tag', 'index') from tagged sentence tokens.

    Args:
        *sent* -- tokenized sentence as it received from a POS-tagger

    Returns:
        *sent_mod* -- modified sentence for query matching

    """
    sent_mod = []
    for token in sent:
        token = ''.join(['"', token[0], '"', token[1]]), token[2]
        sent_mod.append(token)
    return sent_mod

def preformat_query():
    """
    <Since I decided that I'd better match token + POS-tag with one match,
    the query needs to be altered in order to handle '"NN' matches '"NNP' cases
    in the matching function.
    Add a '_' to each query POS-tag.
    """
    query = [(u'"g"NNP', None, False), (u'"DT', 2, False), (u'"f"', None, False)]
    new_query = []
    for q in query:
        if re.match(r'[A-Z]+', q[0][::-1]):
            q = (''.join([q[0], '_']), q[1], q[2])
            new_query.append(q)
    print new_query

def matching(query, sent):
    """
    Find all substrings in the sentence that match the query.

    Args:
        | *query* (list) -- list of query tuples, [('"word"NN', 0, False)]
        | *sent* (list) -- list of sentence token tuples

    Returns:
        | *matches* (list) -- list of lists of found matches

    """
    start = 0  # sent pointer to continue where last stopped
    last = 0  # index of the last match
    matches = []  # matched substrings
    while start != len(fsent):
        full_query = len(query)  # used to check whether the query fully matched
        qmatch = []  # cache for matches, resets if the query not fully matched
        for qterm in query:
            last_matched = False  # True if last qterm matched anything
            for token in fsent[start:]:
                # first check if qterm index allows further search
                if qterm[1] is not None and qterm[1] < token[1] - last:
                    last = token[1] + 1
                    break
                # if there is no match just proceed with the loop
                if not re.search(qterm[0], token[0]):
                    continue
                # if there was a match, check index limit
                if qterm[1] == 0 or qterm[1]:
                    if qterm[1] >= token[1] - last:
                        last = token[1] + 1
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
                        break
                    # idx limit does not allow a match, break
                    else:
                        break
                # idx limit does not exist, add token to qmatch cache
                else:
                    last = token[1] + 1
                    start = last
                    full_query -= 1
                    qmatch.append(token)
                    last_matched = True
                if full_query == 0:
                    matches.append(qmatch)
                break
            # check if a query term was ever matched, if not, break while
            if not last_matched:
                start += 1
                break
    return matches


sent = {0: [(u'a', u'DT', 0), (u'b', u'NNP', 1), (u'c', u'NN', 2),
            (u'd', u'DT', 3), (u'e', u'NNP', 4), (u'f', u'NN', 5),
            (u'g', u'DT', 6), (u'h', u'VBN', 7), (u'i', u'NN', 8),
            (u'j', u'DT', 9), (u'k', 'ZZZ', 10), (u'l', u'NN', 11),
            (u'm', u'VB', 12), (u'n', u'NN', 13), (u'o', u'NN', 14),
            (u'p', u'NN', 15), (u'q', u'NN', 16), (u'r', u'WRB', 17)]}
query = []
query.append([(u'"NNP', None, False), (u'"DT', 2, False), (u'"f"', None, False)])
query.append([(u'"NNP', 1, False), (u'"DT', 2, False), (u'"f"', None, False)])
query.append([(u'"DT', None, False), (u'"ZZZ', 10, False), (u'"NN', 0, False)])
query.append([(u'"g"', 10, False), (u'"ZZZ', 3, False), (u'"NN', 0, False)])
query.append([(u'"j"', None, False), (u'"WRB', None, False)])
query.append([(u'"DTT', 0, False), (u'"r"', 16, False)])
query.append([(u'"DTT', None, False), (u'"ZZZ', 10, False), (u'"r"', None, False)])
query.append([(u'"NNP', None, False), (u'"NN', 10, False)])
query.append([(u'"NN"', None, False), (u'"NN"', None, False)])
fsent= preformat_tagged_sent(sent[0])
print fsent
for q in query:
    m = matching(q, fsent)
    print m

preformat_query()