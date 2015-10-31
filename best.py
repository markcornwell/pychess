# $Id: best.py 7 2010-01-13 12:16:47Z mark $
#
# Best
#
# Very simple best move picker based only on static evaluation
# Plan is to have a family of best move pickers.  This is preliminiary
# to doing a tree search version.
#

import move, static, random

def forWhite(mvs):
    "random move best for white paired with static score"
    assert len(mvs)>0
    max_score = -99999
    for mv in mvs:
        move.make(mv)
        score = static.eval()
        if score > max_score:
            best,max_score = [mv],score
        elif score == max_score:
            best.append(mv)
        move.umake(mv)
    return (random.choice(best),score)

def forBlack(mvs):
    "random move best for black paired with static score"
    assert len(mvs)>0
    min_score = 99999
    for mv in mvs:
        move.make(mv)
        score = static.eval()
        if score < min_score:
            best,min_score = [mv],score
        elif score == min_score:
            best.append(mv)
        move.umake(mv)
    return (random.choice(best),score)

