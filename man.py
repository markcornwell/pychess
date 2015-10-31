# $Id: man.py 7 2010-01-13 12:16:47Z mark $
#
#--------------------------------------------------------------------
#                                 man
#--------------------------------------------------------------------

# We try to isolate the choice of integers inside this module
# in case we want to change it later.  We might even change
# it to something other than integers.
#
# A nice test of how well we encapsulated this secret would be
# to swap out this file for one with integer code defined differently.
# I expect right now to see errors, but they should all be fixable.

# integer codes for each kind of chessman

king   = 1
queen  = 2
rook   = 3
bishop = 4
knight = 5
pawn   = 6

# we use the positive values for white and negative for black
# we reserve 0 to indicate the absense of a man
# None is produced by squares past the edges of the board

def isWhite(m):     return m!=None and m>0
def isBlack(m):     return m!=None and m<0
def isMan(m):       return m!=None and king<=abs(m) and abs(m)<= pawn
def isPiece(m):     return m!=None and king<=abs(m) and abs(m)< pawn
def isEmpty(m):     return m==0

def isQRBN(m):      return 0<abs(m) and abs(m)<6
def whiteQRBN(m):   return 1<m and m<6
def blackQRBN(m):   return -6<m and m<1
def isWhiteKing(m): return m==king
def isBlackKing(m): return m==-king

# to check what kind of man look at the absolute value
def isKind(m,kind): return abs(m)==kind
def isKing(m):      return isKind(m,king)
def isQueen(m):     return isKind(m,queen)
def isBiship(m):    return isKind(m,bishop)
def isKnight(m):    return isKind(m,knight)
def isPawn(m):      return isKind(m,pawn)

# some standard symbols for basic display

def symbol(m):
   if m==0:
      return '--'
   elif isWhite(m):
      return ('WK','WQ','WR','WB','WN','WP')[m-1]
   elif isBlack(m):
      return ('BK','BQ','BR','BB','BN','BP')[abs(m)-1]

#-------------------------------------------------------------------------------
#  Presentation Layer
#-------------------------------------------------------------------------------

def pr(m):
    assert isMan(m)
    return "KQRBNP"[abs(m)-1]

