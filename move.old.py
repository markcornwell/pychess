# $Id: move.old.py 7 2010-01-13 12:16:47Z mark $
#
#--------------------------------------------------------------------------
#                                   move
#--------------------------------------------------------------------------
# A move is represented as a tuple of several forms:
#
#  (h,"-",osq,nsq)            non-capture move,  e.g. e4, Nf7, Bg7
#  (h,"x",osq,nsq,mn)         capture of mn on nsq, exf4, Nxe3, Bxh8
#  (h,"OO",osq)               castles kingside, O-O
#  (h,"OOO",osq)              castles queenside, O-O-O
#  (h,"-/",osq,nsq,mn)       promotion, e.g.  e8(Q), a1(N)
#  (h,"x/",osq,nsq,cmn,pmn)  capture & promote, e.g. exd8(Q)
#  (h,"xep",osq,nsq)            pawn captures en-passant
#
# where
#   h    number of half moves, starting a 0.  Odd moves are white.
#   osq  old square or vacated square
#   nsq  new square or square piece moved to
#   man  captured or promoted to.  Color encoded as +/- values
#
# We intend that moves run easily forward and backward.  That is why
# We keep such info as the piece captured as part of the move.
#
# This section is concerned with semantics of processing legal moves.
# Generating legal moves will be dealt with separately.
#--------------------------------------------------------------------------

import man, board
from square import *

# some functions to access parts of the move tuple

#tag=("-","x","OO","OOO","-/","x/","xep")

# the half move count (hmc) implies the move number (num)
def hmc(mv):    return mv[0]
def num(mv):    return (mv[0]/2)+1

# the half move count implies which side is to move
def color(mv):
    if mv[0]%2==0:
       return 'white'
    else:
       return 'black'

# readable ways to inspect the move tuples
def tag(mv):        return mv[1]  #kind of move       
def osq(mv):        return mv[2]  # old square
def nsq(mv):        return mv[3]  # new square
def mn(mv):         return mv[4]  # man

def isOO(mv):       return mv[1]=="OO"
def isOOO(mv):      return mv[1]=="OOO"

# Making a move, divide and conquer with case analysis

def make(mv):
    ty = tag(mv)
    if ty == "-":
       mkdash(mv)
    elif ty == "x":
       mkcapture(mv)
    elif ty == "OO":
       mkOO(mv)
    elif ty == "OOO":
       mkOOO(mv)
    elif ty == "-/":
       mkdashpromote(mv)
    elif ty == "x/":
       mkcapturepromote(mv)
    elif ty == "xep":
       mkxep(mv)
    else:
       print "makemv: bad move type: %s" % mv[1]
    board.pushFlags()

# Ummaking or undoing the move

def umake(mv):
    ty = tag(mv)
    if ty == "-":
       umkdash(mv)
    elif ty == "x":
       umkcapture(mv)
    elif ty == "-/":
       umkdashpromote(mv)
    elif ty == "x/":
       umkcapturepromote(mv)
    elif ty == "xep":
       umkxep(mv)
    elif ty == "OO":
       umkOO(mv)
    elif ty == "OOO":
       umkOOO(mv)
    else:
       print "makemv: bad move type: %s" % mv[1]
    board.popFlags()

# make the move keeping all the data structures in repair

def mkdash(mv):
    assert tag(mv) in ["-","x"]
    assert man.isMan(board.theBoard[osq(mv)])
    board.theBoard[nsq(mv)] = board.theBoard[osq(mv)]
    board.theBoard[osq(mv)] = 0
    if color(mv)=='white':
       board.whiteMen.remove(osq(mv))
       board.whiteMen.add(nsq(mv))
       if man.isKing(board.theBoard[nsq(mv)]):
           board.whiteKingAt = nsq(mv)
    else:
       board.blackMen.remove(osq(mv))
       board.blackMen.add(nsq(mv))
       if man.isKing(board.theBoard[nsq(mv)]):
           board.blackKingAt = nsq(mv)
    board.history[hmc(mv)] = mv

#-----------------------------------------------------------------
# Note how this is identical to the above except that nsq and osq 
# are transposed throughout.  Example of program inversion.
#-----------------------------------------------------------------

