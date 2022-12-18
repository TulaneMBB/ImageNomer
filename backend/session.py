# Saved information over a session

import math

saved = dict()
idcount = 1

def save(id, data):
    global saved
    saved[id] = data

def load(id):
    global saved
    return saved[id]

def get_id():
    global idcount
    m = idcount
    id = []
    while True:
        n = (m-1)%5+1
        id.append(chr(64+n))
        m = math.floor((m-1)/5)
        if m <= 0:
            break
    idcount += 1
    return ''.join(id[::-1])