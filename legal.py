# $Id: legal.py 7 2010-01-13 12:16:47Z mark $
#
#------------------------------------------------------------------------------
# Legal Moves
#
# Now we filter trial moves for legality, by disallowing moves where the king moves into check
# or castles through check.  Or, since we have not actually defined check at this point, the king
# moves onto an attacked square, or castles through an attacked square.  Here we make use
# of the attack routines.

# Planned Enhancement.  Add some caching to moves generation, legals, and attacks.
#  Cache legal moves, and recalcualte on move.make,move.unmake, board.reset, etc.
#------------------------------------------------------------------------------

import trial, attack, move, board, man
from square import *
from attack import blackAttacks,whiteAttacks
from board import whiteToMove,blackToMove,manAt
from man import king,isKing
from move import tag,make,umake,isOO,isOOO

def moves():
    assert manAt(board.whiteKingAt) == king
    assert manAt(board.blackKingAt) == -king
    legalmoves = []
    for mv in trial.trialmoves():
        make(mv)
        assert manAt(board.whiteKingAt) == king
        assert manAt(board.blackKingAt) == -king
        if blackToMove():
            if isOO(mv):
                if not blackAttacks(e1) and not blackAttacks(f1) and not blackAttacks(g1):
                    legalmoves.append(mv)
            elif isOOO(mv):
                if not blackAttacks(e1) and not blackAttacks(d1) and not blackAttacks(c1):
                    legalmoves.append(mv)
            elif not blackAttacks(board.whiteKingAt):
                legalmoves.append(mv)
        elif whiteToMove():
            if isOO(mv):
                if not whiteAttacks(e8) and not whiteAttacks(f8) and not whiteAttacks(g8):
                    legalmoves.append(mv)
            elif isOOO(mv):
                if not whiteAttacks(e8) and not whiteAttacks(d8) and not whiteAttacks(c8):
                    legalmoves.append(mv)
            elif not whiteAttacks(board.blackKingAt):
                legalmoves.append(mv)
        umake(mv)
    assert manAt(board.whiteKingAt) == king
    assert manAt(board.blackKingAt) == -king
    assert noKingCapture(legalmoves) # you never see a king captured in any legal move
    return legalmoves

def noKingCapture(mvs):
    for mv in mvs:
        if tag(mv) in ["x","x/"]:
            if isKing(move.cmn(mv)):
                print "error (king capture): ",mv
                return False
            if isKing(manAt(move.nsq(mv))):
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
        
