import random


def roll():
    roll = random.randint(1, 20)
    if roll == 1:
        return 0.05
    if roll > 1 and roll <= 6:
        return 0.13
    if roll > 6 and roll <= 8:
        return 0.20
    if roll > 8 and roll <= 10:
        return 0.30
    if roll > 10 and roll <= 13:
        return 0.35
    if roll > 13 and roll <= 16:
        return 0.5
    if roll > 16 and roll <= 17:
        return 0.755
    if roll > 17 and roll <= 19:
        return 0.9
    if roll == 20:
        return 0.95


def chunks(l, n):
    """Yield successive n-sized chunks from l."""
    for i in range(0, len(l), n):
        yield l[i : i + n]
