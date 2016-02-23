#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Standalone POS-tagger implementation using TextBlob's averaged perceptron.
"""
import argparse
import codecs
import docx
import os
import re
import sys
import unicodedata
from itertools import izip_longest
from string import punctuation as punct
from cStringIO import StringIO
from textblob import Blobber
from textblob_aptagger import PerceptronTagger
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfpage import PDFPage


def filter_files(file_list):
    """
    Filter out all non-text files.
    """
    valid_ext = ['.txt', '.docx', '.pdf']
    return [f for f in file_list if os.path.splitext(f)[-1] in valid_ext]


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
    # read pdf file
    elif re.match(r'.pdf', fext):
        contents = pdf_read(fpath)
    # read txt of file without any extension
    elif re.match(r'.txt', fext) or not fext:
        with codecs.open(fpath, 'r', encoding='utf-8') as fopened:
            contents = fopened.read()
    return normalize_text(contents)


def tag(text):
    """
    Process given text with PerceptronTagger.

    Args:
        | *text* (str) -- raw text data

    Returns:
        | *ptagged_text* (str) -- tagged text

    """
    blob = Blobber(pos_tagger=PerceptronTagger())
    parsed_text = blob(text)

    # add excluded punctuation back into the sentences
    full_tagged_sents = {}
    for i, sent in enumerate(parsed_text.sentences):
        full_tagged_sents[i] = []
        idx = 0
        for token1, token2 in izip_longest(sent.tags, sent.tokens):
            if token2 in punct:
                full_tagged_sents[i].append((token2, 'PUNC', idx))
            elif token1:
                full_tagged_sents[i].append(token1 + (idx, ))
            idx += 1
    # convert to str
    print full_tagged_sents
    return 0


def main(args):
    """
    Create directories and save the results.
    Handle given arguments accordingly.
    """
    if args.file:
        fdata = read_input_file(args.file)
        tagged = tag(fdata)
    elif args.dir:
        files = os.listdir(os.path.join(os.getcwd(), args.dir))
        ffiles = filter_files(files)
        tagged_data = []
        for text_file in ffiles:
            fdata = read_input_file(text_file)
            tag(fdata)
            tagged_data.append()
    else:
        print 'Please provide a directory or a filename to process!'
        sys.exit(1)




if __name__ == '__main__':
    prs = argparse.ArgumentParser(description="""
                                  Standalone TexBlob's PerceptronTagger --
    a part-of-speech tagger based on the Averaged Perceptron algorithm which is
    faster and more accurate than NLTK's and pattern's default implementations.
    """)
    prs.add_argument('-d', '--dir',
                     help='Specify a directory with text files to process',
                     required=False)
    prs.add_argument('-f', '--file',
                     help='Specify a text file to process.',
                     required=False)
    prs.add_argument('-o', '--out',
                     help='Specify output directory.',
                     required=False)
    arguments = prs.parse_args()
    main(arguments)