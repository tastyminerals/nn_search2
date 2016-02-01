#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
A collection of text processing methods used by nn-search.
This module also handles user query parsing and text stats.
"""
from __future__ import division
import docx
import os
import re
import sys
from textblob import Blobber
from textblob_aptagger import PerceptronTagger


def normalize_text(text):
    """
    Remove non-utf8 characters.

    Args:
        *chars* (str) -- strings of characters
    Returns:
        *clean_text* (str) -- normalized strings of characters

    """
    # data = re.sub(r'[^\x00-\x7F]+', '', fdata)  # potentially less strict
    bad_chars = '\x81\x8d\x8f\x90\x9d\x01\x03\x0b\x17\x1a\x1c\x1d\x05' \
                '\x06\x07\x10\x11\x12\x13\x14\x15\x16\x18\x1a\x19\x1e' \
                '\x1f\x04\x02\x08\x0c\x0e\x0f\x1b'
    clean_text = text.translate(None, bad_chars)
    return clean_text


def read_input_file(fpath):
    """
    Determine the file extension and act accordingly.
    Read the file and return its contents.

    Args:
        *fpath* (str) -- file path

    Returns:
        *contents* (str) -- file contents

    """
    fext = os.path.splitext(fpath)[-1]
    if re.match(r'.doc|.docx', fext):
        doc = docx.Document(fpath)

    elif re.match(r'.pdf', fext):
        pass

    elif re.match(r'.txt', fext) or not fext:
        with open(fpath, 'r') as fopened:
            contents = fopened.read()

    return normalize_text(contents)


def preprocess_query(query):
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




def textblob_parse(text):
    """
    Use TextBlob toolkit to process text.

    Args:
        *text* (str) -- raw text data

    Returns:
        *(Blobber)* -- Blobber object containing various results
        of text processing done by TextBlob module

    """
    blob = Blobber(pos_tagger=PerceptronTagger())
    return blob(text)


if __name__ == '__main__':
    read_input_file(sys.argv[1])
