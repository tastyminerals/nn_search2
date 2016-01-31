#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
A collection of text processing methods used by nn-search.
This module also handles user query parsing and text stats.
"""
from __future__ import division
import docx
import re
import sys
from textblob import Blobber
from textblob_aptagger import PerceptronTagger


def read_input_file(fpath):
    """
    Determine whether a file is ".docx" or plain ".txt".
    Read the file and return its contents.

    Args:
        *fpath* (str) -- file path

    Returns:
        *contents* (str) -- file contents

    """
    rxdoc = re.compile(r'.doc|.docx')
    rxpdf = re.compile(r'.pdf')
    rxtxt = re.compile(r'.txt|.rst')

    doc = docx.Document(fpath)
    for t in doc.paragraphs:
        print t.text


def preprocess_query(query):
    pass

def parse_query(query):
    """
    Preprocess user query.
    Parse user query and search through text for matched terms.
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
    read_input_file('Einladung_Deutschland.docx')
