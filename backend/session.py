# Saved information over a session

import math

saved = dict()
saved_w = None
idcount = 1

def get_id():
    global idcount
    m = idcount
    id = []
    while True:
        n = (m-1)%26+1
        id.append(chr(64+n))
        m = math.floor((m-1)/26)
        if m <= 0:
            break
    idcount += 1
    return ''.join(id[::-1])

def save(data):
    global saved
    id = get_id()
    saved[id] = data
    return id

def save_weights(data):
    global saved_w
    saved_w = data

def load(id):
    global saved
    return saved[id]

def load_weights():
    global saved_w
    return saved_w
