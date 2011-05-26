#!/usr/bin/python

import pickle
import random

def shuffle(name):
    with open(name, 'rb') as f:
        tweets = pickle.load(f)

    random.shuffle(tweets)

    with open(name, 'wb') as f:
        pickle.dump(tweets, f)

def add(name, fn):
    run = True

    with open(name, 'rb') as f:
        tweets = pickle.load(f)

    with open(fn, 'r') as f:
        for line in f:
            if len(line) < 130:
                tweets.append(line.strip())

    with open(name, 'wb') as f:
        pickle.dump(tweets, f)

def test(name):
    run = True
    i = 0
    oops = []

    while run:
        line = raw_input()

        if line == '.':
            run = False

        else:
            if len(line) > 130:
                oops.append(i)

        i += 1

    print oops


