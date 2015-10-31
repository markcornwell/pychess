# $Id: move.py 7 2010-01-13 12:16:47Z mark $
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
#  (h,"-/",osq,nsq,0,pmn)       promotion, e.g.  e8(Q), a1(N)
#  (h,"x/",osq,nsq,cmn,pmn)  capture & promote, e.g. exd8(Q)
#  (h,"xep",osq,nsq)            pawn captures en-passant
#  (h,"null")                 null move (used in static evaluation)
# where
#   h    number of half moves, starting a 0.  Odd moves are white.
#   osq  old square or vacated square
#   nsq  new square or square piece moved to
#   man  captured or promoted to.  Color encoded as +/- values
#
#  Note that all fields but the second are non-negative integers
#
# We intend that moves run easily forward and backward.  That is why
# We keep such info as the piece captured as part of the move.
#
# This section is concerned with semantics of processing legal moves.
# Generating legal moves will be dealt with separately.
#--------------------------------------------------------------------------

import man, board, zobrist
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

# these fields are only used for pawn promotions 
def cmn(mv):
    "captured man ~ man that was captured on this move"
    assert tag(mv) in ["x/","x","xep","-","-/"]
    if tag(mv)=="-":
        return 0
    else:
        return mv[4] 

def pmn(mv):
    "promotion man ~ piece that the pawn promotes to on this move"
    assert tag(mv) in ["x/","-/"]
    return mv[5] 

# Making a move, divide and conquer with case analysis

def make(mv):
    assert board.valid()
    # Save flags first since move may affect flags - note inverse symmetry with umake
    # fixes an earlier bug where I did it last.  Lesson: follow the math patterns!  -(AB)=(-B)(-A)
    
    board.pushFlags()    
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
    elif ty == "null":
       mknull(mv)
    else:
       print "makemv: bad move type: %s" % mv[1]
    assert board.valid()
    
# Ummaking or undoing the move

def umake(mv):
    assert board.valid()
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
    elif ty == "null":
       umknull(mv)
    else:
       print "makemv: bad move type: %s" % mv[1]
    # pop flags last -- in keeping with reverse order of inverting functions
    board.popFlags()
    assert board.valid()
    
# make the move keeping all the data structures in repair

def mkdash(mv):    
    assert tag(mv) in ["-","x"]
    assert not tag(mv)=="-" or man.isEmpty(cmn(mv))
    assert not tag(mv)=="x" or man.isMan(cmn(mv))
    assert man.isMan(board.manAt(osq(mv)))
    assert board.valid()
    
    # maintain allow flags
    if color(mv)=='white':
        if osq(mv)==e1 and board.manAt(e1)==man.king:
            board.whiteAllowOO = False
            board.whiteAllowOOO = False
        elif osq(mv)==h1 and board.manAt(h1)==man.rook:
            board.whiteAllowOO = False
        elif osq(mv)==a1 and board.manAt(a1)==man.rook:
            board.whiteAllowOOO = False
    else:
        if osq(mv)==e8 and board.manAt(e8)==-man.king:
            board.blackAllowOO = False
            board.blackAllowOOO = False
        elif osq(mv)==h8 and board.manAt(h8)==-man.rook:
            board.blackAllowOO = False
        elif osq(mv)==a8 and board.manAt(a8)==-man.rook:
            board.blackAllowOOO = False
            
    # maintain KingAt and Men sets
    if color(mv)=='white':
       board.whiteMen.remove(osq(mv))
       board.whiteMen.add(nsq(mv))
       if board.manAt(osq(mv)) == man.king:
           board.whiteKingAt = nsq(mv)
    else:
       board.blackMen.remove(osq(mv))
       board.blackMen.add(nsq(mv))
       if board.manAt(osq(mv)) == -man.king:
           board.blackKingAt = nsq(mv)
    
    # update board
    zobrist.PlaceMan(nsq(mv),board.theBoard[osq(mv)])
    zobrist.PlaceMan(osq(mv),0)
    
    #board.theBoard[nsq(mv)] = board.theBoard[osq(mv)]
    #board.theBoard[osq(mv)] = 0
    
    # update history
    board.history[hmc(mv)] = mv
    assert not tag(mv)=="-" or board.valid()

