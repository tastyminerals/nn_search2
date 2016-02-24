#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Standalone POS-tagger implementation using TextBlob's averaged perceptron.
"""
import argparse
import codecs
import os
import re
import sys
import unicodedata
from itertools import izip_longest
from string import punctuation as punct
from textblob import Blobber
from textblob_aptagger import PerceptronTagger


def read_file(fpath):
    """
    Read the specified file.
    """
    try:
        with codecs.open(fpath, 'r', encoding='utf-8') as fopened:
            fdata = normalize_text(fopened.read())
    except (OSError, IOError):
        print 'Can not process "{0}", skipping'.format(fpath)
        return None
    return fdata


def write_file(out_path, tagged_text):
    """
    Write the results of processing to file.

    Args:
        | *out_path* (str) -- output file path
        | *tagged_text* (str) -- pos-tagged data
    """
    try:
        with codecs.open(out_path, 'w', encoding='utf-8') as fnew:
            fnew.write(tagged_text)
    except (OSError, IOError):
        print 'Can not write "{0}"!\n'.format(out_path) +\
              'Make sure there is enough free space on disk.'
        sys.exit(1)


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


def tag(text):
    """
    Process given text with PerceptronTagger.

    Args:
        | *text* (str) -- raw text data

    Returns:
        | *full_text* (str) -- tagged text

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
    full_text = ''
    for vals in full_tagged_sents.values():
        sent = ' '.join(['_'.join([token[0], token[1]]) for token in vals])
        full_text = '\n'.join([full_text, sent])
    return full_text.lstrip('\n')


def main(args, ui_call=False):
    """
    Create directories and save the results.
    Handle given arguments accordingly.
    Args:
        | *ui_call* (bool) -- True if main called from withing UI
        | *in_file_data* (dict) -- dict of type {fname: 'file data'}
        | *in_dir_data* (dict) -- dict of type {fname: 'file data'}

    <Processing various file types in batch mode is supported only via UI.
    I want ``pos_tagger.py`` to have only TextBlob and nltk as dependencies.>

    """
    in_file = None
    in_file_data = None
    in_dir = None
    in_dir_data = None
    if not ui_call:
        in_file = args.file
        in_dir = args.dir
        out_dir = args.out
    else:
        in_file_data, in_dir_data, out_dir = args

    if not os.path.exists(out_dir):
        os.mkdir(out_dir)
    # console single mode
    if in_file:
        print 'Processing "{0}"'.format(in_file)
        out_path = os.path.join(out_dir,
                                'tagged_' + os.path.basename(in_file))
        data = read_file(in_file)
        tagged_text = tag(data)
        write_file(out_path, tagged_text)
    # ui single mode
    elif in_file_data:
        in_fname = in_file_data.keys()[0]
        print 'Processing "{0}"'.format(in_fname)
        out_path = os.path.join(out_dir, 'tagged_' + os.path.basename(in_fname))
        tagged_text = tag(in_file_data[in_fname])
        write_file(out_path, tagged_text)
    # console batch mode
    elif in_dir:
        files = [os.path.join(in_dir, fname) for fname
                 in os.listdir(in_dir)]
        # only plain text files are supported in console batch mode!
        for text_file in files:
            print 'Processing "{0}"'.format(text_file)
            out_path = os.path.join(out_dir,
                                    'tagged_' + os.path.basename(text_file))
            data = read_file(text_file)
            if not data:
                continue
            tagged_text = tag(data)
            write_file(out_path, tagged_text)
    # UI batch mode
    elif in_dir_data:
        for fname, fdata in in_dir_data.items():
            if not fdata:
                continue
            print 'Processing "{0}"'.format(fname)
            out_path = os.path.join(out_dir,
                                    'tagged_' + os.path.basename(fname))
            tagged_text = tag(fdata)
            write_file(out_path, tagged_text)
    else:
        print 'Please provide a directory or a filename to process!'
        sys.exit(1)
    print 'POS-tagging complete!'


if __name__ == '__main__':
    prs = argparse.ArgumentParser(description="""
                                  Standalone TexBlob's PerceptronTagger --
    a part-of-speech tagger based on the Averaged Perceptron algorithm which is
    faster and more accurate than NLTK's and pattern's default implementations.
    """)
    prs.add_argument('-d', '--dir',
                     help='Specify a directory with text files to process.',
                     required=False)
    prs.add_argument('-f', '--file',
                     help='Specify a text file to process.',
                     required=False)
    prs.add_argument('-o', '--out',
                     help='Specify output directory.',
                     default=os.path.join(os.getcwd(), 'output'),
                     required=False)
    arguments = prs.parse_args()
    main(arguments)
