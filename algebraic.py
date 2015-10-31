# $Id: algebraic.py 7 2010-01-13 12:16:47Z mark $
#
# Algebraic Notation
#
# Routines to look up  legal moves from Standard Algebraic Notation (SAN) defined
# in the PGN Specification.
#
# Given SAN strings such as "e5", or "Nf3", find will th search move list and find
# corresponding move tuples.
#
# Ref: Portable Game Notation (PGN) Specification,  http://www.very-best.de/pgn-spec.htm

import man, board, legal

from move   import tag,osq,nsq,pmn
from board  import manAt
from square import rd,file,rank
from man    import isPawn, isKind

# These characters are used to make up patterns on the left hand side
# of the fm table.  E.g.  Nf3 matches pattern pln, exd5 matches pattern lxln

tbl = { 'l' : "abcdefgh",    # letter
        'f' : "abcdefgh",    # file (same as letter)
        'n' : "12345678",    # number
        'r' : "12345678",    # rank (same as number)
        'p' : "KQRNBP",      # piece or pawn
        'q' : "QRBN" }       # what a queen can promote to        
  
kind = {'K': man.king,   'Q': man.queen,   'R': man.rook,
        'B': man.bishop, 'N': man.knight,  'P': man.pawn }

atbl = { 'a':1, 'b':2, 'c':3, 'd':4, 'e':5, 'f':6, 'g':7, 'h':8 }
ntbl = { '1':1, '2':2, '3':3, '4':4, '5':5, '6':6, '7':7, '8':8 }

#------------------------------------------------------------------------------
# Each pattern corresponds to a function we can use to filter the moves.
# The function is given as a lambda expression that operates on
# a move tuple mv evaluating to truth if that tuple matches the move string s.
# See header comment in move.py for the format of the move tuples
#------------------------------------------------------------------------------

fm = {
    "ln" :     lambda s,mv: tag(mv)=="-"
                   and nsq(mv)==rd(s) 
                   and isPawn(manAt(osq(mv))),
    "pln":     lambda s,mv: tag(mv)=="-"  
                   and nsq(mv)==rd(s[1:3]) 
                   and isKind(manAt(osq(mv)),kind[s[0]]),
    "pxln":    lambda s,mv: tag(mv)=="x"
                   and nsq(mv)==rd(s[2:4])  
                   and isKind(manAt(osq(mv)),kind[s[0]]),  
    "lxln":    lambda s,mv: tag(mv) in ["x","xep"]
                   and nsq(mv)==rd(s[2:4])
                   and file(osq(mv))==atbl[s[0]]
                   and isPawn(manAt(osq(mv))), 
    "lnxln":   lambda s,mv: tag(mv) in ["x","xep"]
                   and nsq(mv)==rd(s[3:5])
                   and osq(mv)==rd(s[0:2]),
    "O-O":     lambda s,mv: tag(mv)=="OO",
    "O-O-O":   lambda s,mv: tag(mv)=="OOO",                   
    "pfln":    lambda s,mv: tag(mv)=="-"
                   and nsq(mv)==rd(s[2:4])
                   and file(osq(mv))==atbl[s[1]]
                   and isKind(manAt(osq(mv)),kind[s[0]]),
    "prln":    lambda s,mv: tag(mv)=="-"
                   and nsq(mv)==rd(s[2:4])
                   and rank(osq(mv))==ntbl[s[1]]
                   and isKind(manAt(osq(mv)),kind[s[0]]),
    "ln=q":    lambda s,mv: tag(mv)=="-/"
                   and nsq(mv)==rd(s[0:2])  
                   and isKind(pmn(mv),kind[s[3]]),
    "lxln=q":  lambda s,mv: tag(mv)=="x/"
                   and nsq(mv)==rd(s[2:4])
                   and file(osq(mv))==atbl[s[0]]
                   and isKind(pmn(mv),kind[s[5]]),
    "lnxln=q": lambda s,mv: tab(mv)=="x/"
                   and osq(mv)==rd(s[0:2])
                   and nsq(mv)==rd(s[3:5])
                   and isKind(pmn(mv),kind[s[6]]),
    "prfln":    lambda s,mv: tag(mv)=="x"
                   and nsq(mv)==rd(s[3:5])
                   and osq(mv)==rd(s[1:3])
                   and isKind(manAt(osq(mv)),kind[s[0]]),                       
    "prxln":    lambda s,mv: tag(mv)=="x"
                   and nsq(mv)==rd(s[3:5])
                   and rank(osq(mv))==ntbl[s[1]]
                   and isKind(manAt(osq(mv)),kind[s[0]]),
    "pfxln":    lambda s,mv: tag(mv)=="x"
                   and nsq(mv)==rd(s[3:5])
                   and file(osq(mv))==atbl[s[1]]
                   and isKind(manAt(osq(mv)),kind[s[0]]),
    "prfxln":    lambda s,mv: tag(mv)=="x"
                   and nsq(mv)==rd(s[4:6])
                   and osq(mv)==rd(s[1:3])
                   and isKind(manAt(osq(mv)),kind[s[0]]),                  
    "p-ln":    lambda s,mv: tag(mv)=="-"
                   and nsq(mv)==rd(s[2:4])  
                   and isKind(manAt(osq(mv)),kind[s[0]]) }

#------------------------------------------------------------------------------
# Form returns True iff s matches the pattern string.  
# Letters in the pattern that appear
#  as keys in tbl above match on any of the given set of letters.  
#      E.g.  form("Nf3","pln")==True
# Letters in the pattern not appearing as keys must match exactly. 
#     E.g. form("Nxd5","pxln")==True
#------------------------------------------------------------------------------

def form(s,pat):
    "True iff string s matches the pattern"
    if len(pat)==0 and len(s)==0:
        return True
    elif len(pat)==0 or len(s)==0:
        return False
    elif tbl.has_key(pat[0]):
        return (s[0] in tbl[pat[0]]) and form(s[1:],pat[1:]) 
    else:
        return s[0]==pat[0] and form(s[1:],pat[1:])                   
   
def find(s,mvs):
    pred = None
    ss = strip(s)
    for (pat, f) in fm.items():
        if form(ss,pat):
            pred = f
    if pred==None:
        return []
    else:
        return filter(pred,ss,mvs)
        
def filter(pred,s,mvs):
    list = [ ]
    for mv in mvs:
        if pred(s,mv):
            list.append(mv)
    return list    

def strip(s):
    '''Strip off any annotation symbols at the end -- these never
    disambiguate moves, e.g. "Nxb7+"  becomes "Nxb7"'''
    ss = s
    while len(ss)>0 and last(ss) in ["+","#","!","?","="]:
        ss = ss.replace(last(ss),"")
    return ss

def last(s):
    return s[len(s)-1]
