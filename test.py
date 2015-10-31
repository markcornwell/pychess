#!/usr/bin/python
# $Id: test.py 7 2010-01-13 12:16:47Z mark $
#
#-------------------------------------------------------------------------------
#                                      test
#-------------------------------------------------------------------------------

import man, board, move
from square import *

print "\nClear board:"
board.clear()
board.dump()

print "\nInitial position:"
board.reset()
board.dump()

print "\nClear board (again):"
board.clear()
board.dump()

print "\nInitial position (again):"
board.reset()
board.dump()

print "try to add 2nd king (two times)"
board.addMan(man.king,27)
board.addMan(-man.king,28)

BP= -man.pawn
WN=  man.knight
BN= -man.knight
WP=  man.pawn
WB=  man.bishop

# move tests
print "------------------ game 1 ---------------------"
game =((0,"-",12,28),     (1,"-",52,36),
       (2,"-", 6,21),     (3,"-",57,42),
       (4,"-", 5,33),     (5,"-",48,40),
       (6,"-",33,24),     (7,"-",62,45),
       (8,"x",21,36,BP),  (9,"x",42,36,WN),
       (10,"OO",4))

for i in xrange(0,len(game)):
   move.make(game[i])
   board.dump()

for i in xrange(len(game)-1,-1,-1):
   move.umake(game[i])
   board.dump()

print "e4=",rd("e4")
print "d4=",rd("d4")
print "a1=",rd("a1")
print "h8=",rd("h8")

def mov(n,so,t,sn=999,sm=999):
   if t=="-":
         return (n,"-",rd(so),rd(sn))
   elif t=="x":
         return (n,"x",rd(so),rd(sn),sm)
   elif t=="OO":
         return (n,"OO",rd(so))
   elif t=="OOO":
         return (n,"OOO",rd(so))
   elif t=="()":
         return (n,"()",rd(so),rd(sn),sm)
   elif t=="xep":
         return (n,"xep",srd(so),rd(sn),sm)
   else:
         print "error: move: no such type"

# move tests
#game = [mov(0,"e2","-","e4"),    mov(1, "e7","-","e5"),
#        mov(2,"g1","-","f3"),    mov(3, "b8","-","c6"),
#        mov(4,"f1","-","b5"),    mov(5, "a7","-","a6"),
#        mov(6,"b5","-","a4"),    mov(7, "g8","-","f6"),
#        mov(8,"f3","x","e5",BP), mov(9, "c6","x","e5",WN),
#        mov(10,"e1","OO"),       mov(11,"f6","x","e4",WP),
#        mov(12,"f1","-","e1"),   mov(13,"d7","-","d5")]

print "------------------ game 2 ---------------------"
game =( (0,"-",e2,e4),      (1,"-",e7,e5),
        (2,"-",g1,f3),     (3,"-",b8,c6),
        (4,"-",f1,b5),     (5,"-",a7,a6),
        (6,"-",b5,a4),     (7,"-",g8,f6),
        (8,"x",f3,e5,BP),  (9,"x",c6,e5,WN),
        (10,"OO",e1),      (11,"-",b7,b5),
        (12,"-",d1,f3),    (13,"x",b5,a4,WB),
        (14,"-",b2,b4),    (15,"xep",a4,b3,WP),
        (16,"x",c2,b3,BP), (17,"x",f6,e4,WP),
        (18,"-",c1,b2),    (19,"-",f8,d6),
        (20,"-",h2,h3),    (21,"-",h7,h6),
        (22,"x",b2,e5,BN), (23,"-",c8,b7),
        (24,"x",e5,g7,BP), (25,"-",d8,e7),
        (26,"-",b1,c3),    (27,"-",c7,c5),
        (28,"-",g7,f6),    (29,"-",c5,c4),
        (30,"x",f3,e4,BN), (31,"x",c4,b3,WP),
        (32,"-",d2,d3),    (33,"-",b3,b2),
        (34,"-",d3,d4))		
		
		
print "game=",game

for i in xrange(0,len(game)):
   move.make(game[i])
   board.dump()

print "------------- undo game 2 ----------------"
for i in xrange(len(game)-1,-1,-1):
   move.umake(game[i])
   board.dump()

# pretty square encoding
def prettysquareencoding():
    for r in xrange(7,-1,-1):
        for f in xrange(0,8):
            i = r*8+f
            print pr(i),
            if hfile(i):
                print

print "----- Pretty printing a game score ---------"
# about the best we can do without knowing all legal moves

print "game=",game
for i in xrange(0,len(game),2):
    print "%s. %-8s" % (move.num(game[i]),move.pr(game[i])),
    if i+1<len(game):
       print "   ",move.pr(game[i+1])
    else:
       print

print "----- Test of attack logic -------"
import attack
for i in xrange(0,len(game)):
   move.make(game[i])
   board.dump()

def displaywhiteattacks():
    for r in xrange(7,-1,-1):
        print "\nMap of squares under attack by white"
        for f in xrange(0,8):
           i = r*8+f
           if attack.whiteAttacks(i):
               print "WA",
           else:
               print "--",
           if hfile(i):
               print

dislaywhiteattacks()
