#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
This module handles various query operations.
"""

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
    rx = re.compile('(".+"([A-Z$]{2,4})?({[0-9]+})?|' +
                    '(".+")?[A-Z$]{2,4}({[0-9]+})?)')
    for node in query_lst:
        try:
            match_gr = rx.search(node).group()
        except AttributeError:
            return 1, node
        if len(node) != len(match_gr):
            # return code 1 with the incorrect node
            return 1, node

    penn_tags = model.get_penn_treebank()[1][1:] + ('PUNC',)
    # convert query for further processing, check POS-tags
    conv_query = []
    for node in query_lst:
        word = re.match(".+", node)
        tag = re.match('(".+")?([A-Z$]{2,4}){?', node)
        idx = re.match('}[0-9]+{', node[::-1])
        if tag and tag.groups()[-1] not in penn_tags:
            return 2, tag.groups()[-1]
        conv_query.append([word, tag, idx])
    return conv_query


def parse_query(query):
    """
    Preprocess and parse user query.

    Args:
        *query* (str) -- user query string


    NN NN{1}
    NN VB
    'green'_JJ 'tree'_NN{2}
    'He'_PN !'goes'_VB{1} 'shop'_NN{5}
    """
    pass


if __name__ == '__main__':
    pass
