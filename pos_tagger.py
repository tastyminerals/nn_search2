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
        full_text = ' '.join([full_text, sent])
    return full_text


def main(args):
    """
    Create directories and save the results.
    Handle given arguments accordingly.
    """
    if not os.path.exists(args.out):
        os.mkdir(args.out)
    if args.file:
        print 'Processing "{0}"'.format(args.file)
        out_path = os.path.join(args.out,
                                'tagged_' + os.path.basename(args.file))
        data = read_file(args.file)
        tagged_text = tag(data)
        write_file(out_path, tagged_text)
    elif args.dir:
        files = [os.path.join(args.dir, fname) for fname
                 in os.listdir(args.dir)]
        for text_file in files:
            print 'Processing "{0}"'.format(text_file)
            out_path = os.path.join(args.out,
                                    'tagged_' + os.path.basename(text_file))
            data = read_file(text_file)
            if not data:
                continue
            tagged_text = tag(data)
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
