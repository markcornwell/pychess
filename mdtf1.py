# $Id: mdtf1.py 7 2010-01-13 12:16:47Z mark $
#
# alphabeta with memory
#
#  alpha ~ a lowerbound, it only increases
# beta ~ an upperbound, it only decreases
#
# ref: www.cs.vu.nl/~aske/mtdf.html
#
#  EXPERIMENTAL 

import sys,board,time,move

depth = 3
timelimit = 60

inf = sys.maxint
TT = {  }

def best():
    if whiteToMove():
        return TBD
    else:
        return TBD

def times_up(t0):
    t = time.clock()
    if t-t0 > timelimit:
        return true

def itterative_deepening():
    t0 = time.clock()
    firstguess = 0
    for d from 1 to depth:
        firstguess,line = MDTF(firstguess,d)
        if times_up(t0):
            break()
    return firstguess,line
  
def MDTF(f,d):
    g,upperbound,lowerbound = f,+inf,-inf
    while True:
        if g==lowerbound:
            beta = g+1
        else:
            beta = g
        g,line = AlphaBetaWithMemory(root,beta-1,beta,d,[])
        if g<beta:
            upperbound = g
        else:
            lowerbound = g
        if lowerbound >= upperbound:
            break
    return g,line

def AlphaBetaWithMemory(alpha,beta,d,line)
    if TT.has_key(board.hash):
        lowerbound,upperbound,cont = TT[board.hash]
        if lowerbound >= beta:
            return lowerbound,line+cont
        if upperbound <= alpha:
            return upperbound,line+cont
        alpha = max(alpha,lowerbound)
        beta = min(beta,upperbound) 
    if d==0:
        g = static.eval()
    elif board.whiteToMove():
        g,a,nline = -inf,alpha,line  # save original alpha value
        for mv in legal.moves():
            if g >= beta:
                break
            move.make(mv)
            g,nline = max(g,AlphaBetaWithMemory(a,beta,d-1,line+[mv]))
            move.umake(mv)
            a = max(a,g)
    else:
        assert board.blackToMove()
        g,b,nline = +inf,beta,line  #save original beta value
        for mv in legal.moves():
            if g <= alpha:
                break
            move.make(mv)
            g,nline = min(g,AlphaBetaWithMemory(alpha,b,d-1,line+[mv]))
            move.umake(mv)
    # transition table storing of bounds
    # fail low implies an upper bound
    if g<=alpha:
        if TT.has_key(board.hash):
            lower,upper,oline = TT[board.hash][0]
        TT[board.hash] = lower,g,nline
    # found an accurate minimax value - will not occur if called with zero window
    if g>alpha and g<beta:
        TT[board.hash] = g,g,nline
    # fail high result implies a lower bound
    if g>beta:
        if TT.has_key(board.hash):
            lower,upper,oline = TT[board.hash]
        TT[board.hash] = g,upper,nline
    return g,nline
    