def umkdash(mv):
    assert tag(mv) in ["-","x"]
    assert man.isMan(board.theBoard[nsq(mv)])
    board.theBoard[osq(mv)] = board.theBoard[nsq(mv)]
    board.theBoard[nsq(mv)] = 0
    if color(mv)=='white':
       board.whiteMen.remove(nsq(mv))
       board.whiteMen.add(osq(mv))
       if man.isKing(board.theBoard[osq(mv)]):
           board.whiteKingAt = osq(mv)
    else:
       board.blackMen.remove(nsq(mv))
       board.blackMen.add(osq(mv))
       if man.isKing(board.theBoard[nsq(mv)]):
           board.blackKingAt = nsq(mv)
    del board.history[hmc(mv)]

#----------------------------------------------------------------------------
# Captures are just like dash moves, but with a bit extra bookeeping added to
# account for removing/adding the captured piece.
#----------------------------------------------------------------------------

def mkcapture(mv):
    assert tag(mv)=="x"
    mkdash(mv)
    if color(mv)=='white':
       board.blackMen.remove(nsq(mv))
    else:
       board.whiteMen.remove(nsq(mv))

def umkcapture(mv):
    assert tag(mv)=="x"
    umkdash(mv)
    board.theBoard[nsq(mv)] = mn(mv)
    if color(mv)=='white':
       board.blackMen.add(nsq(mv))
    else:
       board.whiteMen.add(nsq(mv))

#------------------------------------------------------------------
# castle kingside.  Note the symmetry between mkOO and umkOO
#------------------------------------------------------------------
# TBD:  this can be cleaned up a lot if we just use sqsymb.py

def mkOO(mv):
    assert tag(mv)=="OO"
    if color(mv)=='white':
       assert osq(mv)==square.rd('e1')
       board.theBoard[osq(mv)] = 0
       board.theBoard[rgt(osq(mv))] = man.rook
       board.theBoard[rgt(rgt(osq(mv)))] = man.king
       board.theBoard[rgt(rgt(rgt(osq(mv))))] = 0
       board.whiteMen.remove(osq(mv))
       board.whiteMen.add(rgt(osq(mv)))
       board.whiteMen.add(rgt(rgt(osq(mv))))
       board.whiteMen.remove(rgt(rgt(rgt(osq(mv)))))
       board.whiteKingAt = rgt(rgt(osq(mv)))
       board.whiteAllowOO = False
       board.whiteAllowOOO = False
    else:
       board.theBoard[osq(mv)] = 0
       board.theBoard[rgt(osq(mv))] = -man.rook
       board.theBoard[rgt(rgt(osq(mv)))] = -man.king
       board.theBoard[rgt(rgt(rgt(osq(mv))))] = 0
       board.blackMen.remove(osq(mv))
       board.blackMen.add(rgt(osq(mv)))
       board.blackMen.add(rgt(rgt(osq(mv))))
       board.blackMen.remove(rgt(rgt(rgt(osq(mv)))))
       board.blackKingAt = rgt(rgt(osq(mv)))
       board.blackAllowOO = False
       board.blackAllowOOO = False
    board.history[hmc(mv)] = mv

def umkOO(mv):
    assert tag(mv)=="OO"
    if color(mv)=='white':
       board.theBoard[osq(mv)] = man.king
       board.theBoard[rgt(osq(mv))] = 0
       board.theBoard[rgt(rgt(osq(mv)))] = 0
       board.theBoard[rgt(rgt(rgt(osq(mv))))] = man.rook
       board.whiteMen.add(osq(mv))
       board.whiteMen.remove(rgt(osq(mv)))
       board.whiteMen.remove(rgt(rgt(osq(mv))))
       board.whiteMen.add(rgt(rgt(rgt(osq(mv)))))
       board.whiteKingAt = osq(mv)
       board.whiteAllowOO = True
       board.whiteAllowOOO = True
    else:
       board.theBoard[osq(mv)] = -man.king
       board.theBoard[rgt(osq(mv))] = 0
       board.theBoard[rgt(rgt(osq(mv)))] = 0
       board.theBoard[rgt(rgt(rgt(osq(mv))))] = -man.rook
       board.blackMen.add(osq(mv))
       board.blackMen.remove(rgt(osq(mv)))
       board.blackMen.remove(rgt(rgt(osq(mv))))
       board.blackMen.add(rgt(rgt(rgt(osq(mv)))))
       board.blackKingAt = osq(mv)
       board.blackAllowOO = True
       board.blackAllowOOO = True
    del board.history[hmc(mv)]

