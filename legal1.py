# $Id: legal1.py 7 2010-01-13 12:16:47Z mark $
#
# Now we filter trial moves for legality, by disallowing moves where the king moves into check
# or castles through check.  Or, since we have not actually defined check at this point, the king
# moves onto an attacked square, or castles through an attacked square.  Here we make use
# of the attack routines.

# Planned Enhancement.  Add some caching to moves generation, legals, and attacks.
#  Cache legal moves, and recalcualte on move.make,move.unmake, board.reset, etc.
#

import trial, attack, move, board, man
from square import *
from attack import blackAttacks,whiteAttacks
from board import whiteToMove,blackToMove,manAt
from man import king,isKing

def moves():
    assert manAt(board.whiteKingAt) == king
    assert manAt(board.blackKingAt) == -king
    legalmoves = []
    for mv in trial.trialmoves():
        if not (move.tag(mv) in ["OO","OOO"]) and man.isKing(manAt(move.nsq(mv))):
            print "legal.19: mv=",mv
            board.dump()
        move.make(mv)
        assert manAt(board.whiteKingAt) == king
        assert manAt(board.blackKingAt) == -king
        if board.blackToMove():
            if move.isOO(mv):
                if not blackAttacks(e1) and not blackAttacks(f1) and not blackAttacks(g1):
                    legalmoves.append(mv)
            elif move.isOOO(mv):
                if not blackAttacks(e1) and not blackAttacks(d1) and not blackAttacks(c1):
                    legalmoves.append(mv)
            elif not blackAttacks(board.whiteKingAt):
                legalmoves.append(mv)
        elif board.whiteToMove():
            if move.isOO(mv):
                if not whiteAttacks(e8) and not whiteAttacks(f8) and not whiteAttacks(g8):
                    legalmoves.append(mv)
            elif move.isOOO(mv):
                if not whiteAttacks(e8) and not whiteAttacks(d8) and not whiteAttacks(c8):
                    legalmoves.append(mv)
            elif not whiteAttacks(board.blackKingAt):
                legalmoves.append(mv)
        move.umake(mv)
    assert manAt(board.whiteKingAt) == king
    assert manAt(board.blackKingAt) == -king
    assert noKingCapture(legalmoves) # you never see a king captured in any legal move
    return legalmoves

def noKingCapture(mvs):
    for mv in mvs:
        if move.tag(mv) in ["x","x/"]:
            if man.isKing(move.cmn(mv)):
                print "error (king capture): ",mv
                return False
            if man.isKing(manAt(move.nsq(mv))):
                print "error (king at nsq): ",mv
                return False
    return True

    

def state(legals):
    if len(legals)==0:
        if blackToMove() and whiteAttacks(board.blackKingAt):
            return 'whiteMates'
        elif whiteToMove() and blackAttacks(board.whiteKingAt):
            return 'blackMates'
        else:
            return 'stalemate'
    else:
        return 'continue'

        # TBD  look at 50 move rule, lack of mating material
        
#----------- obsolete -------

def mate(legals):
    assert False # do not call
    if len(legals)==0:
        if board.blackToMove() and attack.whiteAttacks(board.blackKingAt):
            return True
        elif board.whiteToMove() and attack.blackAttacks(board.whiteKingAt):
            return True
        else:
            return False
    else:
        return False
        
def stalemate(legals):
    assert False # do not call
    return len(legals)==0 and not mate(legals)

def draw(legals):
    assert False #do not call
    return stalemate(legals)