#-----------------------------------------------------------------
# Note how this is identical to the above except that nsq and osq 
# are transposed throughout.  Example of program inversion.
#-----------------------------------------------------------------

def umkdash(mv):
    assert tag(mv) in ["-","x"]
    assert not tag(mv)=="-" or man.isEmpty(cmn(mv))
    assert not tag(mv)=="x" or man.isMan(cmn(mv))       
    assert man.isMan(board.theBoard[nsq(mv)])
    assert board.valid()
    
    # maintain KingAt and Men sets
    if color(mv)=='white':
       board.whiteMen.remove(nsq(mv))
       board.whiteMen.add(osq(mv))
       if board.theBoard[nsq(mv)] == man.king:
           board.whiteKingAt = osq(mv)
    else:
       board.blackMen.remove(nsq(mv))
       board.blackMen.add(osq(mv))
       if board.theBoard[nsq(mv)] == -man.king:
           board.blackKingAt = osq(mv)
    
    # update the board
    zobrist.PlaceMan(osq(mv),board.theBoard[nsq(mv)])    
    #board.theBoard[osq(mv)] = board.theBoard[nsq(mv)]
    assert not tag(mv)=="-" or man.isEmpty(cmn(mv))
    assert not tag(mv)=="x" or man.isMan(cmn(mv))
    zobrist.PlaceMan(nsq(mv),cmn(mv))    
    #board.theBoard[nsq(mv)] = cmn(mv)
    
    # maintain history
    del board.history[hmc(mv)]
    assert not tag(mv)=="-" or board.valid()

#----------------------------------------------------------------------------
# Captures are just like dash moves, but with a bit extra bookeeping added to
# account for removing/adding the captured piece.
#----------------------------------------------------------------------------

def mkcapture(mv):
    assert tag(mv)=="x"
    assert not color(mv)=='white' or man.isBlack(board.manAt(nsq(mv)))
    assert not color(mv)=='black' or man.isWhite(board.manAt(nsq(mv)))
    assert board.valid()
    assert not man.isKing(board.manAt(nsq(mv)))
    mkdash(mv)    
    if color(mv)=='white':
        board.blackMen.remove(nsq(mv))   # <<--------
        # capturing rooks on original squares affects castling
        if nsq(mv)==h8:
            board.blackAllowOO = False
        elif nsq(mv)==a8:
            board.blackAllowOOO = False
    else:
        board.whiteMen.remove(nsq(mv))
        # capturing rooks on original squares affects castling
        if nsq(mv)==h1:
            board.whiteAllowOO = False
        elif nsq(mv)==a1:
            board.whiteAllowOOO = False        
    assert board.valid()

def umkcapture(mv):
    assert tag(mv)=="x"
    assert man.isMan(mn(mv))
    assert not color(mv)=='white' or man.isBlack(mn(mv))
    assert not color(mv)=='black' or man.isWhite(mn(mv))
    assert board.valid()   
    umkdash(mv)    
    # board.theBoard[nsq(mv)] = cmn(mv)  # WHAT ???
    # note the theBoard will be invalid at this point
    if color(mv)=='white':
       assert man.isBlack(board.manAt(nsq(mv)))
       board.blackMen.add(nsq(mv))
    else:
       assert man.isWhite(board.manAt(nsq(mv)))
       board.whiteMen.add(nsq(mv))
    # after the above board maintennance it will be valid again
    assert board.valid()

#------------------------------------------------------------------
# castle kingside.  Note the symmetry between mkOO and umkOO
#------------------------------------------------------------------
# TBD:  this can be cleaned up a lot if we just use sqsymb.py