#------------------------------------------------------------------
# castle queenside.  Note the symmetry between mkOOO and umkOOO
#------------------------------------------------------------------

def mkOOO(mv):
    if color(mv)=='white':
       board.theBoard[osq(mv)] = 0
       board.theBoard[lft(osq(mv))] = man.rook
       board.theBoard[lft(lft(osq(mv)))] = man.king
       board.theBoard[lft(lft(lft(lft(osq(mv)))))] = 0
       board.whiteMen.remove(osq(mv))
       board.whiteMen.add(lft(osq(mv)))
       board.whiteMen.add(lft(lft(osq(mv))))
       board.whiteMen.remove(lft(lft(lft(lft(osq(mv))))))
       board.whiteKingAt = lft(lft(osq(mv)))
       board.whiteAllowOO = False
       board.whiteAllowOOO = False
    else:
       board.theBoard[osq(mv)] = 0
       board.theBoard[lft(osq(mv))] = -man.rook
       board.theBoard[lft(lft(osq(mv)))] = -man.king
       board.theBoard[lft(lft(lft(lft(osq(mv)))))] = 0
       board.blackMen.remove(osq(mv))
       board.blackMen.add(lft(osq(mv)))
       board.blackMen.add(lft(lft(osq(mv))))
       board.blackMen.remove(lft(lft(lft(lft(osq(mv))))))
       board.blackKingAt = lft(lft(osq(mv)))
       board.blackAllowOO = False
       board.blackAllowOOO = False
    board.history[hmc(mv)] = mv

def umkOOO(mv):
    if color(mv)=='white':
       board.theBoard[osq(mv)] = man.king
       board.theBoard[lft(osq(mv))] = 0
       board.theBoard[lft(lft(osq(mv)))] =  0
       board.theBoard[lft(lft(lft(lft(osq(mv)))))] = man.rook
       board.whiteMen.add(osq(mv))
       board.whiteMen.remove(lft(osq(mv)))
       board.whiteMen.remove(lft(lft(osq(mv))))
       board.whiteMen.add(lft(lft(lft(lft(osq(mv))))))
       board.whiteKingAt = osq(mv)
       board.whiteAllowOO = True
       board.whiteAllowOOO = True
    else:
       board.theBoard[osq(mv)] = -man.rook
       board.theBoard[lft(osq(mv))] = 0
       board.theBoard[lft(lft(osq(mv)))] = 0
       board.theBoard[lft(lft(lft(lft(osq(mv)))))] = -man.king
       board.blackMen.add(osq(mv))
       board.blackMen.remove(lft(osq(mv)))
       board.blackMen.remove(lft(lft(osq(mv))))
       board.blackMen.add(lft(lft(lft(lft(osq(mv))))))
       board.blackKingAt = osq(mv)
       board.blackAllowOO = True
       board.blackAllowOOO = True
    del board.history[hmc(mv)]

#------------------------------------------------------------------
# pawn promotion without capture
#------------------------------------------------------------------
# bug: inconsistent representation
#  (h,"-/",osq,nsq,mn)       promotion, e.g.  e8(Q), a1(N)
#  (h,"x/",osq,nsq,cmn,pmn)  capture & promote, e.g. exd8(Q)

def mkdashpromote(mv):
    assert tag(mv) in ["-/","x/"]
    board.theBoard[osq(mv)] = 0
    board.theBoard[nsq(mv)] = mn(mv)  # inconsistent
    if color(mv)=='white':
       board.whiteMen.remove(osq(mv))
       board.whiteMen.add(nsq(mv))
    else:
       board.blackMen.remove(osq(mv))
       board.blackMen.add(nsq(mv))
    board.history[hmc(mv)] = mv

def umkdashpromote(mv):
    assert tag(mv) in ["-/","x/"]
    board.theBoard[nsq(mv)] = 0
    if color(mv)=='white':
       board.theBoard[osq(mv)] = man.pawn
       board.whiteMen.remove(osq(mv))
       board.whiteMen.add(nsq(mv))
    else:
       board.theBoard[osq(mv)] = -man.pawn
       board.blackMen.remove(osq(mv))
       board.blackMen.add(nsq(mv))
    del board.history[hmc(mv)]

