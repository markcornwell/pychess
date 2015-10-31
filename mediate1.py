#!/usr/bin/python -u
# $Id: mediate1.py 7 2010-01-13 12:16:47Z mark $
#

# These are fuctions to mediate between the chess routines and the outside
# inteface, e.g. command line or a gui
#
# Works with XBoard - see engine-intf.html
# Do not use WinBoard.  Use XBoard under cygwin's xwin
# Need to patch security flaw in XBoard 

import sys, random
import board, legal, move, algebraic, san
from square import *
from attack import blackAttacks,whiteAttacks
import time

playing = False
protocolVerion = "unknown"

def get(strip=True):
    log("readline...")
    s = sys.stdin.readline()
    log("got %s" % s)
    if strip:
        return s.replace("\n","")
    else:
        return s
    
def put(s,newline=True):
    if newline:
        ss = "%s\n" % s
    else:
        ss = s
    log("put %s" % ss)
    sys.stdout.write(ss)

logf = open("mediate.log","w")
logf.write("log begun\n")
logf.flush()

def log(s):
    global logf
    logf.write(s)
    logf.flush()
    
def starts(cmd,s):
    return cmd[0:len(s)]==s
    
def xboard():
    cmd = "dummy"
    while cmd!="quit":
        log("cmd %s\n" % cmd)
        if cmd=="xboard":
            put("")
        elif starts(cmd,"protover"):
            protover(cmd)
        elif starts(cmd,"accepted"):
            pass
        elif starts(cmd,"new"):
            new()
        elif starts(cmd,"variant"):
            put_error("variant","not implemented")
        elif starts(cmd,"force"):
            put_error("force","not implemented")
        elif starts(cmd,"go"):
            put_error("go","not implemented")
        elif starts(cmd,"playother"):
            put_error("playother","not implemented")
        elif starts(cmd,"usermove"):
            usermove(cmd)
        elif starts(cmd,"?"):
            put_error("?","not implemented")
        elif starts(cmd,"ping"):
            put_pong(cmd)
        elif starts(cmd,"draw"):
            put("offer draw")
        elif starts(cmd,"result"):
            put_error("result","not implemented")
        elif starts(cmd,"setboard"):
            put_error("setboard","not implemented")
        elif cmd=="dummy":
            pass
        else:
            put_error(cmd,"unrecognized command")
        cmd = get()
 
def new():
    global playing
    board.reset()
    playing = True

def usermove(cmd):
    if not playing:
        put_error(cmd,"no game in progress")
    else:
        mvstring = cmd.split(" ")[1]
        trymv(mvstring)
    
def trymv(s):
    assert playing
    mvs = legal.moves()
    found = algebraic.find(s,mvs)
    if len(found)==0:
        put_illegalmove(s,"not found")
    elif len(found)==1:
        move.make(found[0])
        reply()  # sends the random response
    elif len(found)>1:
        put_illegalmove(s,"ambiguous")

def reply():
    global playing
    assert playing
    mvs = legal.moves()
    if len(mvs)>0:
        mv = random.choice(mvs)
        s = san.pr(mv,mvs) # use a different notation
        put_move(s)
        move.make(mv)
    else: 
        assert len(mvs)==0
        playing = False 
        if board.whiteToMove():
            if blackAttacks(board.whiteKingAt):
                put_result("1-0","white checkmated")
            else:
                put_result("1/2-1/2","stalemate")
        else:
            assert board.blackToMove()
            if whiteAttacks(board.blackKingAt):
                put_result("0-1","black checkmated")
            else:
                put_result("1/2-1/2","stalemate")        
        
def protover(cmd):
    global protocolVersion
    protocolVersion = cmd.split(" ")[1]
    put_feature()

# These all talk ot winboard
def put_pong(cmd):
    number = cmd.split(" ")[1]
    put("pong %s" % number)

def put_feature():
    put('feature myname="Black Momba" usermove=1 san=1 draw=1 colors=0')
    put('feature done=1')  # must be last feature 

def put_illegalmove(mvstring,reason=""):
    if reason=="":
        put("Illegal move: %s" % mvstring)
    else:
        put("Illegal move (%s): %s" % (reason,mvstring))

def put_error(cmd,reason):
    put("Error (%s): %s" % (reason,cmd))

def put_move(mvstring):
    "tell winboard what move the engine made"
    put("move %s" % mvstring)
    
def put_result(res,comment):
    if res in ["0-1","1-0","1/2-1/2"]:
        put("%s { %s }" % (res,comment))
    else:
        put_error("res","internal error in engine")

xboard()
