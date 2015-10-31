# $Id: attack.py 7 2010-01-13 12:16:47Z mark $
#
#-------------------------------------------------------------------------------
#                                   attack
#-------------------------------------------------------------------------------
# Determine if a specific square is under attack.  Useful for detecting checks.
#
# Lots of opportunity for optimizations.  One obvious one is to preprocess
# a table mapping sq to a list of knight attack sqaures.  Can leave off None elements
# to make the lists smaller.  Need to run timings to verify this buys anything.  Don't
# know what kind of internal optimizations the interpreter makes.  A smart optimizer
# might be doing this already.

import square, man, board
from square import fwd,dfr,rgt,dbr,bak,dbl,lft,dfl

def scan(sq,d):
    "the first man found scanning in the given direction, or None if none found."
    if sq==None:
        return None
    elif d(sq)==None:
        return None
    elif board.theBoard[d(sq)] == 0:
        return scan(d(sq),d)
    else:
        return board.theBoard[d(sq)]

#----------------------------------------------------------------------
# attacks by black on white
#----------------------------------------------------------------------

def blackAttacks(sq):
    for d in [fwd,rgt,bak,lft]:
       if scan(sq,d) in [-man.queen,-man.rook]:
           return True
    for d in [dfr,dfl,dbr,dbl]:
       if scan(sq,d) in [-man.queen,-man.bishop]:
           return True
    return blackPawnAttacks(sq) or blackKnightAttacks(sq) or blackKingAttacks(sq)

def blackPawnAttacks(sq):
    for d in [dfr,dfl]:
       if board.manAt(d(sq)) == -man.pawn:
           return True
    return False

def blackKnightAttacks(sq):
    for s in [dfl(fwd(sq)),dfr(fwd(sq)),dfr(rgt(sq)),dbr(rgt(sq)),
              dbr(bak(sq)),dbl(bak(sq)),dbl(lft(sq)),dfl(lft(sq))]:
        if board.manAt(s) == -man.knight:
            return True
    return False

def blackKingAttacks(sq):
    for d in [fwd,dfr,rgt,dbr,bak,dbl,lft,dfl]:
        if board.manAt(d(sq)) == -man.king:
            return True
    return False

#----------------------------------------------------------------------
# attacks by white on black
#----------------------------------------------------------------------

def whiteAttacks(sq):
    for d in [fwd,rgt,bak,lft]:
       if scan(sq,d) in [man.queen,man.rook]:
           return True
    for d in [dfr,dfl,dbr,dbl]:
       if scan(sq,d) in [man.queen,man.bishop]:
           return True
    return whitePawnAttacks(sq) or whiteKnightAttacks(sq) or whiteKingAttacks(sq)

def whitePawnAttacks(sq):
    for d in [dbr,dbl]:
       if board.manAt(d(sq))==man.pawn:
           return True
    return False

def whiteKnightAttacks(sq):
    for s in [dfl(fwd(sq)),dfr(fwd(sq)),dfr(rgt(sq)),dbr(rgt(sq)),
              dbr(bak(sq)),dbl(bak(sq)),dbl(lft(sq)),dfl(lft(sq))]:
        if board.manAt(s) == man.knight:
            return True
    return False

def whiteKingAttacks(sq):
    for d in [fwd,dfr,rgt,dbr,bak,dbl,lft,dfl]:
       if board.manAt(d(sq)) == man.king:
           return True
    return False
