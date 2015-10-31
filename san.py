# $Id: san.py 7 2010-01-13 12:16:47Z mark $
#
# Standard Algebraic Notation
#
# To format a move in Standard Algrbraic Notation (SAN), we first use
# simplest form, then look it up with algebraic.find.  If it unique, we are done.
# If, there is more than one match we disambiguate it, by trying in turn 
# adding the rank, then adding the file, then adding both rank and file
# of the piece ot move into the notation.
#
# References
#   http://www.very-best.de/pgn-spec.htm
#   http://www.markalowery.net/Chess/Notation/pgn.html
#
# TBD - need to revise the patterns in algebraic to match the SAN patterns here.
# Nice test would be to (1) try it on existing PGN files  (2) interface with xboard

import square,man,algebraic
from algebraic import kind
from move   import tag,osq,nsq,pmn
from board  import manAt
from square import rd,col,row
from man    import isPawn, isPiece, isKind

def pr(mv,mvs):
    if tag(mv) in ["-","-/"]:
       return prdash(mv,mvs)
    elif tag(mv) in ["x","x/","xep"]:
       return prcapture(mv,mvs)
    elif tag(mv) == "OO":
       return prOO(mv,mvs)
    elif tag(mv) == "OOO":
       return prOOO(mv,mvs)
    else:
       print "san.pr: bad move type: %s" % mv[1]

# the assert condition reminds me that prdash is called from two places
# under different contitions.  It reminds me to handle both.     
def prdash(mv,mvs):
    assert tag(mv)=="-" or tag(mv)=="-/"
    if isPawn(manAt(osq(mv))):
        return prdashPawn(mv,mvs)
    else:
        return prdashPiece(mv,mvs)

# Note how the assert statements in prdashPawn and prdashPiece match up with
# the guards in prdash
        
def prdashPawn(mv,mvs):
    assert tag(mv)=="-" or tag(mv)=="-/"
    assert isPawn(manAt(osq(mv)))
    # simplest form - ln
    ln = square.pr(nsq(mv))
    if tag(mv)=="-/":
        q = man.pr(pmn(mv))
        s = "%s=%s" % (ln,q)
    else:
        s = ln
    found = algebraic.find(s,mvs)
    if len(found)==1:
        return s

def prdashPiece(mv,mvs):
    assert tag(mv)=="-"
    assert isPiece(manAt(osq(mv)))
    # simplest form - pln
    p  = man.pr(manAt(osq(mv)))
    ln = square.pr(nsq(mv))
    s  = "%s%s" % (p,ln)
    found = algebraic.find(s,mvs)
    if len(found)==1:
        return s
    # disabiguate by file - pfln
    f = "abcdefgh"[col(osq(mv))]
    s = "%s%s%s" % (p,f,ln)
    found = algebraic.find(s,mvs)    
    if (len(found))==1:
        return s
    # disambiguate by rank - prln
    r = "12345678"[row(osq(mv))]
    s = "%s%s%s" % (p,r,ln)
    found = algebraic.find(s,mvs)
    if (len(found))==1:
        return s
    # disambiguate by both -rare but possible - prfln
    s = "%s%s%s%s" % (p,r,f,ln)
    if (len(found))==1:
        return s
    # there should be no other cases given that move is legal
    assert False

def prcapture(mv,mvs):
    assert tag(mv) in ["x","x/","xep"]
    if isPawn(manAt(osq(mv))):
        return prcapturePawn(mv,mvs)
    else:
        return prcapturePiece(mv,mvs)    

def prcapturePawn(mv,mvs):
    assert tag(mv) in ["x","x/","xep"]
    assert isPawn(manAt(osq(mv)))
    # simplest form - fxln
    f = "abcdefgh"[col(osq(mv))]
    ln = square.pr(nsq(mv))
    if tag(mv)=="x/":
        q = man.pr(pmn(mv))
        s = "%sx%s=%s" % (f,ln,q)
    else:
        s = "%sx%s" % (f,ln)
    found = algebraic.find(s,mvs)
    if len(found)==1:
        return s
    # disambiguate by both - rfxln
    rf = square.pr(osq(mv))
    if tag(mv)=="x/":
        s = "%sx%s=%s" % (rf,ln,q)
    else:
        s = "%sx%s" % (rf,ln)    
    found = algebraic.find(s,mvs)
    if len(found)==1:
        return s
    # if move is legal there should be no other cases
    assert False
    
def prcapturePiece(mv,mvs):
    assert tag(mv) in ["x","x/","xep"]
    assert isPiece(manAt(osq(mv)))
    # simplest form - pxln
    p  = man.pr(manAt(osq(mv)))
    ln = square.pr(nsq(mv))
    s = "%sx%s" % (p,ln)
    found = algebraic.find(s,mvs)
    if len(found)==1:
        return s
    # disambiguate by file - pfxln
    f = "abcdefgh"[col(osq(mv))]
    s = "%s%sx%s" % (p,f,ln)
    found = algebraic.find(s,mvs)
    if len(found)==1:
        return s
    # disambiguate by rank - prxln
    r = "12345678"[row(osq(mv))]
    s = "%s%sx%s" % (p,r,ln)
    found = algebraic.find(s,mvs)
    if len(found)==1:
        return s
    # disambiguate by both - prfxln
    s = "%s%s%sx%s" % (p,r,f,ln)
    found = algebraic.find(s,mvs)
    if len(found)==1:
        return s    
    # if move is legal there should be no other cases
    assert False
    
def prOO(mv,mvs):
    return "O-O"

def prOOO(mv,mvs):
    return "O-O-O"
