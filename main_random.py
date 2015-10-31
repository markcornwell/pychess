#!/usr/bin/python -O
# $Id: main_random.py 7 2010-01-13 12:16:47Z mark $
#
# main
#
# Command loop: plays moves on board.  Exercises use of algebraic for input.
# This one talks to a human being.  See Mediate for an interface that talks
# to a GUI front end.

import board,legal,trial,move,man,algebraic,san
from square import *
import random,sys,time

autoshow = False
prompt = "> "
verbose = False
random.seed(777)

def main():
    global autoshow, verbose
    board.reset()
    #show()
    line = raw_input(prompt)
    toks = line.split(" ")
    cmd = toks[0]
    while cmd!="quit":
        board.valid()  # agressive validation
        # find and execute command
        if cmd in ["h","help"]:
            help()
        elif cmd in ["s","show"]:
            show()
        elif cmd in ["l","legals"]:
            legals()
        elif cmd in ["a","allow"]:
            allow()
        elif cmd in ["n","new"]:
            new()
        elif cmd in ["b","best"]:
            best()
        elif cmd in ["","r","random"]:
            rand()
        elif cmd in ["hammer"]:
            hammer()
        elif cmd in ["showoff"]:
            autoshow = False
        elif cmd in ["showon"]:
            autoshow = True
        elif cmd in ["verboseon"]:
            verbose = True
        elif cmd in ["verboseoff"]:
            verbose = False
        elif cmd in ["find"]:
            if len(toks)==1:
                s = raw_input("enter move> ")
            else:
                s = toks[1]
            find(s)
        elif cmd in ["u","undo"]:
            undo()
        elif cmd in ["d","dump"]:
            board.dump()
        else:
            trymv(cmd)
        # get next command
        line = raw_input(prompt)
        toks = line.split(" ")
        cmd = toks[0]

def help():
    print "Nf3          play the move"
    print "show         prints the board"
    print "legals       prints the list of legal moves"
    print "allow        prints what castling still allowed"
    print "new          starts a new game"
    print "quit         quits the game"
    print "random       make a random legal move"
    print "hammer       play random games until cntl-c keyboard interrupt"
    print "best         print the best move in this position [TBD]"
    print "showon       show board after every move"
    print "showoff      stop showing board after every move"
    print "verboseon    enable debugging output"
    print "verboseoff   disable debuggin output"
    print "find Nf3     just find the move, but don't try to make it"
    print "undo         undo last move"
    print "help         list of commands"
    
def show():
    board.show()
    print "%s to move" % toMove()

def auto():
    if autoshow:
        show()
    
def toMove():
    if board.whiteToMove():
        return 'white'
    else:
        return 'black'
    
def legals():
    mvs = legal.moves()
    for mv in mvs:
        if board.whiteToMove():
            print "%s %s" % (move.num(mv),san.pr(mv,mvs))
        else:
            print "%s ...%s" % (move.num(mv),san.pr(mv,mvs))

def allow():
    print "whiteAllowOO=",board.whiteAllowOO
    print "whiteAllowOOO=",board.whiteAllowOOO
    print "blackAllowOO=",board.blackAllowOO
    print "blackAllowOOO=",board.blackAllowOOO

def new():
    board.reset()
    auto()

def rand(silent=False):
    mvlist = legal.moves()
    if len(mvlist)>0:
        #n = random.randint(0,len(mvlist)-1)
        mv = random.choice(mvlist)
        if not silent:
            if move.color(mv)=='white':
                msg = "After %s %s" % (move.num(mv),san.pr(mv,mvlist))
            else:
                msg = "After %s ...%s" % (move.num(mv),san.pr(mv,mvlist))          
        move.make(mv)
        if not silent:
            print msg
            auto()
        if verbose:
            board.dump()
            assert board.valid() # aggressive validation
        return True
    else:
        print "no moves"
        return False

def hammer():
    movecount = 0
    gamecount = 0
    gamemoves = 0

    raw_input("Hit cntl-C to stop, any key to begin")
    starttime = time.clock()
    sys.stdout.write("started %s" % time.ctime(starttime))
    try:
        while True:
            if not rand() or kingsonly() or len(board.history)>200:
                gamecount = gamecount + 1
                sys.stdout.write("\n")
                sys.stdout.write("game %s finished in %s moves\n" % (gamecount,gamemoves))
                elapsedtime = time.clock() - starttime
                sys.stdout.write("total moves %s\n in %s seconds\n" % (movecount,elapsedtime))
                sys.stdout.write("avg %f sec/move\n" % (elapsedtime/movecount))
                sys.stdout.flush()
                show()
                gamemoves = 0
                new()
            movecount = movecount + 1
            gamemoves = gamemoves + 1
    except KeyboardInterrupt:
        print "%s moves played over %s games" % (movecount,gamecount)

def kingsonly():
    return len(board.whiteMen)==1 and len(board.blackMen)==1
        
def best():
    print "Not yet implemented"
            
def trymv(s):
    mvs = legal.moves()
    found = algebraic.find(s,mvs)
    if len(found)==0:
        print "not found"
    elif len(found)==1:
        move.make(found[0])
        auto()
    elif len(found)>1:
        print "ambiguous"

def find(s):
    mvs = legal.moves()
    found = algebraic.find(s,mvs)
    if len(found)==0:
        print " "*13 + "no such move"
    if len(found)==1:
        print " "*13+"found unique", san.pr(found[0],mvs)
    elif len(found)>1:
        print " "*13+"ambiguous, choices are:"
        for mv in found:
           print " "*17,san.pr(mv,mvs)
    return found

def undo():
    mv = board.lastMove()
    if mv==None:
        print "at start of game"
    else:
        move.umake(mv)
        auto()

main()
