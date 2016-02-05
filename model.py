#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
A collection of text processing methods used by nn-search.
This module also handles user query parsing, text preprocessing and text stats.
"""
from __future__ import division
from collections import Counter
from itertools import izip_longest
import os
import re
import subprocess as sb
import sys
import unicodedata
from string import punctuation as punct
from cStringIO import StringIO


import docx
import hunspell
import matplotlib.pyplot as plt
import matplotlib.cm as cmx
import matplotlib.colors as colors
from nltk.corpus import stopwords
from textblob import Blobber, Word
from textblob_aptagger import PerceptronTagger
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfpage import PDFPage



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


def process_text(*args):
    """
    Process loaded text with textblob toolkit.
    Calculate text statistics.

    Args:
        *text* (str) -- raw text data

    Returns:
        | *parsed_text* (Blobber) -- Blobber obj which contains parse results
        | *full_tagged_sents* (dict) -- dict of
          *{send num: {word num: (word, POS-tag)}}*

    """
    model_queue, text = args
    blob = Blobber(pos_tagger=PerceptronTagger())
    parsed_text = blob(text)

    # add excluded punctuation back into the sentences
    full_tagged_sents = {}
    for i, sent in enumerate(parsed_text.sentences):
        full_tagged_sents[i] = []
        for token1, token2 in izip_longest(sent.tags, sent.tokens):
            if token2 in punct:
                full_tagged_sents[i].append((token2, 'PNCT'))
            elif token1:
                full_tagged_sents[i].append(token1)
    model_queue.put([parsed_text, full_tagged_sents])


def get_stats(text):
    """
    Use TextBlob object created after text extraction to get necessary stats.
    Calculate pos-tags.
    Calculate lexical diversity.
    Use hunspell to calculate correctness.

    Args:
        *text* (TextBlob) -- TextBlob object that contains parsed text data

    Returns:
        *stats* (dict) -- dictionary object containing important stats

    """
    # get token, word and sentence count
    token_cnt = len(text.tokens)
    word_cnt = len(text.words)
    sent_cnt = len(text.sentences)

    # calculate pos-tags
    tag_cnts = Counter((tup[1] for tup in text.tags))

    # calculate lexical diversity, unique words / total words
    parsed_lower = [w.lower() for w in text.words
                    if w.lower() not in stopwords.words('english')]
    total_tokens = [w for w in text.words
                    if w.lower() not in stopwords.words('english')]
    try:
        diversity = round(len(set(parsed_lower)) / len(total_tokens), 2)
    except ZeroDivisionError:
        diversity = 0.0

    # get polarity [-1.0, 1.0]
    # get subjectivity [0.0, 1.0], 0.0 - objective, 1.0 - subjective
    polarity = round(text.sentiment[0], 2)
    subjectivity = round(text.sentiment[1], 2)

    # calculate text correctness
    hspell = hunspell.HunSpell('/usr/share/hunspell/en_US.dic',
                               '/usr/share/hunspell/en_US.aff')
    correct = [hspell.spell(token) for token in text.words]
    try:
        correctness = 1 - correct.count(False) / correct.count(True)
        correctness = round(correctness, 2)
    except ZeroDivisionError:
        correctness = 0.0

    stats = {}
    stats['tokens'] = token_cnt
    stats['words'] = word_cnt
    stats['sents'] = sent_cnt
    stats['tags'] = tag_cnts
    stats['diversity'] = diversity
    stats['polar'] = polarity
    stats['subj'] = subjectivity
    stats['corr'] = correctness
    return stats

def plot_tags(tags_dic):
    bars = plt.bar(range(len(tags_dic)), tags_dic.values(), align='center')
    plt.xticks(range(len(tags_dic)), tags_dic.keys())
    for i in range(len(tags_dic)):
        bars[i].set_color(col)
    #plt.show()


if __name__ == '__main__':
    pass
