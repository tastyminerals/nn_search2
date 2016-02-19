#!/usr/bin/env python2
# -*- coding: utf-8 -*-
import re


sent = {0: [(u'The', u'DT', 0), (u'Text', u'NNP', 1), (u'widget', u'NN', 2),
            (u'The', u'DT', 3), (u'Text', u'NNP', 4), (u'widget', u'NN', 5),
            (u'provides', u'VBZ', 6), (u'formatted', u'VBN', 7), (u'text', u'IN', 8),
            (u'display', u'NN', 19), (u'.', 'PUNC', 10), (u'display', u'NN', 11),
            (u'display', u'VB', 12), (u'display', u'JJ', 13), (u'display', u'NN', 14),
            (u'display', u'NN', 15), (u'display', u'DT', 16), (u'display', u'NN', 17)]}

query = [(u'"DT', None, False), ('"DT', 3, False)]

# convert sent
sent1 = {0: []}
for token in sent[0]:
    token = ''.join(['"', token[0], '"', token[1]]), token[2]
    sent1[0].append(token)

total_n = 0
start = 0
last = 0
matched = []
while total_n < len(sent1[0]):
    full_query = len(query)
    qmatch = []
    for q in query:
        for token in sent1[0][start:]:
            print 'Iterating: query term:', q, 'token:', token, 'curidx:', token[1], 'total_n:', total_n
            total_n += 1
            start = total_n
            rq = re.compile(q[0]+'$')
            if re.search(rq, token[0]):
                print 'MATCH!'
            else:
                continue
            if q[1] == 0 or q[1]:
                print 'DETECTED idx, query idx', q[1], 'curidx:', token[1], 'last:', last
                if q[1] >= token[1] - last:
                    last = token[1] + 1
                    print 'MATCHED IDX!'
                    print 'full_query decrement', full_query - 1
                    full_query -= 1
                    qmatch.append(q)
                    if full_query == 0:
                        print 'ADDING qmatch'
                        matched.append(qmatch)
                        break
                    continue
                else:
                    continue
            else:
                print 'full_query decrement', full_query - 1
                last = token[1] + 1
                full_query -= 1
                qmatch.append(q)
            print 'FULL query last', full_query, full_query == 0
            if full_query == 0:
                print 'ADDING qmatch'
                matched.append(qmatch)
            break


print matched