def mkOO(mv):
    assert tag(mv)=="OO"
    assert board.valid()
    if color(mv)=='white':
       assert osq(mv)==e1
       assert board.whiteAllowOO
       zobrist.PlaceMan(e1,0)
       #board.theBoard[e1] = 0
       zobrist.PlaceMan(f1,man.rook)
       #board.theBoard[f1] = man.rook
       zobrist.PlaceMan(g1,man.king)
       #board.theBoard[g1] = man.king
       zobrist.PlaceMan(h1,0)       
       #board.theBoard[h1] = 0
       board.whiteMen.remove(e1)
       board.whiteMen.add(f1)
       board.whiteMen.add(g1)
       board.whiteMen.remove(h1)
       board.whiteKingAt = g1
       board.whiteAllowOO = False    # not need since board.popFlags()  will fix
       board.whiteAllowOOO = False   # not need since board.popFlags()  will fix
    else:
       assert color(mv)=='black'
       assert osq(mv)==e8
       assert board.blackAllowOO
       zobrist.PlaceMan(e8,0)
       #board.theBoard[e8] = 0
       zobrist.PlaceMan(f8,-man.rook)
       #board.theBoard[f8] = -man.rook
       zobrist.PlaceMan(g8,-man.king)
       #board.theBoard[g8] = -man.king
       zobrist.PlaceMan(h8,0)
       #board.theBoard[h8] = 0
       board.blackMen.remove(e8)
       board.blackMen.add(f8)
       board.blackMen.add(g8)
       if not h8 in board.blackMen:
            print "move.271:"
            board.dump()
       board.blackMen.remove(h8)
       board.blackKingAt = g8
       board.blackAllowOO = False   # not need since board.popFlags()  will fix
       board.blackAllowOOO = False  # not need since board.popFlags()  will fix
    board.history[hmc(mv)] = mv
    assert board.valid()

def umkOO(mv):
    assert tag(mv)=="OO"
    assert board.valid()
    if color(mv)=='white':
       assert osq(mv)==e1
       assert not board.whiteAllowOO
       assert not board.whiteAllowOOO
       zobrist.PlaceMan(e1,man.king)
       #board.theBoard[e1] = man.king
       zobrist.PlaceMan(f1,0)
       #board.theBoard[f1] = 0
       zobrist.PlaceMan(g1,0)
       #board.theBoard[g1] = 0
       zobrist.PlaceMan(h1,man.rook)
       #board.theBoard[h1] = man.rook
       board.whiteMen.add(e1)
       board.whiteMen.remove(f1)
       board.whiteMen.remove(g1)
       board.whiteMen.add(h1)
       board.whiteKingAt = e1
       board.whiteAllowOO = True   # not need since board.popFlags()  will fix
    else:
       assert osq(mv)==e8
       assert not board.blackAllowOO
       assert not board.blackAllowOOO
       zobrist.PlaceMan(e8,-man.king)
       #board.theBoard[e8] = -man.king
       zobrist.PlaceMan(f8,0)
       #board.theBoard[f8] = 0
       zobrist.PlaceMan(g8,0)
       #board.theBoard[g8] = 0
       zobrist.PlaceMan(h8,-man.rook)
       #board.theBoard[h8] = -man.rook
       board.blackMen.add(e8)
       board.blackMen.remove(f8)
       board.blackMen.remove(g8)
       board.blackMen.add(h8)
       board.blackKingAt = e8
       board.blackAllowOO = True   # not need since board.popFlags()  will fix
    del board.history[hmc(mv)]
    assert board.valid()
    
#------------------------------------------------------------------
# castle queenside.  Note the symmetry between mkOOO and umkOOO
#------------------------------------------------------------------
# thinking about how this routine could be derived from the invarints
# for the board data structure -- perhaps even mechanically
# E.g.  (Ai: manAt[i] == m  =>  (i in whitemen))   justifies/motivates
# all our modifications to whiteMen

