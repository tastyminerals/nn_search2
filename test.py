#!/usr/bin/env python2
# -*- coding: utf-8 -*-

sent = {0: [('a', 'NNS', 0), ('b', 'VB', 1), ('c', 'NN', 2),
            ('d', 'DT', 3), ('e', 'NN', 4), ('f', 'JJ', 5)]}


query = (['c', 'NN', None], [None, 'NN', 5])

matched = []
for q in query:
    print 'Iterating', q
    for node in sent[0][start:]
        print 'Checking', q, node
        if q[0] in node or q[1] in node:
            print 'q[0] or q[1] in node', True
            if q[2] and q[2] >= node[-1]:
                print 'q[2] > node[-1]', True
                matched.append(node)
                print 'Breaking'
                break

print matched



