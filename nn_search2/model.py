#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
A collection of text processing methods used by nn-search.
This module also handles user query parsing, text preprocessing and text stats.
"""
from __future__ import division
from collections import Counter, OrderedDict as od
import csv
import os
import platform
import random
import re
from string import punctuation
import subprocess as sb
import unicodedata
from cStringIO import StringIO
import docx
if not platform.system() == 'Windows':
    import hunspell
import matplotlib
matplotlib.use('Agg')  # fixing threading issue on Windows
import matplotlib.pyplot as plt
import matplotlib.cm as cmx
import matplotlib.colors as colors
import nltk
from nltk.corpus import stopwords
from nltk.tag.perceptron import PerceptronTagger
from textblob import TextBlob
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfpage import PDFPage
from colors import COLLECTION


NLTK_PENN = (u'CC', u'CD', u'DT', u'EX', u'FW', u'IN', u'JJ', u'JJR', u'JJS',
             u'LS', u'MD', u'NN', u'NNP', u'NNPS', u'NNS', u'PDT', u'POS',
             u'PRP', u'PRP$', u'RB', u'RBR', u'RBS', u'RP', u'SYM', u'TO',
             u'UH', u'VB', u'VBD', u'VBG', u'VBN', u'VBP', u'VBZ', u'WDT',
             u'WP', u'WP$', u'WRB')


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
    Remove all text formatting.

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
    # remove formatting
    stripped_text = ' '.join(re.sub(r'\n', ' ', ascii_text).split())
    return stripped_text


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
    # TextBlob runs POS-tagging
    model_queue, text = args
    parsed_text = TextBlob(text)
    # POS-tagging with nltk again because TextBlob sent.tags is too slow
    tagger = PerceptronTagger()
    tagset = None
    sent_detector = nltk.data.load('tokenizers/punkt/english.pickle')
    sents_tokenized = sent_detector.tokenize(text)
    tokenized = []
    for sent in sents_tokenized:
        tokenized.append(nltk.tokenize.word_tokenize(sent, language='english'))
    pos_sents = od()
    for i, sent_toks in enumerate(tokenized):
        pos_text = nltk.tag._pos_tag(sent_toks, None, tagger)
        joined_tags = [(pos[0], 'PUNC' if pos[1] not in NLTK_PENN else pos[1],
                        n) for n, pos in enumerate(pos_text)]
        pos_sents[i] = joined_tags
    model_queue.put([parsed_text, pos_sents])


def get_stats(model_queue, tblob):
    """
    Use TextBlob object created after text extraction to get necessary stats.
    Calculate pos-tags.
    Calculate lexical diversity.
    Use hunspell to calculate correctness.

    Args:
        | *model_queue* (Queue) -- Queue object
        | *tblob* (TextBlob) --TextBlob object

    Returns:
        *stats* (dict) -- dictionary object containing important stats

    """
    # get token, word and sentence count
    token_cnt = len(tblob.tokens)
    word_cnt = len(tblob.words)
    sent_cnt = len(tblob.sentences)

    # calculate pos-tags
    tag_cnts = Counter((tup[1] for tup in tblob.tags))
    english_stopwords = stopwords.words('english')
    # calculate lexical diversity, unique words / total words
    parsed_lower = [w.lower() for w in tblob.words
                    if w.lower() not in english_stopwords]
    total_tokens = [w for w in tblob.words
                    if w.lower() not in english_stopwords]
    try:
        diversity = round(len(set(parsed_lower)) / len(total_tokens), 2)
    except ZeroDivisionError:
        diversity = 0.0

    # get polarity [-1.0, 1.0]
    # get subjectivity [0.0, 1.0], 0.0 - objective, 1.0 - subjective
    polarity = round(tblob.sentiment[0], 2)
    subjectivity = round(tblob.sentiment[1], 2)

    if not platform.system() == 'Windows':
        # calculate text correctness
        hspell = hunspell.HunSpell('/usr/share/hunspell/en_US.dic',
                                   '/usr/share/hunspell/en_US.aff')
        correct = [hspell.spell(token) for token in tblob.words]
        try:
            correctness = 1 - correct.count(False) / correct.count(True)
            correctness = round(correctness, 2)
        except ZeroDivisionError:
            correctness = 0.0
    else:
        correctness = 'Unix only'

    stats = {}
    stats['tokens'] = token_cnt
    stats['words'] = word_cnt
    stats['sents'] = sent_cnt
    stats['tags'] = tag_cnts
    stats['diversity'] = diversity
    stats['polar'] = polarity
    stats['subj'] = subjectivity
    stats['corr'] = correctness
    model_queue.put(stats)


def get_penn_treebank():
    """
    Read Penn Treebank tags, format and return.

    Returns:
        *penn* (list) -- a list of two lists with Penn Treebank descriptions

    """
    with open(os.path.join('data', 'penn_tags.csv'), 'rb') as fcsv:
        penn_reader = csv.reader(fcsv, delimiter=',')
        penn = [row for row in penn_reader
                if row and not row[0].startswith('#')]
    return zip(*penn)


def get_graphs_data(model_queue, tags_dic, current_fname, process_res):
    """
    Run plot_tags() and get_ngrams()
    Put results in a Queue.

    Args:
        | *model_queue* (Queue) -- Queue object
        | *tags_dic* (dict) -- dict with POS-tag counts
        | *current_fname* (str) -- name of the loaded file
        | *process_res* (TextBlob) -- TextBlob object

    """
    plt.ioff()  # fixing threading on Windows
    # make plots and sort POS-tags
    ordered_pos = plot_tags(tags_dic, current_fname)
    # get most frequent words/ngrams counts
    mostn, ngram2, ngram3 = get_ngrams(process_res)
    # put everything into a Queue
    model_queue.put(ordered_pos)
    model_queue.put([mostn, ngram2, ngram3])


def get_ngrams(txtblob_obj):
    """
    Calculate word and ngram counts for Graphs option.
    Calculate top n frequent words.
    Calculate top n 2-grams
    Calculate top n 3-grams

    Args:
        *txtblob_obj* (Blob) -- object containing parse results

    Returns:
        |*mostn* (list) -- a list of n most frequent words
        |*ngram2* (list) -- a list of n most frequent 2-grams
        |*ngram3* (list) -- a list of n most frequent 3-grams

    """
    counter = Counter(txtblob_obj[0].words)
    counts_dic = od(counter.most_common())
    tags_dic = dict(txtblob_obj[0].tags)
    # POS-tags included into most frequent words list
    include = ('JJ', 'JJR', 'JJS', 'NN', 'NNS', 'NNP', 'NNPS', 'VB', 'VBG')
    # get n most frequent words
    mostn = [(k, counts_dic[k])
             for k in counts_dic if tags_dic.get(k) in include][:10]
    ngram2_cnt = Counter([(n[0], n[1]) for n in txtblob_obj[0].ngrams(2)])
    ngram3_cnt = Counter([(n[0], n[1], n[2]) for n
                          in txtblob_obj[0].ngrams(3)])
    ngram2 = [(n[0], ngram2_cnt[n[0]]) for n in ngram2_cnt.most_common(10)]
    ngram3 = [(n[0], ngram3_cnt[n[0]]) for n in ngram3_cnt.most_common(10)]
    return mostn, ngram2, ngram3


def plot_tags(tags_dic, save_fname):
    """
    Create and save plots for 'Graphs' option.
    These plot files shall be grabbed and included into UI.

    Args:
        | *tags_dic* (dict) -- dictionary of POS-tag occurrences
        | *save_fname* (str) -- currently processed file name without extension

    Returns:
        *odd* (OrderedDict) -- frequency sorted POS-tags

    """
    matplotlib.rc('font', **{'size': 13})
    # create POS-tags distribution plot
    odd = od(sorted([(k, v) for k, v in tags_dic.items()], key=lambda x: x[1]))
    bars = plt.barh(range(len(odd)), odd.values(), align='center')
    plt.title('Part-of-speech tags statistics')
    plt.yticks(range(len(odd)), odd.keys())
    plt.xlabel('Occurrence')
    plt.ylabel('POS-tags')
    plt.grid(True)
    plt.margins(y=0)
    random.shuffle(COLLECTION)
    for i in range(len(tags_dic)):
        bars[i].set_color(COLLECTION[i])
    plt.savefig(os.path.join('_graphs', save_fname + '.png'))
    # create functional / non-fuctional words pie chart
    plt.clf()
    matplotlib.rc('font', **{'size': 16})
    functional = ('DT', 'PDT', 'PRP', 'PRP$', 'IN', 'CC', 'UH', 'RP', 'WRB',
                  'WP$', 'WDT', 'WP', 'EX', 'MD', 'TO')
    content = ('JJ', 'JJR', 'JJS', 'NN', 'NNS', 'NNP', 'NNPS', 'RB', 'RBR',
               'RBS', 'VB', 'VBD', 'VBG', 'VBN', 'VBP', 'VBZ')
    fwords = sum([tags_dic[k] for k in tags_dic if k in functional])
    cwords = sum([tags_dic[k] for k in tags_dic if k in content])
    try:
        fratio = round(fwords / (fwords + cwords) * 100, 1)
        cratio = round(cwords / (fwords + cwords) * 100, 1)
    except ZeroDivisionError:
        fratio = 0.0
        cratio = 0.0
    labels = ['functional', 'content']
    sizes = [fratio, cratio]
    pie_colors = ['salmon', 'royalblue']
    plt.pie(sizes, labels=labels, colors=pie_colors, autopct='%1.1f%%',
            shadow=True, startangle=90)
    # Set aspect ratio to be equal so that pie is drawn as a circle.
    plt.axis('equal')
    # increasing fonts in a pie chart
    plt.savefig(os.path.join('_graphs', save_fname + '_pie.png'))
    plt.clf()
    return od(reversed(list(odd.items())))


def get_search_stats(model_queue, matches, text):
    """
    Get some search stats.

    Args:
        | *matches* -- dict of matching results
        | *text* -- Text widget text

    Returns:
        | *mcnt* -- number of matched terms
        | *mlen* -- length of matched characters
        | *mratio* -- ratio of matched characters

    """
    # get number of matches
    mcnt = sum([len(vals) for vals in matches.values() if vals])

    # get the length of matches chars
    mlen = sum([len(val2[0]) for vals in matches.values() for val1 in vals
                for val2 in val1])
    # calculate % of matched terms against complete text
    mratio = round(mlen / len(text), 2)
    model_queue.put({'Tokens matched': mcnt, 'Matched length': mlen,
                     'Matched length ratio': mratio})


if __name__ == '__main__':
    pass
