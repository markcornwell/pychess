# $Id: fen.py 7 2010-01-13 12:16:47Z mark $
#
#------------------------------------------------------------------------------
# FEN ~ Forsyth-Edwards Notation
#  A standard notation for exchanging chess positions
# see fen.txt
#
# An intesting use for exchanging positions is to allow a community of
# chess agents to cooperate with each other.
#
# Another way to specify positions would just be to send the move history
# say as a PGN file.  Seems more elegant even, given that programs should
# already understand PGN.
#
# If we are talking to our own program, we could just send the history.
# Everything in the position can be reconstucted from that.
#------------------------------------------------------------------------------
import square,man,board

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

# converting board position to FEN
       
def pr():
    fmt = "%s %s %s %s %s %s"
    return fmt % (prPieceData(),
                  prActiveColor(),
                  prCastlingAvail(),
                  prEpTargetSq(),
                  prHalfMoveClock(),
                  prFullMoveNumber())

def prPieceData():
    cnt = 0
    d = ""
    for r in xrange(7,-1,-1):
        for f in xrange(0,8):
            sq = r*8 + f
            m = board.manAt(sq)
            if man.isMan(m):
                if cnt>0:
                    d = d + str(cnt)
                    cnt = 0
                d = d+sym[m]
            else:
                assert man.isEmpty(m)
                cnt = cnt+1
        if r>0:
            d = d + "/"
    return d

def prActiveColor():
    if board.whiteToMove():
        return "w"
    else
        return "b"

def prCastlingAvail():
    av = ""
    if board.whiteAllowOO:
        av = av + "K"
    if board.whiteAllowOOO:
        av = av + "Q"
    if board.blackAllowOO:
        av = av + "k"
    if board.blackAllowOOO:
        av = av + "q"
    if av=="":
        av = "-"

               
def prEpTargetSq():
    if len(board.history)=0:
        return "-"
    mv = board.lastmove()
    if move.tag(mv)=="-" and board.manAt(move.nsq(mv))==man.pawn:
        if move.color(mv)=='white':
            if square.rank(move.osq(mv))==2 and square.rank(move.nsq(mv))==4:
                return square.pr(square.fwd(move.osq(mv)))
        else:
            assert move.color(mv)=='black'
            if square.rank(move.osq(mv))==7 and square.rank(move.nsq(mv))==5:
                return square.pr(square.bak(move.osq(mv)))
    else:
        return "-"

def prHalfMoveClock():
    #number of half moves since the last pawn advance or capturing move
    return "0"  # TBD
    
def prFullMoveNumber():
    return str(len(history)/2 + 1)
    
# converting FEN to board position

isym = { }  # to be inverse of sym
for k in sym.keys():
    isym[sym[k]]=k

def rd(s):
    board.clear()
    f = s.split(" ")
    rdPieceData(f[0])
    rdActiveColor(f[1])
    rdCastlingAvail(f[2])
    rdEpTargetSq(f[3])
    rdHalfMoveClock(f[4])
    rdFullMoveNumber(f[5])

def rdPieceData(f):
    sq = 63
    i = 0
    while sq>=0:
        fi = f[i]
        if fi in isym.keys():
            board.addMan(isym[fi],sq)
            sq = sq-1
        elif fi="/":
            assert afile(sq)
        else:
            cnt = int(fi)
            assert cnt>0
            assert cnt<=8
            while cnt>0:
                sq = sq-1
                cnt = cnt-1
        i = i+1

def rdActiveColor(f):
    global activeColor
    assert f in ["w","b"]
    activeColor=f

def rdCastlingAvail(f):
    board.whiteAllowOO = False
    board.whiteAllowOOO = False
    board.blackAllowOO = False
    board.blackAllowOOO = False
    if f="-":
        return
    for c in f:
        if c=="K":
            board.whiteAllowOO = True
        elif c=="Q":
            board.whiteAllowOOO = True
        elif c=="k":
            board.blackAllowOO = True
        elif c=="q":
            board.blackAllowOOO = True

def rdEpTargetSq(f)
    if f=="-":
        pass
    else:
        assert len(f)==2
        assert f[2] in ['a','b','c','d','e','f','g','h']
        assert f[1] in ['1','2','3','4','5','6','7','8']
        pass  #TBD

def rdHalfMoveClock(f):
    pass #
    
def rdFullMoveNumber(f)
    # now we are screwed because I have been using len(history) for move number everywhere
    # major revision now to deal with a history that picks up in the middle of the game
    # Need to think on this.




