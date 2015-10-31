# $Id: trial.py 7 2010-01-13 12:16:47Z mark $

#------------------------------------------------------------------------------
#                           trial moves
#------------------------------------------------------------------------------

from square import *
from move import osq,nsq,tag
import man,board,move
import sys

mvs = []

def trialmoves():
   if board.whiteToMove():
      return wtrials(len(board.history),board.whiteMen)
   else:
      return btrials(len(board.history),board.blackMen)

def wtrials(h,sqset):
   assert board.whiteToMove()
   assert h == len(board.history)
   global mvs
   mvs = []
   for sq in sqset:
      assert man.isWhite(board.manAt(sq))
      if board.manAt(sq)==man.pawn:
          wtrialpawn(h,sq)
      elif board.manAt(sq)==man.knight:
          wtrialknight(h,sq)
      elif board.manAt(sq)==man.bishop:
          wtrialbishop(h,sq)
      elif board.manAt(sq)==man.rook:
          wtrialrook(h,sq)
      elif board.manAt(sq)==man.queen:
          wtrialqueen(h,sq)
      elif board.manAt(sq)==man.king:
          wtrialking(h,sq)
      else:
          print "wtrials: square not occupied"
   return mvs

def btrials(h,sqset):
   assert board.blackToMove()
   assert h == len(board.history)
   global mvs
   mvs = []
   for sq in sqset:
      assert man.isBlack(board.manAt(sq))
      if board.manAt(sq) == -man.pawn:
          btrialpawn(h,sq)
      elif board.manAt(sq) == -man.knight:
          btrialknight(h,sq)
      elif board.manAt(sq) == -man.bishop:
          btrialbishop(h,sq)
      elif board.manAt(sq) == -man.rook:
          btrialrook(h,sq)
      elif board.manAt(sq) == -man.queen:
          btrialqueen(h,sq)
      elif board.manAt(sq) == -man.king:
          btrialking(h,sq)
      else:
          print "btrials: square not occupied"
   return mvs

#--------------------------------------------------------------------
#                                  pawn
#--------------------------------------------------------------------

def wtrialpawn(h,sq):
   assert board.whiteToMove()
   assert h == len(board.history)
   assert board.manAt(sq) == man.pawn
   global mvs
   # pawn may move 2 squares on first move
   if rank(sq)==2 and board.empty(fwd(sq)) and board.empty(fwd(fwd(sq))):
       mvs.append((h,"-",sq,fwd(fwd(sq))))
   # pawn moves only one square fwd if beyond original position and square is empty
   if rank(sq)<7:
       if board.manAt(fwd(sq))==0:
           mvs.append((h,"-",sq,fwd(sq)))
       if man.isBlack(board.manAt(dfr(sq))):
           mvs.append((h,"x",sq,dfr(sq),board.manAt(dfr(sq))))
       if man.isBlack(board.manAt(dfl(sq))):
           mvs.append((h,"x",sq,dfl(sq),board.manAt(dfl(sq))))
   # pawn promotes on reaching last rank    
   if rank(sq)==7:
       if board.manAt(fwd(sq))==0:
           for pmn in [man.queen,man.rook,man.bishop,man.knight]:
                mvs.append((h,"-/",sq,fwd(sq),0,pmn))
       if man.isBlack(board.manAt(dfr(sq))):
           for pmn in [man.queen,man.rook,man.bishop,man.knight]:
                mvs.append((h,"x/",sq,dfr(sq),board.manAt(dfr(sq)),pmn))
       if man.isBlack(board.manAt(dfl(sq))):
           for pmn in [man.queen,man.rook,man.bishop,man.knight]:
                mvs.append((h,"x/",sq,dfl(sq),board.manAt(dfl(sq)),pmn))
   # en passant             
   if len(board.history)>0:
       mv = board.lastMove()
       if tag(mv)=="-" and board.manAt(nsq(mv)) == -man.pawn and rank(osq(mv))==7 and rank(nsq(mv))==5:
           if nsq(mv) in [rgt(sq),lft(sq)]:
                mvs.append((h,"xep",sq,fwd(nsq(mv))))

