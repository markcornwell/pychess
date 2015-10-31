# $id$
#
# alphabeta with memory 
#
#  alpha ~ a lowerbound, it only increases
# beta ~ an upperbound, it only decreases
#
# ref: www.cs.vu.nl/~aske/mtdf.html
#
# EXPERIMENTAL -- see alphabeta.py for something more stable

import sys,board,time,move,legal,static,san

depth = 3         # depth of search in half moves
timelimit = 100   # seconds?

inf = sys.maxint
TT = {  }       #  Transposition Table

def best(mvlist):
    global t0
    if board.whiteToMove():
        alpha = -inf
        for mv in mvlist:
            move.make(mv)
            t0 = time.clock()
            #score = max(score,itterative_deepening())
            #score = itterative_deepening()
            score = MDTF(0,depth+1)
            if score > alpha:
                bestmv,alpha = mv,score
            move.umake(mv)
            print score, san.pr(mv,mvlist)
        return bestmv,alpha,0,0   # the 0,0 are just dummy placeholder values
    else:
        assert board.blackToMove()
        beta = inf
        for mv in mvlist:
            move.make(mv)
            t0 = time.clock()
            #score = min(score,itterative_deepening())
            #score = itterative_deepening()
            score = MDTF(0,depth+1)
            if score < beta:
                bestmv,beta = mv,score
            move.umake(mv)
            print score, san.pr(mv,mvlist)
        return bestmv,beta,0,0  # the 0,0 are just a dummy placeholder values

def XXtimes_up():
    global t0, timelimit
    t = time.clock()
    timeused = t-t0
    print "Time left %s seconds" % (timelimit - timeused)
    if t-t0 > timelimit:
        return True
    else:
        return False

def XXitterative_deepening():
    global t0
    t0 = time.clock()
    firstguess = 0
    for d in xrange(1,depth+1):
        print "Depth %s search" % d
        firstguess = MDTF(firstguess,d)
        if times_up():
            break
    return firstguess

def MDTF(f,d):
    g,upperbound,lowerbound = f,+inf,-inf
    while True:
        if g==lowerbound:
            beta = g+1
        else:
            beta = g
        g = AlphaBetaWithMemory(beta-1,beta,d)
        if g<beta:
            upperbound = g
        else:
            lowerbound = g
        print "MDTF bounds = [ %d , %d ]" % (upperbound,lowerbound)
        if lowerbound >= upperbound:
            break
    return g

def AlphaBetaWithMemory(alpha,beta,d):
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
        for mv in legal.moves():
            if g >= beta:
                break
            move.make(mv)
            g = max(g,AlphaBetaWithMemory(a,beta,d-1))
            move.umake(mv)
            a = max(a,g)
    else:
        assert board.blackToMove()
        g,b = +inf,beta  #save original beta value
        for mv in legal.moves():
            if g <= alpha:
                break
            move.make(mv)
            g = min(g,AlphaBetaWithMemory(alpha,b,d-1))
            move.umake(mv)
    # transition table storing of bounds
    # fail low implies an upper bound
    if g<=alpha:
        if TT.has_key(board.hash):
            lower,upper = TT[board.hash]
        else:
            lower,upper = -inf,+inf
        TT[board.hash] = lower,g
    # found an accurate minimax value - will not occur if called with zero window
    if g>alpha and g<beta:
        TT[board.hash] = g,g
    # fail high result implies a lower bound
    if g>beta:
        if TT.has_key(board.hash):
            lower,upper = TT[board.hash]
        else:
            lower,upper = -inf,+inf
        TT[board.hash] = g,upper
    return g
    