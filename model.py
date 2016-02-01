#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
A collection of text processing methods used by nn-search.
This module also handles user query parsing, text preprocessing and text stats.
"""
from __future__ import division
import docx
import os
import re
import subprocess as sb
import sys
import unicodedata
from textblob import Blobber
from textblob_aptagger import PerceptronTagger

# for reading pdf
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfpage import PDFPage
from cStringIO import StringIO


def pdf_read(pdf):
    """
    Use PDFMiner to extract text from pdf file.
    <PDFMiner even though more low-level but pretty good tool to read pdfs>

    Args:
        *pdf* (str) -- path to pdf file

    Returns:
        *text* (str) -- a text extracted from pdf

    """
    # initalizing objects
    res_manager = PDFResourceManager()
    strio = StringIO()
    lps = LAParams()
    device = TextConverter(res_manager, strio, codec='utf-8', laparams=lps)
    interpreter = PDFPageInterpreter(res_manager, device)
    # opening a pdf file with 'rb' mode for reading binary files
    pdf_file = file(pdf, 'rb')
    for page in PDFPage.get_pages(pdf_file, maxpages=0, password='',
                                  caching=True, check_extractable=True):
        interpreter.process_page(page)
    # finishing up
    pdf_file.close()
    device.close()
    text = strio.getvalue()
    strio.close()
    return text


def normalize_text(text):
    """
    Remove non-utf8 characters.
    Convert text to ascii.

    <If you throw some utf-8 text to English POS-tagger, it might fail because
    even some English texts might contain weird chars, accents and diacritics.>

    Args:
        *chars* (str) -- strings of characters
    Returns:
        *ascii_text* (str) -- text converted to ascii

    """
    # removing some non-utf8 chars
    utext = re.sub(r'[^\x00-\x7F]+', '', text)
    try:
        utext = unicode(text, 'utf-8')
    except TypeError as err:
        # file is already unicode
        print err
    # converting to ascii
    ascii_text = unicodedata.normalize('NFKD', utext).encode('ascii', 'ignore')
    return ascii_text


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
    # read docx file
    if re.match(r'.docx', fext):
        doc = docx.Document(fpath)
        contents = ''
        for par in doc.paragraphs:
            contents = '\n'.join([contents, par.text])
    # read doc file
    elif re.match(r'.doc', fext):
        process = sb.Popen(['antiword', fpath], stdout=sb.PIPE)
        contents, err = process.communicate()
    # read pdf file
    elif re.match(r'.pdf', fext):
        contents = pdf_read(fpath)
    # read txt of file without any extension
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
    pass