def btrialpawn(h,sq):
   assert board.blackToMove()
   assert h == len(board.history)
   assert board.manAt(sq) == -man.pawn
   global mvs
   # pawn may move 2 squares on first move
   if rank(sq)==7 and board.empty(bak(sq)) and board.empty(bak(bak(sq))):
       mvs.append((h,"-",sq,bak(bak(sq))))
   # pawn moves only one square if beyond original position
   if rank(sq)>2:
       if board.manAt(bak(sq))==0:
           mvs.append((h,"-",sq,bak(sq)))
       if man.isWhite(board.manAt(dbr(sq))):
           mvs.append((h,"x",sq,dbr(sq),board.manAt(dbr(sq))))
       if man.isWhite(board.manAt(dbl(sq))):
           mvs.append((h,"x",sq,dbl(sq),board.manAt(dbl(sq))))
   # pawn promotes on reaching last rank
   if rank(sq)==2:
       if board.manAt(bak(sq))==0:
           for pmn in [-man.queen,-man.rook,-man.bishop,-man.knight]:
                mvs.append((h,"-/",sq,bak(sq),0,pmn))
       if man.isWhite(board.manAt(dbr(sq))):
           for pmn in [-man.queen,-man.rook,-man.bishop,-man.knight]:
                mvs.append((h,"x/",sq,dbr(sq),board.manAt(dbr(sq)),pmn))
       if man.isWhite(board.manAt(dbl(sq))):
           for pmn in [-man.queen,-man.rook,-man.bishop,-man.knight]:
                mvs.append((h,"x/",sq,dbl(sq),board.manAt(dbl(sq)),pmn))
   # en passant
   if len(board.history)>0:
       mv = board.lastMove()
       if tag(mv)=="-" and board.manAt(nsq(mv)) == man.pawn and rank(osq(mv))==2 and rank(nsq(mv))==4:
           if nsq(mv) in [rgt(sq),lft(sq)]:
                mvs.append((h,"xep",sq,bak(nsq(mv))))
                
#------------------------------------------------------------------------------
#                                  Knight
#------------------------------------------------------------------------------

def wtrialknight(h,sq):
   assert board.whiteToMove()
   assert h == len(board.history)
   assert board.manAt(sq) == man.knight
   global mvs
   for s in [dfr(fwd(sq)),dfr(rgt(sq)),dbr(rgt(sq)),dbr(bak(sq)),
             dbl(bak(sq)),dbl(lft(sq)),dfl(lft(sq)),dfl(fwd(sq))]:
      if board.empty(s):
          mvs.append((h,"-",sq,s))
      if man.isBlack(board.manAt(s)):
          mvs.append((h,"x",sq,s,board.manAt(s)))

def btrialknight(h,sq):
   assert board.blackToMove()
   assert h == len(board.history)
   assert board.manAt(sq) == -man.knight
   global mvs
   for s in [dfr(fwd(sq)),dfr(rgt(sq)),dbr(rgt(sq)),dbr(bak(sq)),
             dbl(bak(sq)),dbl(lft(sq)),dfl(lft(sq)),dfl(fwd(sq))]:
      if board.empty(s):
          mvs.append((h,"-",sq,s))
      elif man.isWhite(board.manAt(s)):
          mvs.append((h,"x",sq,s,board.manAt(s)))

#------------------------------------------------------------------------------
#                                  Bishop
#------------------------------------------------------------------------------

def wtrialbishop(h,sq):
   assert board.whiteToMove()
   assert h == len(board.history)
   assert board.manAt(sq) == man.bishop
   global mvs
   for dir in [dfr,dfl,dbr,dbl]:
      s = dir(sq)
      done = False
      while not s==None and not done:
         if board.empty(s):
             mvs.append((h,"-",sq,s))
             s = dir(s)
         elif man.isBlack(board.manAt(s)):
             mvs.append((h,"x",sq,s,board.manAt(s)))
             done = True
         elif man.isWhite(board.manAt(s)):
             done = True

def btrialbishop(h,sq):
   assert board.blackToMove()
   assert h == len(board.history)
   assert board.manAt(sq) == -man.bishop
   global mvs
   for dir in [dfr,dfl,dbr,dbl]:
      s = dir(sq)
      done = False
      while not s==None and not done:
         if board.empty(s):
             mvs.append((h,"-",sq,s))
             s = dir(s)
         elif man.isWhite(board.manAt(s)):
             mvs.append((h,"x",sq,s,board.manAt(s)))
             done = True
         elif man.isBlack(board.manAt(s)):
             done = True

#------------------------------------------------------------------------------
#                                  Rook
#------------------------------------------------------------------------------