#------------------------------------------------------------------
# pawn promotion with capture
#------------------------------------------------------------------
# bug: inconsistent representation

def mkcapturepromote(mv):
    mkdashpromote(mv)
    if color(mv)=='white':
        board.blackMen.remove(nsq(mv))
    else:
        board.whiteMen.remove(nsq(mv))

def umkcapturepromote(mv):
    umkdashpromote(mv)
    board.theBoard[nsq(mv)]=mnc
    if color(move)=='white':
        board.blackMen.add(nsq(mv))
    else:
        board.whiteMen.add(nsq(mv))

#------------------------------------------------------------------
# pawn captures en passant
#------------------------------------------------------------------

def mkxep(mv):
    assert tag(mv)=="xep"
    assert board.manAt(nsq(mv))==0   
    if color(mv)=='white':
       assert board.manAt(osq(mv)) == man.pawn
       assert board.manAt(bak(nsq(mv))) == -man.pawn      
       board.theBoard[osq(mv)]=0
       board.theBoard[nsq(mv)]=man.pawn
       board.theBoard[bak(nsq(mv))]=0
       board.whiteMen.remove(osq(mv))
       board.whiteMen.add(nsq(mv))
       board.blackMen.remove(bak(nsq(mv)))      
    else:
       assert board.manAt(osq(mv)) == -man.pawn
       assert board.manAt(fwd(nsq(mv))) == man.pawn       
       board.theBoard[osq(mv)]=0
       board.theBoard[nsq(mv)]= -man.pawn
       board.theBoard[fwd(nsq(mv))]=0
       board.blackMen.remove(osq(mv))
       board.blackMen.add(nsq(mv))
       print "mv=",mv
       board.whiteMen.remove(fwd(nsq(mv)))
    board.history[hmc(mv)] = mv

def umkxep(mv):
    assert tag(mv)=="xep"
    if color(mv)=='white':
       board.theBoard[osq(mv)] = man.pawn
       board.theBoard[nsq(mv)] = 0
       board.theBoard[bak(nsq(mv))]= -man.pawn
       board.whiteMen.add(osq(mv))
       board.whiteMen.remove(nsq(mv))
       board.blackMen.add(bak(nsq(mv)))
    else:
       board.theBoard[osq(mv)] = -man.pawn
       board.theBoard[nsq(mv)] = 0
       board.theBoard[fwd(nsq(mv))] = man.pawn
       board.blackMen.add(osq(mv))
       board.blackMen.remove(nsq(mv))
       board.whiteMen.add(fwd(nsq(mv)))
    del board.history[hmc(mv)]

#-------------------------------------------------------------------------------
# Presentation Layer Stuff for Moves  (consider this a higher layer)
#-------------------------------------------------------------------------------

import square

def pr(mv):
    if mv[1] == "-":
       return prdash(mv)
    elif mv[1] == "x":
       return prcapture(mv)
    elif mv[1] == "OO":
       return prOO(mv)
    elif mv[1] == "OOO":
       return prOOO(mv)
    elif mv[1] == "-/":
       return prdashpromote(mv)
    elif mv[1] == "x/":
       return prcapturepromote(mv)
    elif mv[1] == "xep":
       return prxep(mv)
    else:
       print "prmv: bad move type: %s" % mv[1]

def prdash(mv):
    manthatmoves = man.pr(board.theBoard[osq(mv)])
    fromsquare = square.pr(osq(mv))
    tosquare= square.pr(nsq(mv))
    return "%s%s-%s" % (manthatmoves, fromsquare, tosquare)

def prcapture(mv):
    manthatmoves = man.pr(board.theBoard[osq(mv)])
    fromsquare = square.pr(osq(mv))
    tosquare = square.pr(nsq(mv))
    return "%s%sx%s" % (manthatmoves, fromsquare, tosquare)

def prOO(mv):
    return "O-O"

def prOOO(mv):
    return "O-O-O"

def prdashpromote(mv):
    return "%s(%s)" % ( prdash(mv), man.pr(board.theBoard[mn(mv)]) )

def prcapturepromote(mv):
    return "%s(%s)" % ( prcapture(mv), man.pr(board.theBoard[mn(mv)]) )

def prxep(mv):
    return "%s(ep)" % prcapture(mv)
