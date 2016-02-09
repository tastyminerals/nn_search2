#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
This module handles various query operations.
"""

import re

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
    re.search('(".+")?([A-Z]+)?({[0-9]+})?', query).group()
    pass

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