def mkOOO(mv):
    assert tag(mv)=="OOO"
    assert board.valid()
    if color(mv)=='white':
        assert osq(mv)==e1
        assert board.whiteAllowOOO 
        zobrist.PlaceMan(e1,0)
        #board.theBoard[e1] = 0
        zobrist.PlaceMan(d1,man.rook)
        #board.theBoard[d1] = man.rook
        zobrist.PlaceMan(c1,man.king)
        #board.theBoard[c1] = man.king
        zobrist.PlaceMan(a1,0)
        #board.theBoard[a1] = 0
        board.whiteMen.remove(e1)
        board.whiteMen.add(d1)
        board.whiteMen.add(c1)
        board.whiteMen.remove(a1)
        board.whiteKingAt = c1
        board.whiteAllowOO = False
        board.whiteAllowOOO = False
    else:
        assert osq(mv)==e8
        assert board.blackAllowOOO 
        zobrist.PlaceMan(e8,0)
        #board.theBoard[e8] = 0
        zobrist.PlaceMan(d8,-man.rook)
        #board.theBoard[d8] = -man.rook
        zobrist.PlaceMan(c8,-man.king)
        #board.theBoard[c8] = -man.king
        zobrist.PlaceMan(a8,0)
        #board.theBoard[a8] = 0
        board.blackMen.remove(e8)
        board.blackMen.add(d8)
        board.blackMen.add(c8)
        board.blackMen.remove(a8)
        board.blackKingAt = c8
        board.blackAllowOO = False
        board.blackAllowOOO = False
    board.history[hmc(mv)] = mv
    assert board.valid()

def umkOOO(mv):
    assert tag(mv)=="OOO"
    assert board.valid()
    if color(mv)=='white':
       assert osq(mv)==e1
       assert not board.whiteAllowOO
       assert not board.whiteAllowOOO
       zobrist.PlaceMan(e1,man.king)
       #board.theBoard[e1] = man.king
       zobrist.PlaceMan(d1,0)
       #board.theBoard[d1] = 0
       zobrist.PlaceMan(c1,0)
       #board.theBoard[c1] =  0
       zobrist.PlaceMan(a1,man.rook)
       #board.theBoard[a1] = man.rook
       board.whiteMen.add(e1)
       board.whiteMen.remove(d1)
       board.whiteMen.remove(c1)
       board.whiteMen.add(a1)
       board.whiteKingAt = e1
       board.whiteAllowOOO = True  # not need since board.popFlags()  will fix
    else:
       assert osq(mv)==e8
       assert not board.blackAllowOO
       assert not board.blackAllowOOO
       zobrist.PlaceMan(e8,-man.king)
       #board.theBoard[e8] = -man.king
       zobrist.PlaceMan(d8,0)
       #board.theBoard[d8] = 0
       zobrist.PlaceMan(c8,0)
       #board.theBoard[c8] = 0
       zobrist.PlaceMan(a8,-man.rook)
       #board.theBoard[a8] = -man.rook
       board.blackMen.add(e8)
       board.blackMen.remove(d8)
       board.blackMen.remove(c8)
       board.blackMen.add(a8)
       board.blackKingAt = e8
       board.blackAllowOOO = True  # not need since board.popFlags()  will fix
    del board.history[hmc(mv)]
    assert board.valid()
    
#------------------------------------------------------------------
# pawn promotion without capture
#------------------------------------------------------------------
# bug: inconsistent representation
#  WAS (h,"-/",osq,nsq,mn)       promotion, e.g.  e8(Q), a1(N)
#
#  (h,"-/",osq,nsq,cmn=0,pmn)       promotion, e.g.  e8(Q), a1(N)
#------------------------------------------------------------------

