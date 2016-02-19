#!/usr/bin/env python2
# -*- coding: utf-8 -*-
sent = {0: [('a', 'NNS', 0), ('b', 'VB', 1), ('c', 'NN', 2),
            ('d', 'DDT', 3), ('e', 'NN', 4), ('f', 'JJ', 5),
            ('a', 'NNS', 6), ('b', 'VB', 7), ('c', 'NN', 8),
            ('d', 'DT', 9), ('e', 'NN', 10), ('f', 'JJ', 11)]}

query = (['a', 'NNS', None, False], [None, 'DT', 2, False], ['f', None, 1, False])
query2 = (['a', 'NNS', None, False], [None, 'DT', 2, True], ['f', None, 1, False])

def single_match(query, sent):
    prev = 0
    matched = []
    while prev < len(sent):
        negation = False
        limit = False
        for q in query:
            if negation or limit:  # we detected ! node, stop checking next q
                break
            words_before = 0
            print 'Iterating', q
            for node in sent[prev:]:
                words_before += 1
                if q[2] and q[2] + 1 < words_before:
                    break
                print 'Checking', q, '==', node
                if q[0]:
                    print 'Matching WORD', q[0], node
                    if q[0] in node and not q[-1]:
                        print 'MATCHED!'
                    elif q[0] in node and q[-1]:
                        print 'NEGATION'
                    else:
                        print 'WORD NOT MATCHED!'
                        prev = node[2] + 1
                        # check if idx is max to the node pos, break
                        if q[2] and matched[-1][-1] + 1 + q[2] - node[2] <= 0:
                            print 'NO POINT! BREAKING', matched[-1][-1] + 1 + q[2] - node[2], node[2]
                            limit = True
                            break
                        continue

                if q[1]:
                    print 'Matching TAG', q[1], node
                    if q[1] in node and not q[-1]:
                        print 'MATCHED!'
                    elif q[1] in node and q[-1]:
                        print 'NEGATION'
                    else:
                        print 'TAG NOT MATCHED!'
                        if q[2] and matched[-1][-1] + 1 + q[2] - node[2] <= 0:
                            print 'NO POINT! BREAKING', matched[-1][-1] + 1 + q[2] - node[2], node[2]
                            limit = True
                            break
                        prev = node[2] + 1
                        continue

                if isinstance(q[2], int):
                    print 'Matching IDX', q[2] + node[2], node[2]
                    if q[2] + node[2] > node[2] and not q[-1]:
                        print 'MATCHED!'
                        matched.append(node)
                        print 'APPENDING MATCHED', matched
                        prev = node[2] + 1
                        break

                # check for ! node first
                if not q[-1]:
                    matched.append(node)
                    print 'APPENDING MATCHED', matched
                    prev = node[2] + 1
                    break
                elif q[-1]:
                    print 'RESET matched[]'
                    matched = []
                    prev = node[2] + 1
                    negation = True  # start query from beginning
                    break


        print '======', matched
        print prev, len(sent)

single_match(query, sent[0])
