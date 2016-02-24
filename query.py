#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
This module handles various query operations.
"""
from collections import OrderedDict as od
import re
import model


def preprocess_query(query):
    """
    Check user query for errors.
    Convert it into ready to parse format.
    Convert all punctuation tags to PUNC.

    Args:
        *query* (str) -- user query as entered in Entry widget

    Returns:
        *prequery* () -- preprocessed query

    """
    query_lst = query.split()
    # check query syntax
    rx = re.compile('!?(".+"([A-Z$]{2,4})?({[0-9]+})?|' +
                    '!?(".+")?[A-Z$]{2,4}({[0-9]+})?)')
    for node in query_lst:
        try:
            match_gr = rx.search(node).group()
        except AttributeError:
            return 1, node
        if len(node) != len(match_gr):
            # return code 1 with the incorrect node
            return 1, node

    # check POS-tags correctness
    penn_tags = model.get_penn_treebank()[1][1:] + ('PUNC',)
    ready_query = []
    # convert query for further processing, check POS-tags
    for node in query_lst:
        if not node.startswith('!'):
            not_node = False
        else:
            not_node = True
        word = re.match(r'"(.+)"', node) or None
        tag = re.match(r'(".+")?([A-Z$]{2,4}){?', node) or None
        idx = re.match(r'}([0-9]+){', node[::-1]) or None
        if tag and tag.groups()[-1] not in penn_tags:
            return 2, tag.groups()[-1]
        if word:
            word = word.group(1)
        else:
            word = None
        if tag:
            tag = tag.group(2)
        else:
            tag = None
        if idx:
            idx = int(idx.group(1)[::-1])
        else:
            idx = None
        ready_query.append((word, tag, idx, not_node))
    return ready_query


def find_matches(query, sents):
    """
    Iterate over a sentences dict and find query matches for each sentence.
    Decide what to highlight, single tokens or a range of tokens.

    Args:
        | *query* -- a list of preprocessed query tuples
        | *sents* -- a dict of sentence token tuples as returned by POS-tagger,
         ``{0: [(u'this', u'DT', 0), (u'is', u'VBZ', 1), (u'a', u'DT', 2),
            (u'tree', u'NN', 3)]}``

    Returns:
        | *matched_lst* -- a list of matched tokens per sentence
        | *single_marker* -- True if matching single tokens

    """
    # decide between a range and a single token
    single_marker = True if len(query) == 1 else False
    if not query:
        return None, single_marker
    matched_dic = od()
    for sent_idx in sents:
        matched_dic[sent_idx] = [item1 for item0 in
                                 match_query(query, sents[sent_idx])
                                 for item1 in item0]
    return matched_dic, single_marker
    # This is a green tree. The tree is big.


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
    start = 0
    last = 0
    negation = False
    matches = []
    while start != len(sent):
        print 'WHILE loop'
        full_query = len(query)  # used to check whether the query fully matched
        qmatch = []  # cache for matches, reset if the query not fully matched
        for qterm in query:
            print 'QTERM loop'
            # if ! negation, we must break into while and restart query loop
            if negation:
                print 'NEGATION BREAKING TO WHILE'
                negation = False
                break
            last_matched = False
            for token in sent[start:]:
                print 'token loop, iterating:', qterm, 'with token:', token
                # first check if qterm index allows further search
                if qterm[2] is not None and qterm[2] < token[2] - last:
                    print 'EARLY BREAK!', start, len(sent)
                    # if negation, we add to qmatch and break
                    if qterm[3]:
                        last, start, full_query, last_matched, negation, \
                         qmatch = update_cache(token, qmatch, full_query)
                        break
                    last = token[2] + 1
                    print 'ABOUT TO BREAK!'
                    break
                # if word and there is no word match just proceed to next token
                if qterm[0] is not None and not qterm[0] == token[0] and \
                   not qterm[3]:
                    continue
                # if tag and there is no tag match just proceed to next token
                if qterm[1] is not None and not qterm[1] == token[1] and \
                   not qterm[3]:
                    continue
                # check ! negation and handle all options accordingly
                if qterm[3] and (qterm[0] == token[0] or qterm[1] == token[1]):
                    if qterm[2] is not None:
                        if qterm[2] >= token[2] - last:
                            last, start, full_query, last_matched, negation, \
                             qmatch = update_cache(token, qmatch,
                                                   full_query, True)
                            break
                        else:
                            last, start, full_query, last_matched, negation, \
                             qmatch = update_cache(token, qmatch, full_query)
                            # check here if the qterm was the last in a query
                            if full_query == 0:
                                # if it was append a qmatch before we break
                                matches.append(qmatch)
                                last_matched = True
                                break
                            break
                    else:
                        last, start, full_query, last_matched, negation, \
                         qmatch = update_cache(token, qmatch, full_query, True)
                        break
                # if idx and there is idx match act
                if qterm[2] is not None:
                    if qterm[2] >= token[2] - last:
                        print 'IDX MATCH!'
                        last, start, full_query, last_matched, negation, \
                         qmatch = update_cache(token, qmatch, full_query)
                        # check here if the qterm was the last in a query
                        if full_query == 0:
                            # if it was append a qmatch before we break
                            matches.append(qmatch)
                            last_matched = True
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
                    matches.append(qmatch)
                break
        # check if a query term was ever matched, if not, break while
        #if not last_matched:
        #    print 'NEVER MATCHED, BREAKING!'
        #    start += 1
        #    break
    return matches


if __name__ == '__main__':
    pass
