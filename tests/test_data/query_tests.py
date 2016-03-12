#!/usr/bin/env python2

QUERIES = [
            [(None, 'NN', None, False)],
            [(None, 'DT', None, False), (None, 'NN', None, False)],
            [(None, 'DT', None, False), (None, 'NN', 1, False)],
            [(None, 'DT', None, False), (None, 'JJ', 1, False), (None, 'NN', 1, False)],
            [(None, 'DT', None, False), (None, 'JJ', 3, False), (None, 'PUNC', None, False)],
            [(None, 'RB', None, False), (None, 'PRP', 0, False)],
            [(None, 'RB', None, False), (None, 'VBD', 1, False)],
            [(None, 'RB', 1, False), (None, 'IN', 2, False)],
            [(None, 'DT', 5, False), (None, 'IN', 5, False), (None, 'NN', None, False)],
            [('a', 'DT', None, False), (None, 'JJ', 2, False), ('all', None, None, False)],
            [('a', 'DT', None, False), (None, 'JJ', 2, False), ('all', None, None, False), ('glass', 'NN', None, False)],
            [('a', 'DT', None, False), (None, 'JJ', 2, False), ('all', None, None, False), ('glass', 'NN', 5, False)],
            [('Suddenly', 'RB', 0, False), (None, 'VBN', None, False)],
            [('**she\\', None, None, False)],
            [('**she\\', None, None, False), (None, 'DT', None, False)],
            [('little', None, None, False), ('made', 'VBN', None, False)],
            [('all', None, None, False), ('of', None, None, False)],
            [('upon', 'IN', None, False), ('of', 'IN', None, False), ('solid', 'JJ', None, False)],
    ]

SENTS = [
         {0: [(u'Suddenly', 'RB', 0), (u'**she\\', 'PRP', 1), (u'came', 'VBD', 2),
            (u'upon', 'IN', 3), (u'a', 'DT', 4), (u'little', 'JJ', 5),
            (u'table', 'NN', 6), (u',', 'PUNC', 7), (u'all', 'DT', 8),
            (u'made', 'VBN', 9), (u'of', 'IN', 10), (u'solid', 'JJ', 11),
            (u'glass', 'NN', 12), (u'.', 'PUNC', 13)]}
    ]

GOLD = [
            [[(u'table', 'NN', 6)]], [[(u'glass', 'NN', 12)]],
            [[(u'a', 'DT', 4), (u'little', 'JJ', 5), (u'table', 'NN', 6)]], [[(u'all', 'DT', 8), (u'made', 'VBN', 9), (u'of', 'IN', 10), (u'solid', 'JJ', 11), (u'glass', 'NN', 12)]],
            [[(u'a', 'DT', 4), (u'little', 'JJ', 5), (u'table', 'NN', 6)]],
            [[(u'a', 'DT', 4), (u'little', 'JJ', 5), (u'table', 'NN', 6)]],
            [[(u'a', 'DT', 4), (u'little', 'JJ', 5), (u'table', 'NN', 6), (u',', 'PUNC', 7)]], [[(u'all', 'DT', 8), (u'made', 'VBN', 9), (u'of', 'IN', 10), (u'solid', 'JJ', 11), (u'glass', 'NN', 12), (u'.', 'PUNC', 13)]],
            [[(u'Suddenly', 'RB', 0), (u'**she\\', 'PRP', 1)]],
            [[(u'Suddenly', 'RB', 0), (u'**she\\', 'PRP', 1), (u'came', 'VBD', 2)]],
            [[(u'Suddenly', 'RB', 0), (u'**she\\', 'PRP', 1), (u'came', 'VBD', 2), (u'upon', 'IN', 3)]],
            [[(u'a', 'DT', 4), (u'little', 'JJ', 5), (u'table', 'NN', 6), (u',', 'PUNC', 7), (u'all', 'DT', 8), (u'made', 'VBN', 9), (u'of', 'IN', 10), (u'solid', 'JJ', 11), (u'glass', 'NN', 12)]],
            [[(u'a', 'DT', 4), (u'little', 'JJ', 5), (u'table', 'NN', 6), (u',', 'PUNC', 7), (u'all', 'DT', 8)]],
            [[(u'a', 'DT', 4), (u'little', 'JJ', 5), (u'table', 'NN', 6), (u',', 'PUNC', 7), (u'all', 'DT', 8), (u'made', 'VBN', 9), (u'of', 'IN', 10), (u'solid', 'JJ', 11), (u'glass', 'NN', 12)]],
            [[(u'a', 'DT', 4), (u'little', 'JJ', 5), (u'table', 'NN', 6), (u',', 'PUNC', 7), (u'all', 'DT', 8), (u'made', 'VBN', 9), (u'of', 'IN', 10), (u'solid', 'JJ', 11), (u'glass', 'NN', 12)]],
            [[(u'Suddenly', 'RB', 0), (u'**she\\', 'PRP', 1), (u'came', 'VBD', 2), (u'upon', 'IN', 3), (u'a', 'DT', 4), (u'little', 'JJ', 5), (u'table', 'NN', 6), (u',', 'PUNC', 7), (u'all', 'DT', 8), (u'made', 'VBN', 9)]],
            [[(u'**she\\', 'PRP', 1)]],
            [[(u'**she\\', 'PRP', 1), (u'came', 'VBD', 2), (u'upon', 'IN', 3), (u'a', 'DT', 4)]],
            [[(u'little', 'JJ', 5), (u'table', 'NN', 6), (u',', 'PUNC', 7), (u'all', 'DT', 8), (u'made', 'VBN', 9)]],
            [[(u'all', 'DT', 8), (u'made', 'VBN', 9), (u'of', 'IN', 10)]],
            [[(u'upon', 'IN', 3), (u'a', 'DT', 4), (u'little', 'JJ', 5), (u'table', 'NN', 6), (u',', 'PUNC', 7), (u'all', 'DT', 8), (u'made', 'VBN', 9), (u'of', 'IN', 10), (u'solid', 'JJ', 11)]]
    ]
