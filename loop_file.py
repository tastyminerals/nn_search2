#!/usr/bin/python2.7
# -*- coding: utf-8 -*-


def run_fib(n):
    if n == 1:
        return 1
    elif n == 0:
        return 0
    else:
        return run_fib(n-1) + run_fib(n-2)

def do_looping(queue):
    answer = run_fib(35)
    print 'Finished fib'
    queue.put(answer)
