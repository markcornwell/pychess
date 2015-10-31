# $Id: board.py 7 2010-01-13 12:16:47Z mark $
#
#---------------------------------------------------------------------
#                                 Board
#---------------------------------------------------------------------
# previous version June 11, 2006
#---------------------------------------------------------------------
# Modify to support Zobrist hashing
# stop allowing other routine to writed directly to the board
# all write now go through a function that computes a hash.
#
# This version strengthens encapsulsation of decisions in man
# Eliminiates assumptions about man encodings that seeped over
# For comparison previous version was board1.py

import square, man, sys
import zobrist

# We represent an empty chessboard as an array of 64 zero's.
theBoard = [0] * 64

# Any time the board changes these must  be maintained
# we decide to hang has maintennence off of these functions

whiteMen = set([ ])    # set of squares holding white men
blackMen = set([ ])    # set of squares holding black men

whiteKingAt = 999      # position of white king (999 if not set)
blackKingAt = 999      # position of black king (999 if not set)

# Any time a move is made (unmade), these must be maintained

whiteAllowOO  = True  # True iff white King and King's Rook have not moved
whiteAllowOOO = True  # True iff white King and Queen's Rook have not moved
blackAllowOO  = True  # True iff black King and King's Rook have not moved
blackAllowOOO = True  # True iff black King and Queen's Rook have not moved

flags = []
hash = 0

# A quite beautiful implementation of a stack for saving and restoring flags

def pushFlags():
    flags.append((whiteAllowOO, whiteAllowOOO, blackAllowOO, blackAllowOOO))

def popFlags():
    global whiteAllowOO, whiteAllowOOO, blackAllowOO, blackAllowOOO
    whiteAllowOO, whiteAllowOOO, blackAllowOO, blackAllowOOO = flags.pop()

#----------------------------------------------------------------
# We keep a history of the moves made in the game
# We can always tell whose move it is.
#----------------------------------------------------------------

history = { }          # dictionary of the moves made so far
                       # key is half move number starting at 0    
def lastMove():
    if len(history)==0:
        return None
    else:
        return history[len(history)-1]

def whiteToMove():
    return len(history) % 2 == 0

def blackToMove():
    return len(history) % 2 == 1

def colorToMove():
    if whiteToMove():
        return 'white'
    else:
        return 'black'

#--------------------------------------------------------------------------------    
# We interpret the theBoard with these routines.  Given a square
# we can tell what man is on it, or test to see if it is occupied
# or empty.
#--------------------------------------------------------------------------------

def manAt(sq):
   if sq==None:
       return None
   else:
       return theBoard[sq]

def occupied(sq):
   if sq==None:
       return False
   else:
       return theBoard[sq]!=0

def empty(sq):
   return manAt(sq)==0

# addMan validates as it populates the board

def addMan(m,sq):
   global theBoard,whiteKingAt, blackKingAt, whiteMen, blackMen
   if not man.isMan(m):
      print "addman: bad value for man: %s" % m
   elif not square.isq(sq):
      print "addman: bad value for square: %s" %sq
   elif man.isPawn(m) and (square.lastrank(sq) or square.firstrank(sq)):
      print "addman: pawns not allowed on rank" % rank(sq)
   elif occupied(sq):
      print "addman: square %s is occupied" % sq
   elif man.isWhiteKing(m) and not (whiteKingAt == 999):
      print "addman: only one white king allowed"
   elif man.isBlackKing(m) and not (blackKingAt == 999):
      print "addman: only one black king allowed"
   else:
      #assert hash == zobrist.hashBoard()
      if man.isWhite(m):
         if man.isKing(m):
            whiteKingAt = sq
         whiteMen.add(sq)
      else:
         if man.isKing(m):
            blackKingAt = sq
         blackMen.add(sq)     
      zobrist.PlaceMan(sq,m)
      #assert hash == zobrist.hashBoard()

def dump():
   show()
   print "whiteMen=", whiteMen
   print "blackMen=", blackMen
   print "whiteKingAt=", whiteKingAt
   print "blackKingAt=", blackKingAt
   print "history=", history
   print "len(history)=", len(history)
   print "whiteAllowOO=", whiteAllowOO
   print "whiteAllowOOO=", whiteAllowOOO   
   print "blackAllowOO=", blackAllowOO
   print "blackAllowOOO=", blackAllowOOO
   print "flags=", flags
   print "hash=", hash

#----------------------------------------------------------------------------
# valid() either returns True or throws an assert violation
# Caputures alot of our data structure invariant for the board
# Instrumented with some diagnostics if consistency checks fail
# This is a very expensive check, responsible for most of the
# time in assertion checking.
#----------------------------------------------------------------------------

def valid():
   #return True # disabled to speed up testing
   if not hash == zobrist.hashBoard():
      dump()
   assert hash == zobrist.hashBoard()
   assert theBoard[whiteKingAt] == man.king
   # debug
   if theBoard[blackKingAt] != -man.king:
       print "board 136: dumping"
       dump()
   assert theBoard[blackKingAt] == -man.king
   for sq in xrange(0,64):
      if manAt(sq)==0:
          assert (sq in whiteMen) == False
          assert (sq in blackMen) == False
      elif man.isWhite(manAt(sq)):
          assert (sq in whiteMen) == True
          # debug
          if (sq in blackMen):
                print "board 147: manAt(sq)=",manAt(sq)
                print "board 148: sq=",sq
                print "board 149: blackMen=", blackMen
                dump()
          assert (sq in blackMen) == False
      elif man.isBlack(manAt(sq)):
          # debug
          if (sq in whiteMen):
                print "board 155: manAt(sq)=",manAt(sq)
                print "board 156: sq=",sq
                print "board 157: whiteMen=", whiteMen  
                dump()
          assert (sq in whiteMen) == False
          assert (sq in blackMen) == True
      else:
          assert False
   return True

def clear():
   global theBoard, whiteMen, blackMen, whiteKingAt, blackKingAt, history
   global whiteAllowOO, whiteAllowOOO, blackAllowOO, blackAllowOOO
   global flags, hash
   for sq in xrange(0,64):
      theBoard[sq]=0
   hash = 0
   whiteMen = set([ ])
   blackMen = set([ ])
   whiteKingAt = 999
   blackKingAt = 999
   history = { }
   whiteAllowOO = True
   whiteAllowOOO = True
   blackAllowOO = True
   blackAllowOOO = True
   flags = []
   assert hash == zobrist.hashBoard()
 
def setup():
   backrank=[man.rook,man.knight,man.bishop,man.queen,man.king,man.bishop,man.knight,man.rook]
   for sq in xrange(0,8):
      addMan(backrank[sq],sq)
   for sq in xrange(8,16):
      addMan(man.pawn, sq)
   for sq in xrange(48,56):
      addMan(-man.pawn,sq)
   for sq in xrange(56,64):
      addMan(-backrank[sq-56],sq)
   valid()

def reset():
    clear()
    setup()

# basic display
def display(msg, newline=True, silent=False):
    if silent:
        return
    if newline:
        msg += '\n'
    sys.stdout.write(msg)
    sys.stdout.flush()

def show():
   print "-----------------------"
   for r in xrange(7,-1,-1):
      for f in xrange(0,8):
         sq = r*8 + f
         display(man.symbol(theBoard[sq])+" ", square.hfile(sq))
   print "-----------------------"

