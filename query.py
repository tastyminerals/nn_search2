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
    node_idx = None
    for node in query_lst:
        if not node.startswith('!'):
            not_node = False
        else:
            not_node = True
        tag = re.match('(".+")?([A-Z$]{2,4}){?', node)
        if tag and tag.groups()[-1] not in penn_tags:
            return 2, tag.groups()[-1]
        # separate idx from node
        if node.endswith('}'):
            node_idx = int(re.search('{([0-9]+)}$', node).groups()[-1])
            node = re.sub('}[0-9]+{', '', node[::-1], 1)[::-1]
        # add formatted query to list
        ready_query.append((node, node_idx, not_node))
        node_idx = None
    print ready_query
    return ready_query


def parse_query(query):
    """
    Preprocess and parse user query.

    Args:
        *query* (str) -- user query string

    """
    pass


if __name__ == '__main__':
    pass
