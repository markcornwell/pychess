# $Id: alphabetawithmemory.py 7 2010-01-13 12:16:47Z mark $
#
# alphabeta with memory
#
#  alpha ~ a lowerbound, it only increases
# beta ~ an upperbound, it only decreases
#
# ref: www.cs.vu.nl/~aske/mtdf.html
#

import sys,board,static

inf = sys.maxint
TT = {  }
    
def AlphaBetaWithMemory(mvlist,alpha,beta,d)
    if TT.has_key(board.hash):
        lowerbound,upperbound = TT[board.hash]
        if lowerbound >= beta:
            return lowerbound
        if upperbound <= alpha:
            return upperbound
        alpha = max(alpha,lowerbound)
        beta = min(beta,upperbound) 
    if d==0:
        g = static.eval()
    elif board.whiteToMove():
        g,a = -inf,alpha  # save original alpha value
        for mv in mvlist:
            if g >= beta:
                break
            move.make(mv)
            g = max(g,AlphaBetaWithMemory(legal.moves(),a,beta,d-1))
            move.umake(mv)
            a = max(a,g)
    else:
        assert board.blackToMove()
        g,b = +inf,beta  #save original beta value
        for mv in mvlist:
            if g <= alpha:
                break
            move.make(mv)
            g = min(g,AlphaBetaWithMemory(legal.moves(),alpha,b,d-1))
            move.umake(mv)
    # transition table storing of bounds
    # fail low implies an upper bound
    if g<=alpha:
        if TT.has_key(board.hash):
            lower,upper = TT[board.hash]
        TT[board.hash] = lower,g
    # found an accurate minimax value - will not occur if called with zero window
    if g>alpha and g<beta:
        TT[board.hash] = g,g
    # fail high result implies a lower bound
    if g>beta:
        if TT.has_key(board.hash):
            lower,upper = TT[board.hash]
        TT[board.hash] = g,upper
    return g
            