def mkdashpromote(mv):
    assert tag(mv) in ["-/","x/"]
    assert man.isPawn(board.manAt(osq(mv)))
    assert board.manAt(nsq(mv))==cmn(mv)
    assert not color(mv)=='white' or man.whiteQRBN(pmn(mv))
    assert not color(mv)=='black' or man.blackQRBN(pmn(mv))    
    assert not color(mv)=='white' or board.manAt(osq(mv)) == man.pawn   
    assert not color(mv)=='black' or board.manAt(osq(mv)) == -man.pawn   
    assert not tag(mv)=="-/" or cmn(mv)==0
    assert not tag(mv)=="x/" or cmn(mv)!=0
    assert board.valid()
    # update board
    zobrist.PlaceMan(osq(mv),0)
    #board.theBoard[osq(mv)] = 0
    zobrist.PlaceMan(nsq(mv),pmn(mv))
    #board.theBoard[nsq(mv)] = pmn(mv)
    # maintain Men
    if color(mv)=='white':
       board.whiteMen.remove(osq(mv))
       board.whiteMen.add(nsq(mv))
    else:
       board.blackMen.remove(osq(mv))
       board.blackMen.add(nsq(mv))
    board.history[hmc(mv)] = mv
    assert not tag(mv)=="-" or board.valid()
 
def umkdashpromote(mv):
    assert tag(mv) in ["-/","x/"]
    assert board.manAt(osq(mv))==0
    assert board.manAt(nsq(mv))==pmn(mv)
    assert not color(mv)=='white' or man.whiteQRBN(pmn(mv))
    assert not color(mv)=='black' or man.blackQRBN(pmn(mv))
    assert not tag(mv)=="-/" or cmn(mv)==0
    assert not tag(mv)=="x/" or cmn(mv)!=0  
    assert board.valid()
    zobrist.PlaceMan(nsq(mv),cmn(mv))    
    #board.theBoard[nsq(mv)] = cmn(mv)
    if color(mv)=='white':
       zobrist.PlaceMan(osq(mv),man.pawn)
       #board.theBoard[osq(mv)] = man.pawn
       board.whiteMen.remove(nsq(mv))
       board.whiteMen.add(osq(mv))
    else:
       zobrist.PlaceMan(osq(mv),-man.pawn)
       #board.theBoard[osq(mv)] = -man.pawn
       board.blackMen.remove(nsq(mv))
       board.blackMen.add(osq(mv))
    del board.history[hmc(mv)]
    assert not tag(mv)=="-" or board.valid()

#------------------------------------------------------------------
# pawn promotion with capture
#------------------------------------------------------------------
# bug: inconsistent representation
#  (h,"x/",osq,nsq,cmn,pmn)  capture & promote, e.g. exd8(Q)

def mkcapturepromote(mv):
    assert tag(mv)=="x/"
    assert board.valid()
    mkdashpromote(mv)
    if color(mv)=='white':
        board.blackMen.remove(nsq(mv))
        # capturing rooks on original squares affects castling
        if nsq(mv)==h8:
            board.blackAllowOO = False
        elif nsq(mv)==a8:
            board.blackAllowOOO = False
    else:
        board.whiteMen.remove(nsq(mv))
        # capturing rooks on original squares affects castling
        if nsq(mv)==h1:
            board.whiteAllowOO = False
        elif nsq(mv)==a1:
            board.whiteAllowOOO = False     
    assert board.valid()
    
def umkcapturepromote(mv):
    assert tag(mv)=="x/"
    assert board.valid()
    umkdashpromote(mv)
    if color(mv)=='white':
        board.blackMen.add(nsq(mv))
    else:
        board.whiteMen.add(nsq(mv))
    assert board.valid()

#------------------------------------------------------------------
# pawn captures en passant
#------------------------------------------------------------------

