#!/usr/bin/python -Ou
# $Id: mediate.py 7 2010-01-13 12:16:47Z mark $
#

# These are fuctions to mediate between the chess routines and the outside
# inteface, e.g. command line or a gui
#
# Works with XBoard - see engine-intf.html
# Do not use WinBoard.  Use XBoard under cygwin's xwin
# Need to patch security flaw in XBoard 

import os, sys, random
import board, legal, move, algebraic, san
from square import *
from attack import blackAttacks,whiteAttacks
import time
import best
import alphabeta

#playing = False    
engineColor = None   # color engine plays
assert engineColor in [None,'white','black']

def stopClocks():
    pass  # TBD
   
feature_requested = { }
feature_accepted = { }

def put_featureXXX():
    put('feature myname="Black Momba"')
    put('feature usermove=1 san=1 draw=1 colors=0 sigint=0 sigterm=0 done=1')

def put_feature():
    request('myname','\"Black Momba\"')
    request('usermove','1')
    request('san','1')
    request('draw','1')
    request('colors','0')
    request('sigint','0')
    request('sigterm','0')
    request('time','0')
    request('reuse','1')
    #request('done','1')  # must be last feature 

def request(key,val):
    feature_requested[key]=val
    put('feature %s=%s' % (key,val))    
    
def accepted(cmd):
    key = cmd.split(" ")[1]
    feature_accepted[key] = feature_requested[key]
    
def get(strip=True):
    #log("readline...")
    s = sys.stdin.readline()
    if engineColor==None:
        log("?????(%s) got %s\n" % (os.getpid(),s))
    else:
        log("%s(%s) got %s\n" % (engineColor,os.getpid(),s))
    if strip:
        return s.replace("\n","")
    else:
        return s
    
def put(s,newline=True):
    if newline:
        ss = "%s\n" % s
    else:
        ss = s
    if engineColor==None:
        log("?????(%s) put %s" % (os.getpid(),ss))
    else:
        log("%s(%s) put %s" % (engineColor,os.getpid(),ss))    
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
    global engineColor
    cmd = "dummy"
    while cmd!="quit":
        #log("cmd %s\n" % cmd)
        if cmd=="xboard":
            put("")
        elif starts(cmd,"protover"):
            protover(cmd)
        elif starts(cmd,"accepted"):
            accepted(cmd)
        elif starts(cmd,"new"):
            new()
        elif starts(cmd,"variant"):
            put_error("variant","not implemented")
        elif starts(cmd,"force"):
            force()
        elif starts(cmd,"go"):
            go()
        elif starts(cmd,"random"):
            pass
        elif starts(cmd,"computer"):
            pass
        elif starts(cmd,"level"):
            pass
        elif starts(cmd,"hard"):
            pass
        elif starts(cmd,"time"):
            pass
        elif starts(cmd,"otim"):
            pass            
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
            #put_error("result","not implemented")
            engineColor = None
        elif starts(cmd,"setboard"):
            put_error("setboard","not implemented")
        elif cmd=="dummy":
            pass
        else:
            put_error(cmd,"unrecognized command")
        cmd = get()
 
def new():
# Reset the board to the standard chess starting position. Set White 
# on move. Leave force mode and set the engine to play Black. 
# Associate the engine's clock with Black and the opponent's clock 
# with White. Reset clocks and time controls to the start of a new 
# game. Stop clocks. Do not ponder on this move, even if pondering is 
# on. Remove any search depth limit previously set by the sd command.
    global engineColor
    stopClocks()
    board.reset()
    engineColor = 'black'
    
def force():
#Set the engine to play neither color ("force mode"). Stop clocks. 
# The engine should check that moves received in force mode are 
# legal and made in the proper turn, but should not think, ponder, or 
# make moves of its own. 
    global engineColor
    engineColor = None
    stopClocks()

def go():
#Leave force mode and set the engine to play the color that is on
# move. Associate the engine's clock with the color that is 
# on move, the opponent's clock with the color that is not on move.
# Start the engine's clock. Start thinking and eventually make a move.
    global engineColor
    assert engineColor == None
    engineColor = board.colorToMove()
    assert engineColor in ['white','black']
    time.sleep(1)
    reply()

def usermove(cmd):
# By default, moves are sent to the engine without a command name; 
# the notation is just sent as a line by itself. Beginning in protocol 
# version 2, you can use the feature command to cause the command 
# name "usermove" to be sent before the move. Example: "usermove 
# e2e4".
    assert engineColor in ['black','white',None]
    if board.colorToMove()==engineColor:
        put_error(cmd,"out of turn move ignored")
    else:
        mvstring = cmd.split(" ")[1]
        opponent_move(mvstring)
    
def opponent_move(s):
    assert engineColor in ['white','black',None]
    assert board.colorToMove()!=engineColor
    mvs = legal.moves()
    found = algebraic.find(s,mvs)
    if len(found)==0:
        put_illegalmove(s,"not found")
    elif len(found)==1:
        assert board.colorToMove()!=engineColor
        assert move.color(found[0])!=engineColor
        move.make(found[0])
        if board.colorToMove()==engineColor:
            assert board.colorToMove()==engineColor
            reply() 
    elif len(found)>1:
        put_illegalmove(s,"ambiguous")

def reply():
    #if not board.colorToMove()==engineColor:
    #    return None
    assert board.colorToMove()==engineColor
    mvs = legal.moves()
    #time.sleep(0.1)
    if len(mvs)>0:
        if len(board.history)>300:
            resign()
        else:
            mv,score,cnt,sec = alphabeta.best(mvs)
            s = san.pr(mv,mvs)
            put_move(s)
            move.make(mv)
    else: 
        assert len(mvs)==0
        report_result()             
        
def resign():
    global engineColor
    if engineColor=='white':
        put_result("0-1","white resigns")
    else:
        put_result("1-0","black resigns")
    engineColor==None
        
def report_result():
    assert len(legal.moves())==0
    if board.whiteToMove():
        if blackAttacks(board.whiteKingAt):
            put_result("1-0","black mates")
        else:
            put_result("1/2-1/2","stalemate")
    else:
        assert board.blackToMove()
        if whiteAttacks(board.blackKingAt):
            put_result("0-1","white mates")
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
