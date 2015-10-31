# $Id: static.py 7 2010-01-13 12:16:47Z mark $
#
#------------------------------------------------------------------------------
# Static evaluation of positions.  For now we have just two factors
#  Material and kingsafety.  Lots of possibilities, but the tradeoff
# is time for depth of search.  Experiment will determine how much
# more to include here.
#
# By convention:
#   positive is better for white, negative is better for black
#
# Ideas
#  - Need to include mate and stalemate (high priority)
#  - Need to include draw by repetition
# - Should know what phase of the game it is in 
#        opening->development
#        middlegame->make a plan and follow it
#        ending -> queen a pawn
#  - Look into a bitmap representation of movement
#------------------------------------------------------------------------------

import man, board, move, legal, trial
import time, sys, random
from man import pawn
from board import manAt
from square import *
from attack import whiteAttacks,blackAttacks

inf = sys.maxint - 20

value = {  man.king    :  10000, 
           man.queen   :  900, 
           man.rook    :  500,
           man.bishop  :  325,
           man.knight  :  300,
           man.pawn    :  100,
          -man.king    : -10000, 
          -man.queen   : -900, 
          -man.rook    : -500,
          -man.bishop  : -310,
          -man.knight  : -300,
          -man.pawn    : -100 }

kingSafeWt = 10   # value deducted for each empty attacked sq around king

def wmaterial():
    material = 0
    for sq in board.whiteMen:
        material = material + value[manAt(sq)]
    #print "35: material=",count
    return material

def bmaterial():
    material = 0
    for sq in board.blackMen:
        material = material + value[manAt(sq)]
    #print "35: material=",count
    return material    
    
def wkingsafety():
    safety = 0
    k = board.whiteKingAt
    for sq in [fwd(k),dfr(k),rgt(k),dbr(k),
               bak(k),dbl(k),lft(k),dfl(k)]:
        if blackAttacks(sq):
            safety = safety - kingSafeWt
    return safety
            
def bkingsafety():
    safety = 0
    k = board.blackKingAt
    for sq in [fwd(k),dfr(k),rgt(k),dbr(k),
               bak(k),dbl(k),lft(k),dfl(k)]:
        if whiteAttacks(sq):
            safety = safety + kingSafeWt
    return safety

def wcenter():
    center = 0
    for sq in [c4,d4,e4]:
        if manAt(sq)==pawn:
            center = center+10
    return center

def bcenter():
    center = 0
    for sq in [c5,d5,e5]:
        if manAt(sq)==-pawn:
            center = center-10
    return center
    
def wpenalty():
    penalty = 0
    for sq in board.whiteMen:
        # penalty for knight and bishop on original rank
        if firstrank(sq):
            if manAt(sq)==man.knight:
                penalty = penalty - 66
                # get that kings knight out
                if sq==g1:
                    penalty = penalty - 50
            elif manAt(sq)==man.bishop:
                penalty = penalty-61
                # get that kings bishop out
                if sq==f1:
                    penalty = penalty - 50
        # penalty for center pawn on original squares
        if sq in [e2,d2,c2]:
            if manAt(sq)==man.pawn:
                penalty = penalty-96
        # a knight on the rim is dim
        if afile(sq) or hfile(sq):
            if manAt(sq)==man.knight:
                penalty = penalty-89
        # penalty for king in center
        if manAt(sq)==man.king:
			if centerfile(sq):
				penalty = penalty - 77
			if not firstrank(sq):
				penalty = penalty - 100
    return penalty
    
def bpenalty():
    penalty = 0
    for sq in board.blackMen:
        # penalty for knight and bishop on original rank    
        if lastrank(sq):
            if manAt(sq)==-man.knight:
                penalty = penalty + 66
                # get that kings knight out
                if sq==g8:
                    penalty = penalty + 50
            elif manAt(sq)==-man.bishop:
                penalty = penalty+61
                # get that kings bishop out
                if sq==f8:
                    penatly = penalty + 50
        # penalty for center pawn on original squares
        if sq in [e7,d7,c7]:
            if manAt(sq)==-man.pawn:
                penalty = penalty+96
        # a knight on the rim is dim
        if afile(sq) or hfile(sq):
            if manAt(sq)==-man.knight:
                penalty = penalty+89
        # penalty for king in center
        if manAt(sq)==-man.king:
            if centerfile(sq):
                penalty = penalty +77
            if not lastrank(sq):
                penalty = penalty + 100
    return penalty

def wbonus():
    # bonus for rook in center
    bonus = 0
    for sq in board.whiteMen:
        if manAt(sq)==man.rook:
            if sq in [d1,e1,f1]:
                bounus = bonus + 11
        #bonus king at castled sq
        elif manAt(sq)==man.king:
            if sq==g1:
                bonus = bonus + 12
    return bonus                
    
def bbonus():
    bonus = 0
    for sq in board.blackMen:
        #bonus for rook in center    
        if manAt(sq)==-man.rook:
            if sq in [d8,e8,f8]:
                bounus = bonus - 11
        # bonus king at castled sq
        elif manAt(sq)==-man.king:
            if sq==g8:
                bonus = bonus - 12
    return bonus

# we estimate mobility from the number of trial moves
# for the side that des not have he move, we employ the
# trick of a null move.  The null move does not change
# the position of any pieces but does change whose turn
# it is to move.

# Need to watch out for king captures.  This becomes
# possible with null moves and asserts balk when they
# see it.
   
def wmobility(mvs):
    if board.colorToMove()=='white':
        return len(mvs)
    else:
        move.make((len(board.history),'null'))
        cnt = len(trial.trialmoves())
        move.umake(board.lastMove())
        return cnt

def bmobility(mvs):
    if board.colorToMove()=='black':
        return len(mvs)
    else:
        move.make((len(board.history),'null'))
        cnt = len(trial.trialmoves())
        move.umake(board.lastMove())
        return -cnt    

#---------------------------------------------------------------------------------------------
# the evaluation function - since our search depth is pretty lame, I flaunted
# current wisdom by putting a good deal into the static evaluation.
#---------------------------------------------------------------------------------------------

def eval():
    mvs = legal.moves()
    s = legal.state(mvs)
    assert s in ['whiteMates','blackMates','stalemate','continue']
    if s=='whiteMates':
        return +inf   # black has been mated
    elif s=='blackMates':
        return -inf   # white has been mated
    elif s=='stalemate':
        return 0
    else:
        assert s=='continue'
        ma = wmaterial() + bmaterial()
        c = wcenter()   + bcenter()
        p = wpenalty()  + bpenalty()
        b = wbonus()    + bbonus()
        mo = wmobility(mvs) + bmobility(mvs)
        k = wkingsafety() + bkingsafety()
        #print "58: k=%s m=%s eval=%s" % (k,m,k+m)
        tot = 3*ma + c + p + b  + mo
        #tot = ma
        return tot + 0.1*random.randint(0,9)