def mkxep(mv):
    assert tag(mv)=="xep"
    assert board.manAt(nsq(mv))==0   
    if color(mv)=='white':
       assert board.manAt(osq(mv)) == man.pawn
       assert board.manAt(bak(nsq(mv))) == -man.pawn
       zobrist.PlaceMan(osq(mv),0)
       #board.theBoard[osq(mv)]=0
       zobrist.PlaceMan(nsq(mv),man.pawn)
       #board.theBoard[nsq(mv)]=man.pawn
       zobrist.PlaceMan(bak(nsq(mv)),0)
       #board.theBoard[bak(nsq(mv))]=0
       board.whiteMen.remove(osq(mv))
       board.whiteMen.add(nsq(mv))
       board.blackMen.remove(bak(nsq(mv)))      
    else:
       assert board.manAt(osq(mv)) == -man.pawn
       assert board.manAt(fwd(nsq(mv))) == man.pawn
       zobrist.PlaceMan(osq(mv),0)
       #board.theBoard[osq(mv)]=0
       zobrist.PlaceMan(nsq(mv),-man.pawn)
       #board.theBoard[nsq(mv)]= -man.pawn
       zobrist.PlaceMan(fwd(nsq(mv)),0)
       #board.theBoard[fwd(nsq(mv))]=0
       board.blackMen.remove(osq(mv))
       board.blackMen.add(nsq(mv))
       board.whiteMen.remove(fwd(nsq(mv)))
    board.history[hmc(mv)] = mv

def umkxep(mv):
    assert tag(mv)=="xep"
    if color(mv)=='white':
       zobrist.PlaceMan(osq(mv),man.pawn)
       #board.theBoard[osq(mv)] = man.pawn
       zobrist.PlaceMan(nsq(mv),0)
       #board.theBoard[nsq(mv)] = 0
       zobrist.PlaceMan(bak(nsq(mv)),-man.pawn)
       #board.theBoard[bak(nsq(mv))]= -man.pawn
       board.whiteMen.add(osq(mv))
       board.whiteMen.remove(nsq(mv))
       board.blackMen.add(bak(nsq(mv)))
    else:
       zobrist.PlaceMan(osq(mv),-man.pawn)
       #board.theBoard[osq(mv)] = -man.pawn
       zobrist.PlaceMan(nsq(mv),0)
       #board.theBoard[nsq(mv)] = 0
       zobrist.PlaceMan(fwd(nsq(mv)),man.pawn)
       #board.theBoard[fwd(nsq(mv))] = man.pawn
       board.blackMen.add(osq(mv))
       board.blackMen.remove(nsq(mv))
       board.whiteMen.add(fwd(nsq(mv)))
    del board.history[hmc(mv)]
    
# null move ~ not actually a legal move.  It is an artifical device used by the
# static evaluator.  For example, estimate black's mobility by looking at the
# number of legal moves he has if were his move.
    
def mknull(mv):
    assert tag(mv)=="null"
    board.history[hmc(mv)] = mv

def umknull(mv):
    assert tag(mv)=="null"
    del board.history[hmc(mv)]
    
#---------------------------------------------------------------------------------------
# Presentation Layer Stuff for Moves  (consider this all a  higher layer)
#---------------------------------------------------------------------------------------
#--------------------------------------------------------------------------------------------------
# IMPORTANT:  These reference the board as it is before the move!
# Using these to print a move after it has been made on the board will not work.
# You must print the move before making it on the board!
#-------------------------------------------------------------------------------------------------

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

#----------------------------------------------------------------------
# These are a bit verbose but I think they are all fall within the SAN standard
#  See http://www.very-best.de/pgn-spec.htm
# A more consise implementation of move printed is implemented at a higher
# layer in san.py which can take advange of knowlege of what moves are legal
# to make a more concise and more traditional algebraic notation.
# Routine below give us a basic human-friendly move notation using only what
# is available at this layer.
#----------------------------------------------------------------------
       
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
    return "%s(%s)" % ( prdash(mv), man.pr(pmn(mv)) )

def prcapturepromote(mv):
    return "%s(%s)" % ( prcapture(mv), man.pr(pmn(mv)) )

def prxep(mv):
    return "%s(ep)" % prcapture(mv)
