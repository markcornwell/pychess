# $Id: square.py 7 2010-01-13 12:16:47Z mark $
#
#-----------------------------------------------------------------------------
#                                 Square
#-----------------------------------------------------------------------------

# squares are numbered 0 through 63, where 0 is a1 and 63 is h8

a8,b8,c8,d8,e8,f8,g8,h8 = 56,57,58,59,60,61,62,63 
a7,b7,c7,d7,e7,f7,g7,h7 = 48,49,50,51,52,53,54,55 
a6,b6,c6,d6,e6,f6,g6,h6 = 40,41,42,43,44,45,46,47
a5,b5,c5,d5,e5,f5,g5,h5 = 32,33,34,35,36,37,38,39
a4,b4,c4,d4,e4,f4,g4,h4 = 24,25,26,27,28,29,30,31 
a3,b3,c3,d3,e3,f3,g3,h3 = 16,17,18,19,20,21,22,23 
a2,b2,c2,d2,e2,f2,g2,h2 =  8, 9,10,11,12,13,14,15
a1,b1,c1,d1,e1,f1,g1,h1 =  0, 1, 2, 3, 4, 5, 6, 7 

def isq(sq): return 0 <= sq and sq<= 63

# columns and rows are zero origin, numbered 0 through 7

def col(sq):   return sq % 8
def row(sq):   return sq / 8

# rank and file are traditionally numbered 1 though 8

def rank(sq):  return row(sq)+1
def file(sq):  return col(sq)+1

# The first and last rank are significant.  So are the a and h files.

def firstrank(sq):  return sq!=None and rank(sq)==1
def lastrank(sq):   return sq!=None and rank(sq)==8
def afile(sq):      return sq!=None and file(sq)==1
def hfile(sq):      return sq!=None and file(sq)==8

def centerfile(sq): return sq!=None and 4 <= file(sq) and file(sq)<=6

# Relationships in various directions, with border effects.
# Note that fwd, bak,... are have None as a fixpoint, eg. fwd(None)==None
# This keeps them from wrapping around at the edge of the board.

def fwd(sq):
   if lastrank(sq) or sq==None:
      return None
   else:
      return sq+8

def bak(sq):
   if firstrank(sq) or sq==None:
      return None
   else:
      return sq-8

def rgt(sq):
   if hfile(sq) or sq==None:
      return None
   else:
      return sq+1

def lft(sq):
   if afile(sq) or sq==None:
      return None
   else:
      return sq-1

# since these are all composed from the above, they all have a
# fixpoint at None as well.

def dfr(sq):
   "diagonally forward-right"
   return fwd(rgt(sq))

def dfl(sq):
   "diagonally forward-left"
   return fwd(lft(sq))

def dbr(sq):
   "diagonally backward right"
   return bak(rgt(sq))

def dbl(sq):
   "diagonally backward left"
   return bak(lft(sq))

#-------------------------------------------------------------------------------------------------
# Encoding for human readability: squares are named with letter, and a digit
# Traditional "algebraic chess notation"  (Consider this a higher layer)
# It is concerned with presentation.
#-------------------------------------------------------------------------------------------------

atbl = { 'a':1, 'b':2, 'c':3, 'd':4, 'e':5, 'f':6, 'g':7, 'h':8 }
ntbl = { '1':1, '2':2, '3':3, '4':4, '5':5, '6':6, '7':7, '8':8 }

# maps letter-digit string to 0..63 form
def rd(an):
   #print "an=",an 
   assert len(an)==2 and atbl.has_key(an[0]) and ntbl.has_key(an[1])
   file = atbl[an[0]]
   rank = ntbl[an[1]]
   return (file-1) + (rank-1)*8

# maps 0-63 to letter digit form, e.g. prs(2) -> "c1"
def pr(n):
   assert isq(n)
   letter = "abcdefgh"[col(n)]
   digit =  "12345678"[row(n)]
   return letter + digit
