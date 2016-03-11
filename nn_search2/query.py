#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
This module handles various query operations.
"""
from collections import OrderedDict as od
import re


def preprocess_query(query, short_treebank):
    """
    Check user query for errors.
    Convert it into ready to parse format.
    Convert all punctuation tags to PUNC.

    Args:
        |*short_treebank* (list) -- short POS-tags description
        |*query* (str) -- user query as entered in Entry widget

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
    penn_tags = short_treebank[1][1:]
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
    Iterate over a sentence dict and find query matches for each sentence.
    Decide what to highlight, single tokens or a range of tokens.

    Args:
        | *query* -- a list of preprocessed query tuples
        | *sents* -- a dict of sentence token tuples as returned by POS-tagger,
         ``{0: [(u'this', u'DT', 0), (u'is', u'VBZ', 1), (u'a', u'DT', 2),
            (u'tree', u'NN', 3)]}``

    Returns:
        | *matched_lst* -- a list of matched tokens per sentence

    """
    if not query:
        return None
    matched_dic = od()
    for sent_idx in sents:
        matched_dic[sent_idx] = match_query(query, sents[sent_idx])
    return matched_dic


def match_query(query, sent):
    """
    Run user query through the sentence and find all matched substrings.
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
    start = 0  # starting idx
    last = 0  # last iterated idx
    negation = False
    matches = []
    sent_len = len(sent)
    token = [None, None, 0]  # use dummy token for first iteration
    last_matched = False
    while start != sent_len:
        full_query = len(query)  # used to check if the query fully matched
        qmatch = []  # cache for matches, reset if the query not fully matched
        for qnum, qterm in enumerate(query):
            # if ! negation, we must break into while and restart query loop
            if negation:
                negation = False
                break
            # check if qterm idx allows any further search
            if qnum == 0 and qterm[2] is not None and (last + qterm[2] >
                                                       qterm[2]):
                start = sent_len
                break
            # check limit stretch
            if sent_len - token[2] == 1:
                start = sent_len
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
                                qmatch = update_cache(token, qmatch,
                                                      full_query)
                            # check here if the qterm was the last in a query
                            if full_query == 0:
                                # incl a range between first and last matches
                                s, e = [sent.index(qmatch[0]),
                                        sent.index(qmatch[-1])]
                                matches.append(sent[s:e+1])
                                last_matched = True
                                break
                            break
                    else:
                        last, start, full_query, last_matched, negation, \
                            qmatch = update_cache(token, qmatch, full_query,
                                                  True)
                        break
                # if idx and there is idx match act
                if qterm[2] is not None:
                    if qterm[2] >= token[2] - last:
                        last, start, full_query, last_matched, negation, \
                            qmatch = update_cache(token, qmatch, full_query)
                        # check here if the qterm was the last in a query
                        if full_query == 0:
                            # if it was append, incl a range between matches
                            s, e = [sent.index(qmatch[0]),
                                    sent.index(qmatch[-1])]
                            matches.append(sent[s:e+1])
                            last_matched = True
                            break
                        break
                    # if idx limit does not allow a match, break
                    else:
                        break
                # check here for ! negation node, disallow adding to qmatch
                if qterm[3]:
                    last, start, full_query, last_matched, negation, qmatch = \
                        update_cache(token, qmatch, full_query, True)
                    break
                # if idx limit does not exist, add token to qmatch cache
                last, start, full_query, last_matched, negation, \
                    qmatch = update_cache(token, qmatch, full_query)
                # check again if we have fully matched the query
                if full_query == 0:
                    # if it was append, incl a range between matches
                    s, e = [sent.index(qmatch[0]), sent.index(qmatch[-1])]
                    matches.append(sent[s:e+1])
                break
        # Check if a query term was ever matched
        # We handling various cases of breaking out of the loop here.
        # Check if we have any matches and see if the first qterm has no limit.
        if not last_matched and not query[0][2]:
            # check if the last term has a limit and compare qterm sum + limit
            # with the sent length, break if it is bigger
            if query[-1][2] and start + query[-1][2] + len(query) >= sent_len:
                start = sent_len
                break
        # now qterm has a limit and we need to make sure that the sent was
        # fully checked by comparing the start idx with the last token idx
        elif not last_matched and query[0][2]:
            start += 1
            break
    return matches


if __name__ == '__main__':
    pass
