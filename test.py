#!/usr/bin/env python2
# -*- coding: utf-8 -*-
sent = {0: [('a', 'NNS', 0), ('b', 'VB', 1), ('c', 'NN', 2),
            ('d', 'DT', 3), ('e', 'NN', 4), ('f', 'JJ', 5)]}

query = (['a', 'NNS', None], [None, 'NN', 3])

def single_match(query, sent):
    prev = 0
    matched = []
    for q in query:
        words_before = 0
        print 'Iterating', q
        for node in sent[0][prev:]:
            words_before += 1
            if q[2] and q[2] + 1 < words_before:
                break
            print 'Checking', q, '==', node
            if q[0]:
                print 'Matching', q[0], node
                if q[0] in node:
                    print 'MATCHED!'
                else:
                    print 'NOT MATCHED!'
                    continue

            if q[1]:
                print 'Matching', q[1], node
                if q[1] in node:
                    print 'MATCHED!'
                else:
                    print 'NOT MATCHED!'
                    continue

            if isinstance(q[2], int):
                print 'Matching', q[2] + node[-1], node[-1]
                if q[2] + node[-1] > node[-1]:
                    print 'MATCHED!'
                    matched.append(node)
                    prev = node[-1] + 1
                    break
                else:
                    print 'NOT MATCHED!'
                    continue

            matched.append(node)
            prev = node[-1] + 1
            break
    print matched
    print words_before

single_match(query, sent)