def wtrialrook(h,sq):
   assert board.whiteToMove()
   assert h == len(board.history)
   assert board.manAt(sq) == man.rook
   global mvs
   for dir in [fwd,rgt,bak,lft]:
      s = dir(sq)
      done = False
      while not s==None and not done:
         if board.empty(s):
             mvs.append((h,"-",sq,s))
             s = dir(s)
         elif man.isBlack(board.manAt(s)):
             mvs.append((h,"x",sq,s,board.manAt(s)))
             done = True
         elif man.isWhite(board.manAt(s)):
             done = True

def btrialrook(h,sq):
   assert board.blackToMove()
   assert h == len(board.history)
   assert board.manAt(sq) == -man.rook
   global mvs
   for dir in [fwd,rgt,bak,lft]:
      s = dir(sq)
      done = False
      while not s==None and not done:
         if board.empty(s):
             mvs.append((h,"-",sq,s))
             s = dir(s)
         elif man.isWhite(board.manAt(s)):
             mvs.append((h,"x",sq,s,board.manAt(s)))
             done = True
         elif man.isBlack(board.manAt(s)):
             done = True

#------------------------------------------------------------------------------
#                                  Queen
#------------------------------------------------------------------------------

def wtrialqueen(h,sq):
   assert board.whiteToMove()
   assert h == len(board.history)
   assert board.manAt(sq) == man.queen
   global mvs
   for dir in [fwd,rgt,bak,lft,dfr,dfl,dbr,dbl]:
      s = dir(sq)
      done = False
      while not s==None and not done:
         if board.empty(s):
             mvs.append((h,"-",sq,s))
             s = dir(s)
         elif man.isBlack(board.manAt(s)):
             mvs.append((h,"x",sq,s,board.manAt(s)))
             done = True
         elif man.isWhite(board.manAt(s)):
             done = True
         else:
             print "error in wtrialqueen"
             sys.exit(1)

def btrialqueen(h,sq):
   assert board.blackToMove()
   assert h == len(board.history)
   assert board.manAt(sq) == -man.queen
   global mvs
   for dir in [fwd,rgt,bak,lft,dfr,dfl,dbr,dbl]:
      s = dir(sq)
      done = False
      while not s==None and not done:
         if board.empty(s):
             mvs.append((h,"-",sq,s))
             s = dir(s)
         elif man.isWhite(board.manAt(s)):
             mvs.append((h,"x",sq,s,board.manAt(s)))
             done = True
         elif man.isBlack(board.manAt(s)):
             done = True
         else:
             print "error in btrialqueen"
             sys.exit(1)
#------------------------------------------------------------------------------
#                                  King
#------------------------------------------------------------------------------

def wtrialking(h,sq):
    assert board.whiteToMove()
    assert h == len(board.history)
    assert board.manAt(sq) == man.king
    global mvs
    for dir in [fwd,dfr,rgt,dbr,bak,dbl,lft,dfl]:
        s = dir(sq)
        if board.empty(s):
            mvs.append((h,"-",sq,s))
        elif man.isBlack(board.manAt(s)):
            mvs.append((h,"x",sq,s,board.manAt(s)))
        elif man.isWhite(board.manAt(s)):
            pass
    if board.whiteAllowOO and board.empty(f1) and board.empty(g1):
        mvs.append((h,"OO",e1))
    if board.whiteAllowOOO and board.empty(d1) and board.empty(c1) and board.empty(b1):
        mvs.append((h,"OOO",e1))

def btrialking(h,sq):
    assert board.blackToMove()
    assert h == len(board.history)
    assert board.manAt(sq) == -man.king
    global mvs
    for dir in [fwd,dfr,rgt,dbr,bak,dbl,lft,dfl]:
        s = dir(sq)
        if board.empty(s):
            mvs.append((h,"-",sq,s))
        elif man.isWhite(board.manAt(s)):
            mvs.append((h,"x",sq,s,board.manAt(s)))
        elif man.isBlack(board.manAt(s)):
            pass
    if board.blackAllowOO and board.empty(f8) and board.empty(g8):
        mvs.append((h,"OO",e8))
    if board.blackAllowOOO and board.empty(d8) and board.empty(c8) and board.empty(b8):
        mvs.append((h,"OOO",e8))

#------------------------------------------------------------------------------
#                                  Display
#------------------------------------------------------------------------------

def pr(tmoves):
    for m in tmoves:
      if move.hmc(m)%2==1:
          print "%s. ... %s" % (move.num(m),move.pr(m))
      else:
          print "%s. %s" % (move.num(m),move.pr(m))