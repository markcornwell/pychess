# $Id: zobrist.py 7 2010-01-13 12:16:47Z mark $
#
#------------------------------------------------------------------------------
# Zobrist Hash for board positions
# Use for transposition table lookups
#
# assign each piece x square a random number
# xor together the numbers
#
#The following scheme was described by Zobrist in 1970:
#
#    * Generate 12x64 N-bit random numbers (where the transposition table 
#      has 2^N entries) and store them in a table.  Each random number is 
#      associated with a given piece on a given square (i.e., black rook on H4,
#      etc.)  An empty square is represented by a null word.
#
#    * Start with a null hash key.
#
#    * Scan the board; when you encounter a piece, XOR its random number
#       to the current hash key.  Repeat until the entire board has been examined.
#------------------------------------------------------------------------------

import man, square, board
import random

sym = { man.king   : "K",
        man.queen  : "Q",
        man.rook   : "R",
        man.bishop : "B",
        man.knight : "N",
        man.pawn   : "P",
       -man.king   : "k",
       -man.queen  : "q",
       -man.rook   : "r",
       -man.bishop : "b",
       -man.knight : "n",
       -man.pawn   : "p" } 

N = 30   # 2**16 = 64K

ran1 = { }
ran2 = { }

def genTbl(tbl):
    for sq in xrange(0,64):
        for m in sym.keys():
            tbl[sym[m]+square.pr(sq)] = random.randint(1,2**N)

def hashBoard():
    h = 0
    for sq in board.whiteMen:
        if not man.isMan(board.theBoard[sq]):
            print "sq=",sq
            board.dump()
        assert man.isMan(board.theBoard[sq])
        h = XOR(h,board.theBoard[sq],sq)   
    for sq in board.blackMen:
        assert man.isMan(board.theBoard[sq])
        h = XOR(h,board.theBoard[sq],sq)
    #print "hashBoard=",h
    return h

def XOR(h,mn,sq):
    if mn==0:
        return h
    else:
        return h ^ ran1[sym[mn]+square.pr(sq)]

# Hashes a man on a square.   Unhashes any existing man at that square.
# Sets theBoard[sq] = mn  while maintaining hash consistency
def PlaceMan(sq,mn):
    assert square.isq(sq)
    assert man.isMan(mn) or mn==0
    #print "hash:sq=%s mn=%s hash %s" % (sq,mn,board.hash),
    # hash away the old contents
    board.hash = XOR(board.hash,board.theBoard[sq],sq)
    # do the assignment
    board.theBoard[sq] = mn   
    # hash in the new contents
    board.hash = XOR(board.hash,mn,sq)
    #print "-> %s" % board.hash

genTbl(ran1)
genTbl(ran2)
