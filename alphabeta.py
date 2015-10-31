# $Id: alphabeta.py 7 2010-01-13 12:16:47Z mark $
#
# Alpha-beta search
#
#  Straightforward implementation of classic alphabeta serach without too many bells and whistles.
#
# References
#    [Knuth75] Knuth & Moore, An analysis of alpha-beta pruning, Artificial Intelligence 6 (1975), 293-326.
#    [Plaat-97] Aske Plaat, MTD(f) A Minimax Algorithm faster than NegaScout, www.cs.vu.nl/~aske/mtdf.html
#    [Plaat-94] Aske Plaat, et al., A New Paradigm for Minimax Search, Univeristy of Alberta Technical Report
#          TR 94-18, December 1994
#

import board, move, legal, static, sys
import time
import san
from move import make,umake,num

#------------------------------------------------------------------------------
#  Control Parameters
#------------------------------------------------------------------------------

enableTT = True  # enable transposition tables
depth1 = 2   # primary cutoff ~ full width
depth2 = -2  # secondary cutoff (negative) ~ captures only
silent = False

#wlog = open("w.log","w")
#blog = open("b.log","w")
wlog = sys.stdout
blog = sys.stdout

# this is a number to represent infinity.   It is just the biggest integer we have.
inf = sys.maxint

#------------------------------------------------------------------------------
# Transposition Table
#  Entries are of form:  (score,mv)
#  Note that color(mv) will imply where the position is white moves or black moves
#  TBD include castling flags in hash
#------------------------------------------------------------------------------

ttHits = 0  # transposition table hit count
WTT = { }   # white transposition table
BTT = { }   # black transposition table

#------------------------------------------------------------------------------
# Pretty prints the best line in SAN notation.  Don't bother to do this until after
# we have the whole line computed.
#------------------------------------------------------------------------------
def prline(mvs):
    s = ""
    c = 0
    for mv in mvs:
        legals = legal.moves()
        if move.color(mv)=='white':
            s = s + ("%s %s" % (num(mv),san.pr(mv,legals)))
        else:
            if c==0:
                s = "%s ...%s " % (num(mv),san.pr(mv,legals))
            else:
                s = s + (" %s " % san.pr(mv,legals))
        move.make(mv)
        c = c+1
    while c>0:
        move.umake(board.lastMove())
        c = c-1
    return s
    
def isCapture(mv):
    return move.tag(mv) in ["x","x/","xep"]

# used to sort the movelist.  Puts captures at the head of the list
# where they are more likely to cause cut-offs.  
def cmp(mv0,mv1):
    if isCapture(mv0) and not isCapture(mv1):
        return -1
    elif isCapture(mv0)==isCapture(mv1):
        return 0
    else:
        assert not isCapture(mv0) and isCapture(mv1)
        return 1

# run static evaluation on the moves and pick the one with the higher value
def cmp0(mv0,mv1):
    move.make(mv0)
    s0 = static.eval()
    move.umake(mv0)
    move.make(mv1)
    s1 = static.eval()
    move.umake(mv1)
    if s0<s1:
        return -1
    elif s0==s1:
        return 0
    else:
        return +1

def cmp1(mv0,mv1):
    return -cmp0(mv0,mv1)

def best(mvlist):
    assert len(mvlist)>0
    assert depth1>0
    if board.whiteToMove():
        mvlist.sort(cmp)    
        b,s,cnt,t01,ln = bestForWhite(mvlist,depth1)   
    else:
        mvlist.sort(cmp)
        b,s,cnt,t01,ln = bestForBlack(mvlist,depth1)
    return b,s,cnt,t01    
    
def bestForWhite(mvlist,d):
    # white tries to maximize
    global cnt,ttHits
    t0 = time.clock()
    cnt = 0
    assert len(mvlist)>0
    assert d>0
    alpha = -inf
    #alpha = -300
    for mv in mvlist:
        c0 = cnt
        make(mv)
        cnt = cnt+1        
        if enableTT and WTT.has_key(board.hash):
            score,ln = WTT[board.hash]
            ttHits = ttHits+1
        else:
            score,ln = G2(alpha,+inf,d-1,[mv])
            WTT[board.hash] = (score,ln) 
        umake(mv)
        if not silent:
            print >>wlog,"%6s %6s  %s" % (score,cnt-c0,prline(ln))
            wlog.flush()
        if score > alpha:
            best,alpha,bestln = mv,score,ln
    t1 = time.clock()
    return best,alpha,cnt,t1-t0,bestln

def bestForBlack(mvlist,d):
    # black tries to minimize
    global cnt,ttHits
    t0 = time.clock()
    cnt = 0
    assert len(mvlist)>0
    assert d>0
    beta = inf
    #beta = +300
    for mv in mvlist:
        c0 = cnt
        make(mv)
        cnt = cnt+1
        if enableTT and BTT.has_key(board.hash):
            score,ln = BTT[board.hash]
            ttHits = ttHits+1
        else:
            score,ln = F2(-inf,beta,d-1,[mv])
            #score,ln=G2x(inf,min_score,d-1,[mv])
            BTT[board.hash]=(score,ln)
        umake(mv)
        if not silent:
            print >>blog,"%6s %6s  %s" % (score,cnt-c0,prline(ln))   
            blog.flush()
        if score < beta:
            best,beta,bestln = mv,score,ln
    t1 = time.clock()
    return best,beta,cnt,t1-t0,bestln

def moves(d):
    mvlist = legal.moves()
    if d>0:
        # sort captures to the front of the list
        mvlist.sort(cmp)
        return mvlist
    elif d > depth2:
        #  after depth limit reach, we only look at a captures
        return filter(lambda mv: move.tag(mv) in ["x","x/","xep"], mvlist)
    else:
        return [ ]

#----------------------------------------------------------        
# Deep capture versions of F2 and G2
#----------------------------------------------------------

def F2(alpha,beta,d,ln):
    global cnt
    # determine the successor positions
    mvlist = moves(d)
    if len(mvlist)==0:
        return static.eval(),ln
    m = alpha
    mln = ln  # ?
    for mv in mvlist:
        make(mv)
        cnt = cnt+1
        mln = ln+[mv]
        t,tln = G2(m,beta,d-1,mln)
        umake(mv)
        if t>m:
            m,mln = t,tln
        if m>=beta:
            break
    return m,mln

def G2(alpha,beta,d,ln):
    global cnt
    # determine the successor positions
    mvlist = moves(d)
    if len(mvlist)==0:
        return static.eval(),ln
    m = beta
    #mln = ln #?
    for mv in mvlist:
        make(mv)
        cnt = cnt+1
        mln = ln+[mv]
        t,tln = F2(alpha,m,d-1,mln)
        umake(mv)
        if t<m:
            m,mln = t,tln
        if m<=alpha:
            break
    return m,mln
    
