'''A collection of misc. bit operations.'''

def rotater(row, steps=1):
    '''Rotate an array of integers one bit to the right.'''
    lost = 0
    mask = (0xff << steps & 0xff) ^ 0xff
    for i, b in enumerate(row[:]):
        x = b >> steps
        if lost:
            x |= (lost << (8-steps)) & 0xff
        lost = b & mask
        row[i] = x

    if lost:
        row[0] |= (lost << (8-steps))

    return row


def rotatel(row, steps=1):
    '''Rotate an array of integers one bit to the left.'''
    lost = 0
    mask = (0xff >> steps & 0xff) ^ 0xff
    for i, b in enumerate(row[:]):
        x = (b << steps) & 0xff
        if lost:
            x |= (lost >> (8-steps))
        lost = b & mask
        row[i] = x

    if lost:
        row[0] |= (lost >> (8-steps))

    return row
