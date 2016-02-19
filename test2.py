#!/usr/bin/env python2
# -*- coding: utf-8 -*-
import re


sent = {0: [(u'The', u'DT', 4), (u'Text', u'NNP', 5), (u'widget', u'NN', 6),
            (u'provides', u'VBZ', 7), (u'formatted', u'VBN', 8), (u'text', u'IN', 9),
            (u'display', u'NN', 10), (u'.', 'PUNC', 11)]}

query = [(u'"widget"NN', None, False), (u'"provides"VBZ', 0, False), ('"NN', 2, False)]

# convert sent
sent1 = {0: []}
for token in sent[0]:
    token = ''.join(['"', token[0], '"', token[1]]), token[2]
    sent1[0].append(token)

for token in sent1[0]:
    for q in query:
        rq = re.compile(q[0]+'$')
        if re.search(rq, token[0]):
            print q, token
            break
