$Id: README.txt 7 2010-01-13 12:16:47Z mark $

Chess: An Exercise in Programming

I. Goals

This program started as an exercise in programming and a way for me to learn a 
bit of python.  I've tried my hand at writing chess programs on and off since I 
was 18.  I want to stretch my ability to  manage the complexity of the problem 
to arrive at a "good" solution.

By "good" I have some specific design goals in mind:

1)  A concise program that is easy to understand 
2)  The program should support a narrative that explains how I arrived at it 
3)  I should be the centerpiece for a short book on writing chess programs
4)  It should promote programming concepts worthy of attention
5)  It should be a jumping off point for more capable programs 
6)  It should play as well as my nieces and nephews
7)  It should be compatible with standards such as PGN and the ICC's chess protocols

The program should have some practical utility aside from teaching programming 
and providing a forum for me to pontificate on pet programming ideas.  I 
would like to be able to use it as a front end for playing back over my own 
chess games.  Just about all of the games I play on ICC are stored in files on 
my computer in PGN notation. I currently play them back through ChessBase and it 
quite powerful.  But it would be fun to use a player that I have more control 
over and could tweak to my tastes.  I have has some problems with ChessBase that 
I have never been able to iron out to my satisfaction.  (E.g. It forgets all of 
my annotations whenever I am using PGN as my game notation format.)  If I had a 
player of my own, I should be able to fix such problems.

Strong move seach and playing ability is not the sole measure of a chess 
program. But the ability to recognize legal moves and stop the users from 
corrupting the score by entering illegal moves has a great deal of utility.  A 
program that can do that, even if it plays poorly, can be the core of a useful 
chess appliance to record and view games, act a front end to services such as 
ICC, act as an editor for analysing and annotating your own games.  I could see 
it acting as a plug-in extension to an open source text editor extending it to 
edit chess articles.

II. Layers

I intend for the structure to be strictly heirarchical.  Lower level
modules know nothing about any higher level modules.  More formally, you
don't need to know anything about layer n+1 to understand layer n.

I started with the following outline of what functionality to put in each layer.

Layer 0:  squares  - the squares of the chessboard, ranks, files, etc.
Layer 1:  men      -- existence of King, Queen, ... Pawn, colors White and Black
Layer 2:  board    -- mapping of men to squares on the board & vice versa
Layer 3:  move     -- movement of men on the board
Layer 4:  legal    -- generation of legal moves
Layer 6:  seval    -- static evaluation of positions (how good/bad)
Layer 7:  search   -- tree search for good continuations, & best move selection

After I wrote python code for a few of the lower layers, I noticed that things 
in higher layers don't necessarily depend on things lower down.  For example, 
men does not refer to squares at all.  They are independent.  Neither makes 
assumptions about the other.

III. Test Vehicle

I also decided to develop the program concurrently with a test program that 
would exercise the components as they were being developed.  That way I would 
continually test and build.  The approach has been effective in the past.  Here 
it was all the more imporant in that I was new to python and likly to make 
mistakes due to a limited understanding as to what the language primitives 
really meant in all cases.  This should allow me to catch mistakes of 
interpretation early and correct my understanding of the language.  Of course, 
it would help me correct outright programming blunders as well.

IV. Efficiency

Programming in python is quick, but you pay for it in computational speed.  For 
many applications the speed is more adequate, but chess is not such an 
application.  Chess programs performing move search typically strains the 
capabilities of the fastest computers.  Even machine coded programs on small 
devices such as palm pilots play a very weak game of chess.  My earlier java 
based chess programs had proven quite weak due mainly to inefficient use of 
machine cycles for extensive tree searchs.  I expect to hit this same wall with
python.

Though I mentioned earlier that playing strength is not the sole measure of a 
chess program, we need not ingore the issue completely.

The mitigating strategy here is to write the program in such a way that all or 
parts of it can be re-implemented in other more efficient languges, such as C or 
C++.  It may even be desirable to rewrite parts of the C code in assembly language.

Another possibility would be to make the program a wrapper for more efficient 
and well proven chess engines such as Fritz and Crafty.  These engines are 
available on the web and communicate with chess front ends with reasonable 
standardized protocols.  So, our program would be more flexible if we took these 
interfaces into account in our architecture.  We should be able to "unplug" our 
chess engine and plug in one of these more powerful engines.  This would give us
a toolkit where we can mix and match chess engines and chess interfaces.

Finally we should not ignore how far we can go in writing efficient code in 
python. If we pay attention to the asymptotic efficiency of our code, e.g. use 
O(n log n) instead of O(n-squared) algorithms, minimize garbage collection, take 
some timings to find efficient ways to use hash tables, sets, and other data 
structures provided we might be able to get squeeze out something good enough to 
be useful before hitting the wall on performance.

V.  False Starts

Over the course of writing the program, I made some mistakes and had to backtrack
to correct them.  Here are some notes.

  A. Castling.

Initially I though I could represent ability to castle with two boolean flags,
whiteCastled, and blackCastled.   If you castled once, you won't  be able to
castle again. 

But the rules are different for castling kingsize and castling queenside.  So I
broke it into 4 variables:

whiteAllowOO, whiteAllowOOO, blackAllowOO, blackAllow000 to cover 4 cases.

They start out all true and you maintain them by noting any castling moves or
moves made by the king or rook that affect castling.  That is easy enough to do
when making moves, but you need to know a bit when unmaking moves.  Our representation
needs to handle undoing moves and restoring these flags to their former settings.
How will we choose to support that.  Several options were considered.

a) Save the old flags in each move made, that way we can always restore them.  Same
   as how we record any piece captured.
   
b) Save the old flags in a separate stack in parallel with the moves.  Not very different
   from a, but keeps moves a bit more compact.
   
c) Record for each king and each rook, the move number of the first time it moved.  When
   moving backward, you know the move number, so you can reset it as needed.
   
Tough call.  (a) and (b) might create a bit more garbage collection, but are simple to
reason about.  (c) does things in very little space, but complicates the logic just
bit since we have to compare numbers and do some logic to set the values for our 4 flags.

Let us consider alternative (c).  The idea of constant space seems fundamentally right.
All the information we might push the stack can be boiled down to just
pointers into the stack.  Everything below the pointer has one value, everything above
has another.  When you know the pointers, you don't need to store the stack anymore.

So we keep a dictionary firstmv[sq] to remember the number of the first move
origination from sq for sq in [a1,e1,h1,a8,e8,h8].  We initialize these to None,
at the beginning of the game and let move.make and move.umake maintain them.

E.g. 

init_first():
    first = {}
    if sq in [a1,e1,h1,a8,e8,h8]:
        firstmv[sq] = None

So moving forward, move.make will include calls to something like
        
def remember_if_first(sq,n):
    if sq in [a1,e1,h1,a8,e8,h8] and firstmv[sq]==None:
        firstmv[sq] = n

and moving backware, move.umake will include calls to something like
        
def forget_if_first(sq,n):
    if sq in [a1,e1,h1,a8,e8,h8] and firstmv[sq]==n:
        firstmv[sq] = None

These have a nice property that we can verify them from time to time by doing a
search of the move history.  They essentially cache information that could be obtained
by searching the history list anytime.  Periodic consistency checks could help ensure
we got things right in our programming.

Now we can define

def whiteAllowOO():
    return firstmv[e1]==None and firstmv[h1]==None

def whiteAllowOOO():
    return firstmv[e1]==None and firstmv[a1]==None
    
def blackAllowOO():
    return firstmv[e8]==None and firstmv[h8]==None

def blackAllowOOO():
    return firstmv[e8]==None and firstmv[a8]==None

But all this function call overhead worries me.  Is there some trick to pack this
info into a single number that is fast to compute with.

A 32 bit integer breaks down into 4 8-bit integers.  8-bit integers can represent values
up to 255.  Only rare chess games would not move a king or rook after 255 moves, but it 
could happen.  Lets' put aside the rare case to consider separately later.  So, we
could try packing all this into a single integer.  Rather go down this bit twiddling
path, let us stay with the main line above.  There will be plenty of time for optimization
later.  

It does irk me a bit how much exta logic got shoved into the program to support constant
space.  There are a lot of compares in there eating up cycles.  The searches on the 6
squares are particularly ugly.  We could eliminate this by recoding first moves from
every square.  More storage, but it eliminates lots of compares.

init_first():
    first = {}
    if sq in xrange(0,64):
        firstmv[sq] = None
        
def remember_if_first(sq,n):
    if firstmv[sq]==None:
        firstmv[sq] = n
        
def forget_if_first(sq,n):
    if firstmv[sq]==n:
        firstmv[sq] = None

I am guessing it is cheaper to set a single dictionary element than to compare against
6 elements of the list unnecessarily.  This troubles me, I am only guessing.  Need real
performance data to know if this is win or not.  It may even slow things down.  There are
so many ways to implement interpreters, it is silly to guess what is under the hood.

Perhaps (b) could do the job with fewer compares.

In this alternative, we just shove a 4-tuple on the stack each move.  Unmoving just
pops them off.  What could be simpler?

def pushFlags():
    flags.append((whiteAllowOO, whiteAllowOOO, blackAllowOO, blackAllowOOO))

def popFlags():
    whiteAllow00, whiteAllowOOO, blackAllowOO, blackAllowOOO = flags.pop()
    
You must admit, this reads alot cleaner that all the machinations we did for (a)
    
I'm sold.  I have to go with (b).  The clarity is too compelling.


VI. The Mediator

We need something to mediate between the chess engine and things that
will use the chess engine.  The idea here is that the chess just focuses in
on knowing the position on the board, generating legal moves, knowing who has
castled, enforcing the rules of the game.  Some outside entity will be
responsible for interacting with the user via gui, a chess protocol, or a web
interface.  There may be several mediators in fact depending on what we need
to interact with, e.g. WinBoard/XBoard, UCP, or our own custom built GUI.
The mediator might also handle the importing and exporting of games as
PGN files.  We lump all this together and call it mediation.

Here is a list of things the mediator needs to do:

   setup a new game
   determine who the players are (computer, human, etc.)
   display the position to the player
   get moves from the player/gui
   enforce the rules preventing player from making illegal moves
   indicate the computer's moves to the player
   allow the player to set game parameters, such as search depth
   maintain or interact with a chess clock
   save out an adjourned position externally
   load an ajourned position from outside
   pause a game
   resume a game
   
The above list just has to do with playing a full game.  Sometimes
it is helpful to play from a given position without knowing the full
game.  E.g. chess problems, or study positions.

   the ability to setup an arbitrary intial position
   play from the arbitrary position
   arbitrary setup includes values of flags, color to move

Also it would be helpful if many chess engines could be used in
parallel.  Thus an engine might just take a full position and
calculate a best move, returning the move back to the coordinator.
Also the chess engine generate new positions for the coordinator
to assign to other engines, and then incorporate answers into it's
own searches.  Want this to scale to thousands of hosts over the
internet via http messages.

    A.  A simple mediator for a custom GUI
  
        1. Custom GUI      
            a. Operates as a separate process/thread from the engine
            
            b. Communicate with engine via messages
            
            c. Displays board to user, user clicks on squares or
               drags pieces over the squares.  Easy to get (osq,nsq)
               pairs.  Can interpret OO and OOO from that easily.
               may need to prompt for promotion information.
               
            d. Does not know about legality, waits for confirmation
               from engine before actally moving the piece on the
               display.
          
        2. Messages from GUI  -- a stream of tokens
        
            a. 'NewGame'
                 command to start a new game, engine will prepare
                 itself and setup a new board.

            b. 'YouPlay' ['black'|'white']

            c. 'BeginPlay'
            
            d. {a-g}{1-9}{a-g}{1-6}[/Q|/R|/B|/N}]

                 a 4 character message giving old square and new square
                 the engine is expected to use this to lookup
                 the legal move associated with this info.
                 
                 the last part is only sent for pawn promotions.
                 
                 Examples
                 
                    e2e4
                    g8f6
                    a7a8/Q

            g. 'SaveGame'
            h. 'ResumeGame'
            i. 'SavedGameList'
                 
        3.  Messages from the engine to the gui
        
            The philosophy here is to keep the GUI as dumb as possible.
            
            We also want the state of the engine as transparent as possible.
            We make this simple by sending the GUI the entire position each
            time the computer moves.  If the internal board gets corrupted
            then we stand a good chance of seeing it.  The GUI will be pretty
            much stateless from one move to the next.  It gets the whole state
            of the game from the engine each half move.
                       
            The messages are designed to look like
            the display on the screen so it can be read easily if you are 
            monitoring the traffic or reading the logs.
            
            a. Board
               <8 lines of diagram showing the board position>
            
            Example
            
            Board
            BR BN BB BQ BK BB BN BR
            BP BP BP BP BP BP BP BP
            -- -- -- -- -- -- -- --
            -- -- -- -- -- -- -- --
            -- -- -- -- -- -- -- --
            -- -- -- -- -- -- -- --
            WP WP WP WP WP WP WP WP
            WR WN WB WQ WK WB WN WR
            
            b. Messages that say whose move it is
            
               WhiteToMove
               BlackToMove
            
            c. Messages that indicate the outcome of the game
            
               WhiteWins
               BlackWins
               DrawAgreed
               DrawByStalemate
               DrawByRepetition
            
            d. Messages that tell us a move has been rejected            
               CannotMoveThere
               NotYourMove

VII.  Algebraic Notation

    A. Take a look at PGN

    Examples

     e4   e5  O-O   Nf3  exd5(ep)  exd5  e8(Q)  Pxe8/N  Qa5+  e8(Q)++
     Ke3=  resign
     
    All the above need a context of a position including the side to move...
    Then they can locate the move in the list of legal moves for that position.
    
    We can add some redundancy by "clothing" the moves to indicate the move
    number and the side to move.
    
     1 e4        {white moves} 
     1 ...e5     {black moves}
    
     4 O-O       {white castles on 4th move}
     
     We can combine several moves in PGN style
     
     1 e4 e5 2 Nf3 Nc3 3 Bb5
     
    B.  A clever implementation
    
    After playing around for a few hours looking for a clean implementation
    of algebraic notation, I came up with a nice clean implementation based
    on pattern tempates.  It gives the most readable code.

    See algebraic.py

-----------------------------------------------------------------------------
Notes on the June 9, 2006 Version

1.  Drafted FEN to save/restore positions.  This creates issues because we
have not considered how to represent positions whose history does not start
at the beginning of the game.  I've been using len(history) a good deal to
compute the move number, half move count, etc.  Need to think on best way
to deal with games whose history picks up in the middle of the game.

Some alternatives:

a) Instead of len(history) look at the half move number in the history itself.
There is an invariant:
   assert h == len(board.history)
where h is the half move count, that is used a lot in trial.py.  This would
all have to be revised.

b) We could pad the start of the history with dummy moves.  Perhaps allocate
some move tag to represent unknown move. 


2. Would like to display the preferred line along with the scores.

Instrument alphabeta to record the move and pass it up during the search.
Like a synthesised attribute in compiler writing.  Just record the raw move
and don't convert it to san until after we have the whole line.  This keeps
us from slowing things down by pounding too hard on our (rather slow) SAN move
translator.  We are throwing alway all but one line anyway.  It would be
waste to format hundreds to thousands of lines we never going to display.
 
3. Profiling and Instrumentaiton

Would like some profiling or instrumentation to measure how much time we
are spending in searching or in static analysis.  I have a sense that static
analysis is slowing us down, but I can't tell how much.

4. Packaging up positions

Another way of sending positions around (an aternative to FEN) is to send
the whole move history.  From this all the other details can be reconstructed
simply enough.  If versions of this program are chatting between themselves
they can all interpret this pretty trivially.  Inspires me write some module
to import and export positions as history.

5. Distributed move evaluation.  

A coordinator module would enable different chess agents to share the load
of evaluating positions.  Engine agents would register with the coordinator.
Coordinator would take a list of positions to be evaluated and deal them out
to available engine agents, and await a reply on a separate thread for each
agent.  When reply came back, agent would be added to the pool of available
agents.  Agents should be stateless in that they get the whole position to
evaluate each time, they don't remember it from context.  This allows agents
to be used for different games out of the same waiting pool.

Expect we could do all this in python.  This would mediate the problem of 
interpeted python, by just throwing more processors at the problem.  Take 
advantage of inherent massive parallelism in the problem.
 
6. Human Economics

Allow people to run chess agents on their own machines.  They join the chess
agent community.  In return for donating machine cycles and keeping agents
up, they are allowed to play chess against the engine.  So many cycles/moves
in return for play.

7. Security Challenges

Lots of security challenges.  Byzantine community.  Keep people from cheating.
Send them the source to run on their own machines.  They can change the source.
Distributed accounting.  Who accounts for the time used, resources allowed.
Authentication -- how do we know we are talking to the real entity.

Play pen for security architectures, algorithms, protocols, tricks.  Like distributed
poker.

8. Bitboard

Look at article on Bitboard and think about how to incorporate.  Should strenghen
ability to write fast static evaluation.

9. Tanspostion Tables

This might be a useful speedup to incorporate.  Read up and understand this.

10.  Look at some simple pre-processing for move generation.

11.  Need a set of benchmarks to measure how well we are doing.

For move generation
    moves generated per second
    random play
    
For static evaluation
    put timers in static eval
    number of positions evaluated    
    measure milliseconds per position

12.  Incorporate an Opening Book

This can be a side effect of including a transposition table.  

13.  Look at itterative deepening.

14.  Look at null move heuristic  (can save 25-75% of search)

15.  Aspirated Search

16.  MDT(f)


-----------------------------------------------------------------------------
Sunday June 11, 2006

Notes from self play using main.py.  This time used a pretty elaborate version
of static.py.

def eval():
    mvs = legal.moves()
    s = legal.state(mvs)
    assert s in ['whiteMates','blackMates','stalemate','continue']
    if s=='whiteMates':
        return +inf   # black has been mated
    elif s=='blackMates':
        return -inf   # white has been mated
    elif s=='stalemate':
        return 0
    else:
        assert s=='continue'
        m = wmaterial() + bmaterial()
        c = wcenter()   + bcenter()
        p = wpenalty()  + bpenalty()
        b = wbonus()    + bbonus()
        #k = wkingsafety() + bkingsafety()
        #print "58: k=%s m=%s eval=%s" % (k,m,k+m)
        return m + c + p + b
        
It is also important to know what the search parameters were:

depth1 = 2   # primary cutoff ~ full width
depth2 = -6  # secondary cutoff (negative) ~ captures only

This means we look at every move for 2 ply.  After 2 play, we keep looking
up to a maximum of 6 more ply only looking at captures.  This means we will
look at a maximum of 8 ply.
    
        
Note that I do have code in now to detect mates and stalemates.  Last time
I ran a self play, the computer actually found the mates.  Before it had
been looping just repreating positions, since it only looked at material.
Mate does not actually win any material, so it didn't stand out!

The output from a game in progress follows.  This is a listing of the
computer playing itself.  I have a text printout of the board position
followed by the analysis of each move the computer evaluated from that
position.  The first number is the score of the move, followed by the
number of positions looked at.  That is followed by the line considered
best by the computer in it's minimax search.  This is the line responsible
for the score for the first move in that line and represents what the
computer thinks is the best line based on it's evaluation of the the
final position in that line.



mark@kai ~
$ cd chess

mark@kai ~/chess
$ ./main.py
-----------------------
BR BN BB BQ BK BB BN BR
BP BP BP BP BP BP BP BP
-- -- -- -- -- -- -- --
-- -- -- -- -- -- -- --
-- -- -- -- -- -- -- --
-- -- -- -- -- -- -- --
WP WP WP WP WP WP WP WP
WR WN WB WQ WK WB WN WR
-----------------------
white to move
> hammer
started Wed Dec 31 19:00:00 1969
   150     23  1 Nc3 b5 2 Nxb5
   150     21  1 Na3 b5 2 Nxb5
   150     21  1 Nh3 g5 2 Nxg5
   150     22  1 Nf3 g5 2 Nxg5
   130     21  1 a4 b5 2 axb5
    30     20  1 a3 a5
   111     23  1 b4 c5 2 bxc5
    30     20  1 b3 a5
   149     23  1 c4 b5 2 cxb5
    49     20  1 c3 a5
   174     29  1 d4 g5 2 Bxg5
   164     27  1 d3 g5 2 Bxg5
   174     32  1 e4 b5 2 Bxb5
   164     29  1 e3 b5 2 Bxb5
   130     22  1 f4 g5 2 fxg5
    30     20  1 f3 a5
   130     23  1 g4 f5 2 gxf5
    30     20  1 g3 a5
   130     21  1 h4 g5 2 hxg5
    30     20  1 h3 a5
After 1 d4 [174] searched 477 positions in 14.37 sec

-------------
As I look at this the first line just looks wrong.  I don't think
black will play the line

1 Nc3 b5 Nxb5

It looks like the algorithm is confused.  White seems to think that
black is trying to loose.  This looks like an error coding the algorithm.
Time to fiddle some.

I think I fixed an error in the algorithm.  Then I changed the bounds on
the alpha-beta from -inf,+inf to -400,+400 to see the difference.  I got 
this:

mark@kai ~/chess
$ ./main.py
-----------------------
BR BN BB BQ BK BB BN BR
BP BP BP BP BP BP BP BP
-- -- -- -- -- -- -- --
-- -- -- -- -- -- -- --
-- -- -- -- -- -- -- --
-- -- -- -- -- -- -- --
WP WP WP WP WP WP WP WP
WR WN WB WQ WK WB WN WR
-----------------------
white to move
>
  -169     23  1 Nc3 d5 2 Nxd5 Qxd5
     4     21  1 Na3 c5
     4     21  1 Nh3 c5
    21     22  1 Nf3 c5
     1     21  1 a4 c5
     1     20  1 a3 c5
     1     23  1 b4 d5
     1     20  1 b3 c5
    30     23  1 c4 c5
    20     20  1 c3 c5
  -154     29  1 d4 h6 2 Bxh6 Nxh6   <---- it thinks that captures are forced!
  -164     27  1 d3 h6 2 Bxh6 Nxh6
  -741     32  1 e4 h5 2 Qxh5 Rxh5
  -751     29  1 e3 h5 2 Qxh5 Rxh5
     1     22  1 f4 c5
     1     20  1 f3 c5
     1     23  1 g4 c5
     1     20  1 g3 c5
     1     21  1 h4 c5
     1     20  1 h3 c5
After 1 c4 [30] searched 477 positions in 13.99 sec
-----------------------
BR BN BB BQ BK BB BN BR
BP BP BP BP BP BP BP BP
-- -- -- -- -- -- -- --
-- -- -- -- -- -- -- --
-- -- WP -- -- -- -- --
-- -- -- -- -- -- -- --
WP WP -- WP WP WP WP WP
WR WN WB WQ WK WB WN WR
-----------------------
black to move
> hammer
started Wed Dec 31 19:00:14 1969
    88     23  1 ...a5 2 d4
    88     22  1 ...a6 2 d4
   149     60  1 ...b5 2 cxb5
    88     23  1 ...b6 2 d4
    59     24  1 ...c5 2 d4 cxd4 3 Qxd4
    69     22  1 ...c6 2 d4
   903     86  1 ...d5 2 e3 dxc4 3 Bxc4 Qxd2 4 Nxd2
   238     30  1 ...d6 2 h3 Bxh3 3 Nxh3
   830     35  1 ...e5 2 h4 Qxh4 3 Rxh4
   840     32  1 ...e6 2 h4 Qxh4 3 Rxh4
    88     24  1 ...f5 2 d4
    88     22  1 ...f6 2 d4
    88     25  1 ...g5 2 d4
    88     22  1 ...g6 2 d4
    88     23  1 ...h5 2 d4
    88     22  1 ...h6 2 d4
   258     25  1 ...Nc6 2 d4 Nxd4 3 Qxd4
    85     24  1 ...Na6 2 d4
    85     23  1 ...Nh6 2 d4
    68     24  1 ...Nf6 2 d4
After 1 ...c5 [59] searched 611 positions in 17.104 sec
-----------------------
BR BN BB BQ BK BB BN BR
BP BP -- BP BP BP BP BP
-- -- -- -- -- -- -- --
-- -- BP -- -- -- -- --
-- -- WP -- -- -- -- --
-- -- -- -- -- -- -- --
WP WP -- WP WP WP WP WP
WR WN WB WQ WK WB WN WR
-----------------------
white to move
    21     25  2 Nc3 e5
     4     24  2 Na3 d5 3 cxd5 Qxd5
  -799    115  2 Qc2 e5 3 Qxh7 Rxh7
  -814    103  2 Qb3 e5 3 Qxb7 Bxb7
  -799     84  2 Qa4 e5 3 Qxa7 Rxa7
     4     28  2 Nh3 d5 3 cxd5 Qxd5
    21     26  2 Nf3 d5 3 cxd5 Qxd5
     1     24  2 a4 d5 3 cxd5 Qxd5
     1     24  2 a3 d5 3 cxd5 Qxd5
   -60     61  2 b4 cxb4
     1     24  2 b3 d5 3 cxd5 Qxd5
  -814    161  2 d4 e6 3 dxc5 Bxc5 4 Qxd7 Nxd7
  -164     31  2 d3 h6 3 Bxh6 Nxh6
  -741     28  2 e4 h5 3 Qxh5 Rxh5
  -751     26  2 e3 h5 3 Qxh5 Rxh5
     1     26  2 f4 d5 3 cxd5 Qxd5
     1     24  2 f3 d5 3 cxd5 Qxd5
   -14     28  2 g4 d5 3 cxd5 Bxg4
     1     24  2 g3 d5 3 cxd5 Qxd5
     1     25  2 h4 d5 3 cxd5 Qxd5
     1     27  2 h3 d5 3 cxd5 Qxd5
After 2 Nc3 [21] searched 959 positions in 24.546 sec
-----------------------
BR BN BB BQ BK BB BN BR
BP BP -- BP BP BP BP BP
-- -- -- -- -- -- -- --
-- -- BP -- -- -- -- --
-- -- WP -- -- -- -- --
-- -- WN -- -- -- -- --
WP WP -- WP WP WP WP WP
WR -- WB WQ WK WB WN WR
-----------------------
black to move
    79     28  2 ...a5 3 d4 cxd4 4 Qxd4
   240     32  2 ...a6 3 Nb5 axb5 4 cxb5 Rxa2 5 Rxa2
   150     70  2 ...b5 3 Nxb5
    79     28  2 ...b6 3 d4 cxd4 4 Qxd4
   921    119  2 ...d5 3 cxd5 Qxd5 4 Nxd5
   229     35  2 ...d6 3 h3 Bxh3 4 Nxh3
   821     32  2 ...e5 3 h4 Qxh4 4 Rxh4
   831     32  2 ...e6 3 h4 Qxh4 4 Rxh4
    79     32  2 ...f5 3 d4 cxd4 4 Qxd4
    79     28  2 ...f6 3 d4 cxd4 4 Qxd4
    79     46  2 ...g5 3 d4 cxd4 4 Qxd4
    79     28  2 ...g6 3 d4 cxd4 4 Qxd4
    79     29  2 ...h5 3 d4 cxd4 4 Qxd4
    79     46  2 ...h6 3 d4 cxd4 4 Qxd4
    59     29  2 ...Nc6 3 e4
    76     28  2 ...Na6 3 d4 cxd4 4 Qxd4
   879    304  2 ...Qc7 3 e4 Qxh2 4 Rxh2
   894    145  2 ...Qb6 3 e4 Qxb2 4 Bxb2
   850    441  2 ...Qa5 3 Nd5 Qxa2 4 Rxa2
    76     47  2 ...Nh6 3 d4 cxd4 4 Qxd4
   249     34  2 ...Nf6 3 e4 Nxe4 4 Nxe4
After 2 ...Nc6 [59] searched 1634 positions in 41.77 sec
-----------------------
BR -- BB BQ BK BB BN BR
BP BP -- BP BP BP BP BP
-- -- BN -- -- -- -- --
-- -- BP -- -- -- -- --
-- -- WP -- -- -- -- --
-- -- WN -- -- -- -- --
WP WP -- WP WP WP WP WP
WR -- WB WQ WK WB WN WR
-----------------------
white to move
     1     29  3 Rb1 e5
  -799    164  3 Qc2 e5 4 Qxh7 Rxh7
  -814    190  3 Qb3 e5 4 Qxb7 Bxb7
  -770    184  3 Qa4 Ne5 4 Qxa7 Rxa7
     4     36  3 Nh3 e5
  -169     35  3 Nf3 e5 4 Nxe5 Nxe5
     1     29  3 a4 e5
  -160     41  3 a3 Nb4 4 axb4 cxb4 5 Rxa7 Rxa7
   -70    135  3 b4 Nxb4
     1     29  3 b3 e5
  -841    328  3 d4 cxd4 4 Qxd4 Nxd4
  -164     36  3 d3 h6 4 Bxh6 Nxh6
  -741     32  3 e4 h5 4 Qxh5 Rxh5
  -751     33  3 e3 h5 4 Qxh5 Rxh5
    10     33  3 f4 Nf6
     1     29  3 f3 e5
     1    105  3 g4 e5
     1     29  3 g3 e5
     1     30  3 h4 e5
     1     35  3 h3 e5
  -228    278  3 Nd5 d6 4 Nxe7 Ngxe7
  -204    149  3 Ne4 e5 4 Nxc5 Bxc5
   -19     28  3 Nb1 d5 4 cxd5 Qxd5
  -204    152  3 Na4 e5 4 Nxc5 Bxc5
  -199    194  3 Nb5 d5 4 cxd5 Qxd5 5 Nxa7 Rxa7
After 3 f4 [10] searched 2388 positions in 62.75 sec
-----------------------
BR -- BB BQ BK BB BN BR
BP BP -- BP BP BP BP BP
-- -- BN -- -- -- -- --
-- -- BP -- -- -- -- --
-- -- WP -- -- WP -- --
-- -- WN -- -- -- -- --
WP WP -- WP WP -- WP WP
WR -- WB WQ WK WB WN WR
-----------------------
black to move
   330    282  3 ...Ne5 4 fxe5
   288    303  3 ...Nd4 4 d3 Nxe2 5 Ngxe2
   259    405  3 ...Nb4 4 d4 Nxa2 5 Rxa2 cxd4 6 Qxd4
   264    282  3 ...Na5 4 e4 Nxc4 5 Bxc4
    79     28  3 ...Nb8 4 d4 cxd4 5 Qxd4
    59     29  3 ...a5 4 e4
   220     41  3 ...a6 4 Nb5 axb5 5 cxb5 Rxa2 6 Rxa2
   130     68  3 ...b5 4 Nxb5
    59     29  3 ...b6 4 e4
   901    137  3 ...d5 4 cxd5 Qxd5 5 Nxd5
   209     37  3 ...d6 4 h3 Bxh3 5 Nxh3
    45     98  3 ...e5 4 d3 exf4 5 Bxf4
   811     34  3 ...e6 4 h4 Qxh4 5 Rxh4
    50     32  3 ...f5 4 Nf3
    59     29  3 ...f6 4 e4
   130     98  3 ...g5 4 fxg5
    59     30  3 ...g6 4 e4
    59     30  3 ...h5 4 e4
    59     29  3 ...h6 4 e4
    59     29  3 ...Rb8 4 e4
   864     88  3 ...Qc7 4 d3 Qxf4 5 Bxf4
   874    147  3 ...Qb6 4 e4 Qxb2 5 Bxb2
   830    421  3 ...Qa5 4 Nd5 Qxa2 5 Rxa2
    56     31  3 ...Nh6 4 e4
   229     35  3 ...Nf6 4 e4 Nxe4 5 Nxe4
After 3 ...e5 [45] searched 2797 positions in 74.247 sec
-----------------------
BR -- BB BQ BK BB BN BR
BP BP -- BP -- BP BP BP
-- -- BN -- -- -- -- --
-- -- BP -- BP -- -- --
-- -- WP -- -- WP -- --
-- -- WN -- -- -- -- --
WP WP -- WP WP -- WP WP
WR -- WB WQ WK WB WN WR
-----------------------
white to move
    11     68  4 fxe5 Nxe5
   -89    132  4 Rb1 exf4
  -889    494  4 Qc2 exf4 5 Qxh7 Rxh7
  -904    426  4 Qb3 exf4 5 Qxb7 Bxb7
  -708    848  4 Qa4 exf4 5 Qxc6 dxc6
   -89    123  4 Kf2 exf4
   -15    150  4 Nh3 d6 5 fxe5 dxe5
  -188    251  4 Nf3 d6 5 Nxe5 dxe5 6 fxe5 Nxe5
   -89    135  4 a4 exf4
   -89    170  4 a3 exf4
 -1094    435  4 b4 cxb4 5 fxe5 bxc3 6 dxc3 Nxe5 7 Qxd7 Bxd7
  -204    141  4 b3 Qa5 5 fxe5 Qxc3 6 dxc3 Nxe5 7 Qxd7 Bxd7
  -870    653  4 d4 exd4 5 Qxd4 Nxd4
  -183    150  4 d3 h6 5 fxe5 Nxe5 6 Bxh6 Nxh6
  -760    150  4 e4 h5 5 Qxh5 Rxh5 6 fxe5 Rxe5
  -770    153  4 e3 h5 5 Qxh5 Rxh5 6 fxe5 Rxe5
-2147483627    163  4 g4 Qh4
   -18    125  4 g3 d6 5 fxe5 dxe5
  -194    276  4 h4 Be7 5 fxe5 Bxh4 6 Rxh4 Nxe5 7 Rxh7 Rxh7
   -89    149  4 h3 exf4
  -209    205  4 Nd5 f6 5 fxe5 Nxe5 6 Nxf6 Nxf6
  -294    570  4 Ne4 exf4 5 Nxc5 Bxc5
  -109    134  4 Nb1 exf4
  -294    665  4 Na4 exf4 5 Nxc5 Bxc5
  -289    419  4 Nb5 exf4 5 Nxa7 Rxa7
   -19     56  4 f5 Nf6
After 4 fxe5 [11] searched 7267 positions in 189.562 sec
-----------------------
BR -- BB BQ BK BB BN BR
BP BP -- BP -- BP BP BP
-- -- BN -- -- -- -- --
-- -- BP -- WP -- -- --
-- -- WP -- -- -- -- --
-- -- WN -- -- -- -- --
WP WP -- WP WP -- WP WP
WR -- WB WQ WK WB WN WR
-----------------------
black to move
   245    275  4 ...Nxe5 5 e4 Nxc4 6 Bxc4
   140     31  4 ...Nce7 5 d4 cxd4 6 Qxd4
  1150    251  4 ...Nd4 5 h4 Nxe2 6 Ngxe2 Qxh4 7 Rxh4
  1111    422  4 ...Nb4 5 h4 Nxa2 6 Rxa2 Qxh4 7 Rxh4
   345    195  4 ...Na5 5 e4 Nxc4 6 Bxc4
   931     31  4 ...Nb8 5 h4 Qxh4 6 Rxh4
   331    179  4 ...a5 5 Nf3 Nxe5 6 Nxe5
   331    201  4 ...a6 5 Nf3 Nxe5 6 Nxe5
   101    140  4 ...b5 5 cxb5 Nxe5
   331    234  4 ...b6 5 Nf3 Nxe5 6 Nxe5
    92    248  4 ...d5 5 Nxd5 Nxe5
    77    205  4 ...d6 5 exd6 Bxd6
   331    206  4 ...f5 5 Nf3 Nxe5 6 Nxe5
    91    263  4 ...f6 5 exf6 Nxf6
   331    356  4 ...g5 5 Nf3 Nxe5 6 Nxe5
   331    181  4 ...g6 5 Nf3 Nxe5 6 Nxe5
   331    233  4 ...h5 5 Nf3 Nxe5 6 Nxe5
   331    229  4 ...h6 5 Nf3 Nxe5 6 Nxe5
   716    206  4 ...Rb8 5 Qa4 Nxe5 6 Qxa7 Nxc4 7 Qxb8 Nxb2 8 Bxb2
6 moves played over 0 games
> Traceback (most recent call last):
  File "./main.py", line 280, in ?
    main()
  File "./main.py", line 68, in main
    line = raw_input(prompt)
KeyboardInterrupt

mark@kai ~/chess
$ ./main.py
-----------------------
BR BN BB BQ BK BB BN BR
BP BP BP BP BP BP BP BP
-- -- -- -- -- -- -- --
-- -- -- -- -- -- -- --
-- -- -- -- -- -- -- --
-- -- -- -- -- -- -- --
WP WP WP WP WP WP WP WP
WR WN WB WQ WK WB WN WR
-----------------------
white to move
> hammer
started Wed Dec 31 19:00:00 1969
  -169     23  1 Nc3 d5 2 Nxd5 Qxd5
     4     21  1 Na3 c5
     4     21  1 Nh3 c5
    21     22  1 Nf3 c5
     1     21  1 a4 c5
     1     20  1 a3 c5
     1     23  1 b4 d5
     1     20  1 b3 c5
    30     23  1 c4 c5
    20     20  1 c3 c5
  -154     29  1 d4 h6 2 Bxh6 Nxh6
  -164     27  1 d3 h6 2 Bxh6 Nxh6
  -400     25  1 e4 h5
  -400     22  1 e3 h5
     1     22  1 f4 c5
     1     20  1 f3 c5
     1     23  1 g4 c5
     1     20  1 g3 c5
     1     21  1 h4 c5
     1     20  1 h3 c5
After 1 c4 [30] searched 463 positions in 13.369 sec
-----------------------
BR BN BB BQ BK BB BN BR
BP BP BP BP BP BP BP BP
-- -- -- -- -- -- -- --
-- -- -- -- -- -- -- --
-- -- WP -- -- -- -- --
-- -- -- -- -- -- -- --
WP WP -- WP WP WP WP WP
WR WN WB WQ WK WB WN WR
-----------------------
black to move
    88     23  1 ...a5 2 d4
    88     22  1 ...a6 2 d4
   149     60  1 ...b5 2 cxb5
    88     23  1 ...b6 2 d4
    59     24  1 ...c5 2 d4 cxd4 3 Qxd4
    69     22  1 ...c6 2 d4
   400      9  1 ...d5 2 Na3
   238     30  1 ...d6 2 h3 Bxh3 3 Nxh3
   400     32  1 ...e5 2 h4
   400     29  1 ...e6 2 h4
    88     24  1 ...f5 2 d4
    88     22  1 ...f6 2 d4
    88     25  1 ...g5 2 d4
    88     22  1 ...g6 2 d4
    88     23  1 ...h5 2 d4
    88     22  1 ...h6 2 d4
   258     25  1 ...Nc6 2 d4 Nxd4 3 Qxd4
    85     24  1 ...Na6 2 d4
    85     23  1 ...Nh6 2 d4
    68     24  1 ...Nf6 2 d4
After 1 ...c5 [59] searched 528 positions in 14.661 sec
-----------------------
BR BN BB BQ BK BB BN BR
BP BP -- BP BP BP BP BP
-- -- -- -- -- -- -- --
-- -- BP -- -- -- -- --
-- -- WP -- -- -- -- --
-- -- -- -- -- -- -- --
WP WP -- WP WP WP WP WP
WR WN WB WQ WK WB WN WR
-----------------------
white to move
    21     25  2 Nc3 e5
     4     24  2 Na3 d5 3 cxd5 Qxd5
  -400      3  2 Qc2 a5
  -400      3  2 Qb3 a5
  -400      5  2 Qa4 a5
     4     28  2 Nh3 d5 3 cxd5 Qxd5
    21     26  2 Nf3 d5 3 cxd5 Qxd5
     1     24  2 a4 d5 3 cxd5 Qxd5
     1     24  2 a3 d5 3 cxd5 Qxd5
   -60     61  2 b4 cxb4
     1     24  2 b3 d5 3 cxd5 Qxd5
  -400     15  2 d4 b6
  -164     31  2 d3 h6 3 Bxh6 Nxh6
  -400     20  2 e4 h5
  -400     18  2 e3 h5
     1     26  2 f4 d5 3 cxd5 Qxd5
     1     24  2 f3 d5 3 cxd5 Qxd5
   -14     28  2 g4 d5 3 cxd5 Bxg4
     1     24  2 g3 d5 3 cxd5 Qxd5
     1     25  2 h4 d5 3 cxd5 Qxd5
     1     27  2 h3 d5 3 cxd5 Qxd5
After 2 Nc3 [21] searched 506 positions in 14.04 sec
-----------------------
BR BN BB BQ BK BB BN BR
BP BP -- BP BP BP BP BP
-- -- -- -- -- -- -- --
-- -- BP -- -- -- -- --
-- -- WP -- -- -- -- --
-- -- WN -- -- -- -- --
WP WP -- WP WP WP WP WP
WR -- WB WQ WK WB WN WR
-----------------------
black to move
    79     28  2 ...a5 3 d4 cxd4 4 Qxd4
   240     32  2 ...a6 3 Nb5 axb5 4 cxb5 Rxa2 5 Rxa2
   150     70  2 ...b5 3 Nxb5
    79     28  2 ...b6 3 d4 cxd4 4 Qxd4
   400      3  2 ...d5 3 Nxd5
   229     35  2 ...d6 3 h3 Bxh3 4 Nxh3
   400     26  2 ...e5 3 h4
   400     24  2 ...e6 3 h4
    79     32  2 ...f5 3 d4 cxd4 4 Qxd4
    79     28  2 ...f6 3 d4 cxd4 4 Qxd4
    79     46  2 ...g5 3 d4 cxd4 4 Qxd4
    79     28  2 ...g6 3 d4 cxd4 4 Qxd4
    79     29  2 ...h5 3 d4 cxd4 4 Qxd4
    79     46  2 ...h6 3 d4 cxd4 4 Qxd4
    59     29  2 ...Nc6 3 e4
    76     28  2 ...Na6 3 d4 cxd4 4 Qxd4
   400      3  2 ...Qc7 3 Rb1
   400      3  2 ...Qb6 3 Rb1
   400      5  2 ...Qa5 3 Rb1
    76     45  2 ...Nh6 3 d4 cxd4 4 Qxd4
   249     34  2 ...Nf6 3 e4 Nxe4 4 Nxe4
After 2 ...Nc6 [59] searched 623 positions in 17.375 sec
-----------------------
BR -- BB BQ BK BB BN BR
BP BP -- BP BP BP BP BP
-- -- BN -- -- -- -- --
-- -- BP -- -- -- -- --
-- -- WP -- -- -- -- --
-- -- WN -- -- -- -- --
WP WP -- WP WP WP WP WP
WR -- WB WQ WK WB WN WR
-----------------------
white to move
     1     29  3 Rb1 e5
  -400      9  3 Qc2 Ne5
  -400     54  3 Qb3 Ne5
  -400     11  3 Qa4 Ne5
     4     36  3 Nh3 e5
  -169     35  3 Nf3 e5 4 Nxe5 Nxe5
     1     29  3 a4 e5
  -160     41  3 a3 Nb4 4 axb4 cxb4 5 Rxa7 Rxa7
   -70    135  3 b4 Nxb4
     1     29  3 b3 e5
  -400      3  3 d4 cxd4
  -164     36  3 d3 h6 4 Bxh6 Nxh6
  -400     25  3 e4 h5
  -400     26  3 e3 h5
    10     33  3 f4 Nf6
     1     29  3 f3 e5
     1    105  3 g4 e5
     1     29  3 g3 e5
     1     30  3 h4 e5
     1     35  3 h3 e5
  -228    268  3 Nd5 d6 4 Nxe7 Ngxe7
  -204    149  3 Ne4 e5 4 Nxc5 Bxc5
   -19     28  3 Nb1 d5 4 cxd5 Qxd5
  -204    152  3 Na4 e5 4 Nxc5 Bxc5
  -199    194  3 Nb5 d5 4 cxd5 Qxd5 5 Nxa7 Rxa7
After 3 f4 [10] searched 1575 positions in 41.24 sec
-----------------------
BR -- BB BQ BK BB BN BR
BP BP -- BP BP BP BP BP
-- -- BN -- -- -- -- --
-- -- BP -- -- -- -- --
-- -- WP -- -- WP -- --
-- -- WN -- -- -- -- --
WP WP -- WP WP -- WP WP
WR -- WB WQ WK WB WN WR
-----------------------
black to move
   330    226  3 ...Ne5 4 fxe5
   288    284  3 ...Nd4 4 d3 Nxe2 5 Ngxe2
   259    342  3 ...Nb4 4 d4 Nxa2 5 Rxa2 cxd4 6 Qxd4
   264    228  3 ...Na5 4 e4 Nxc4 5 Bxc4
    79     28  3 ...Nb8 4 d4 cxd4 5 Qxd4
    59     29  3 ...a5 4 e4
   220     39  3 ...a6 4 Nb5 axb5 5 cxb5 Rxa2 6 Rxa2
   130     68  3 ...b5 4 Nxb5
    59     29  3 ...b6 4 e4
   400      3  3 ...d5 4 Nxd5
   209     37  3 ...d6 4 h3 Bxh3 5 Nxh3
    45     98  3 ...e5 4 d3 exf4 5 Bxf4
   400     24  3 ...e6 4 h4
    50     32  3 ...f5 4 Nf3
    59     29  3 ...f6 4 e4
   130     95  3 ...g5 4 fxg5
    59     30  3 ...g6 4 e4
    59     30  3 ...h5 4 e4
    59     29  3 ...h6 4 e4
    59     29  3 ...Rb8 4 e4
   400     29  3 ...Qc7 4 Nh3
   400      3  3 ...Qb6 4 Rb1
   400      5  3 ...Qa5 4 Rb1
    56     31  3 ...Nh6 4 e4
   229     35  3 ...Nf6 4 e4 Nxe4 5 Nxe4
After 3 ...e5 [45] searched 1837 positions in 47.999 sec
-----------------------
BR -- BB BQ BK BB BN BR
BP BP -- BP -- BP BP BP
-- -- BN -- -- -- -- --
-- -- BP -- BP -- -- --
-- -- WP -- -- WP -- --
-- -- WN -- -- -- -- --
WP WP -- WP WP -- WP WP
WR -- WB WQ WK WB WN WR
-----------------------
white to move
    11     68  4 fxe5 Nxe5
   -89    132  4 Rb1 exf4
  -400      3  4 Qc2 exf4
  -400      3  4 Qb3 exf4
  -400      5  4 Qa4 exf4
   -89    123  4 Kf2 exf4
   -15    150  4 Nh3 d6 5 fxe5 dxe5
  -188    247  4 Nf3 d6 5 Nxe5 dxe5 6 fxe5 Nxe5
   -89    135  4 a4 exf4
   -89    170  4 a3 exf4
  -400      7  4 b4 cxb4
  -204    141  4 b3 Qa5 5 fxe5 Qxc3 6 dxc3 Nxe5 7 Qxd7 Bxd7
  -400     27  4 d4 cxd4
  -183    150  4 d3 h6 5 fxe5 Nxe5 6 Bxh6 Nxh6
  -400     82  4 e4 h5
  -400     91  4 e3 h5
-2147483627    119  4 g4 Qh4
   -18    125  4 g3 d6 5 fxe5 dxe5
  -194    276  4 h4 Be7 5 fxe5 Bxh4 6 Rxh4 Nxe5 7 Rxh7 Rxh7
   -89    149  4 h3 exf4
  -209    205  4 Nd5 f6 5 fxe5 Nxe5 6 Nxf6 Nxf6
  -294    537  4 Ne4 exf4 5 Nxc5 Bxc5
  -109    134  4 Nb1 exf4
  -294    657  4 Na4 exf4 5 Nxc5 Bxc5
  -289    419  4 Nb5 exf4 5 Nxa7 Rxa7
   -19     56  4 f5 Nf6
After 4 fxe5 [11] searched 4237 positions in 108.125 sec
-----------------------
BR -- BB BQ BK BB BN BR
BP BP -- BP -- BP BP BP
-- -- BN -- -- -- -- --
-- -- BP -- WP -- -- --
-- -- WP -- -- -- -- --
-- -- WN -- -- -- -- --
WP WP -- WP WP -- WP WP
WR -- WB WQ WK WB WN WR
-----------------------
black to move
   245    217  4 ...Nxe5 5 e4 Nxc4 6 Bxc4
   140     31  4 ...Nce7 5 d4 cxd4 6 Qxd4
   400    166  4 ...Nd4 5 h4
   400    246  4 ...Nb4 5 h4
   345    172  4 ...Na5 5 e4 Nxc4 6 Bxc4
   400     23  4 ...Nb8 5 h4
   331    127  4 ...a5 5 Nf3 Nxe5 6 Nxe5
   331    139  4 ...a6 5 Nf3 Nxe5 6 Nxe5
   101    118  4 ...b5 5 cxb5 Nxe5
   331    175  4 ...b6 5 Nf3 Nxe5 6 Nxe5
    92    217  4 ...d5 5 Nxd5 Nxe5
    77    158  4 ...d6 5 exd6 Bxd6
   331    162  4 ...f5 5 Nf3 Nxe5 6 Nxe5
    91    196  4 ...f6 5 exf6 Nxf6
   331    292  4 ...g5 5 Nf3 Nxe5 6 Nxe5
   331    142  4 ...g6 5 Nf3 Nxe5 6 Nxe5
   331    164  4 ...h5 5 Nf3 Nxe5 6 Nxe5
   331    190  4 ...h6 5 Nf3 Nxe5 6 Nxe5
   400     40  4 ...Rb8 5 Qa4
    40    185  4 ...Qe7 5 e4 Nxe5
   400      3  4 ...Qf6 5 exf6
   400    230  4 ...Qg5 5 Nf3
     1     19  4 ...Qh4 5 g3 Qxc4
    40    171  4 ...Qc7 5 e4 Nxe5
   400    203  4 ...Qb6 5 Nf3
   400    322  4 ...Qa5 5 Nf3
   331    139  4 ...Ke7 5 Nf3 Nxe5 6 Nxe5
   316    160  4 ...Be7 5 Nf3 Nxe5 6 Nxe5
   406      1  4 ...Bd6 5 exd6
   328    195  4 ...Nh6 5 Nf3 Nxe5 6 Nxe5
   311    191  4 ...Nf6 5 Nf3 Nxe5 6 Nxe5
   311    156  4 ...Nge7 5 Nf3 Nxe5 6 Nxe5
After 4 ...Qh4 [1] searched 4982 positions in 143.346 sec
-----------------------
BR -- BB -- BK BB BN BR
BP BP -- BP -- BP BP BP
-- -- BN -- -- -- -- --
-- -- BP -- WP -- -- --
-- -- WP -- -- -- -- BQ
-- -- WN -- -- -- -- --
WP WP -- WP WP -- WP WP
WR -- WB WQ WK WB WN WR
-----------------------
white to move
  -400    194  5 g3 Be7
After 5 g3 [-400] searched 195 positions in 4.837 sec
-----------------------
BR -- BB -- BK BB BN BR
BP BP -- BP -- BP BP BP
-- -- BN -- -- -- -- --
-- -- BP -- WP -- -- --
-- -- WP -- -- -- -- BQ
-- -- WN -- -- -- WP --
WP WP -- WP WP -- -- WP
WR -- WB WQ WK WB WN WR
-----------------------
black to move
   400     10  5 ...Qxh2 6 Rxh2
   400    335  5 ...Qxc4 6 Nf3
   400     10  5 ...Qxg3 6 hxg3
   400      2  5 ...Nxe5 6 gxh4
    40    496  5 ...Qh5 6 e4 Qxe5
   400    252  5 ...Qh6 6 Nf3
   400      6  5 ...Qh3 6 Bxh3
    40    692  5 ...Qg4 6 e4 Qxd1 7 Kxd1 Nxe5
   400      3  5 ...Qf4 6 gxf4
   400     12  5 ...Qe4 6 Nxe4
    40    534  5 ...Qd4 6 e4 Qxe5
   400    267  5 ...Qg5 6 Nf3
   400      3  5 ...Qf6 6 exf6
    40    207  5 ...Qe7 6 e4 Nxe5
   331    166  5 ...Qd8 6 Nf3 Nxe5 7 Nxe5
  1031      1  5 ...Nd8 6 gxh4
  1011      1  5 ...Nce7 6 gxh4
   400      3  5 ...Nd4 6 gxh4
   400      3  5 ...Nb4 6 gxh4
   400      2  5 ...Na5 6 gxh4
  1031      1  5 ...Nb8 6 gxh4
   400      2  5 ...a5 6 gxh4
   400      2  5 ...a6 6 gxh4
   400     74  5 ...b5 6 gxh4
   400      2  5 ...b6 6 gxh4
   400     24  5 ...d5 6 gxh4
   400      3  5 ...d6 6 gxh4
   400      2  5 ...f5 6 gxh4
   400      3  5 ...f6 6 gxh4
   400      5  5 ...g5 6 gxh4
   400      2  5 ...g6 6 gxh4
   400      2  5 ...h5 6 gxh4
   400      2  5 ...h6 6 gxh4
   400      2  5 ...Rb8 6 gxh4
   400      2  5 ...Ke7 6 gxh4
   400      2  5 ...Kd8 6 gxh4
   400    716  5 ...Be7 6 e4
   400      3  5 ...Bd6 6 gxh4
   400      2  5 ...Nh6 6 gxh4
   400      2  5 ...Nf6 6 gxh4
   400      2  5 ...Nge7 6 gxh4
After 5 ...Qh5 [40] searched 3901 positions in 100.945 sec
-----------------------
BR -- BB -- BK BB BN BR
BP BP -- BP -- BP BP BP
-- -- BN -- -- -- -- --
-- -- BP -- WP -- -- BQ
-- -- WP -- -- -- -- --
-- -- WN -- -- -- WP --
WP WP -- WP WP -- -- WP
WR -- WB WQ WK WB WN WR
-----------------------
white to move
  -400    130  6 Rb1 d6
  -400     46  6 Qc2 Qxe5
  -400    213  6 Qb3 Qxh2
  -400    314  6 Qa4 Qxe5
    11    189  6 Kf2 Qxe5
  -214   1009  6 Bg2 Nxe5 7 Bxb7 Bxb7
  -233    574  6 Bh3 Qxe5 7 Bxd7 Bxd7
  -103    299  6 Nh3 d6 7 exd6 Bxh3 8 Bxh3 Qxh3
   -69    276  6 Nf3 g5 7 Nxg5 Qxg5
  -400    184  6 a4 d6
  -400    225  6 a3 d6
  -209   1219  6 b4 Qxe5 7 bxc5 Qxc3 8 dxc3 Bxc5 9 Qxd7 Bxd7
  -400    132  6 b3 d6
  -400     58  6 d4 cxd4
   -95    357  6 d3 h6 7 Bxh6 Qxe5 8 Bxg7 Bxg7
    40    249  6 e4 Qxe5
    30    230  6 e3 Qxe5
  -400     64  6 h4 b5
  -400     80  6 h3 b5
  -400    167  6 Nd5 d6
  -204   1720  6 Ne4 Nxe5 7 Nxc5 Nxc4 8 Nxb7 Bxb7
  -400     96  6 Nb1 d6
  -204   1954  6 Na4 Nxe5 7 Nxc5 Nxc4 8 Nxb7 Bxb7
  -189   1554  6 Nb5 Qxe5 7 Nxa7 Rxa7
-2147483627     18  6 g4 Qh4
    -8    281  6 e6 dxe6
After 6 e4 [40] searched 11664 positions in 306.731 sec
-----------------------
BR -- BB -- BK BB BN BR
BP BP -- BP -- BP BP BP
-- -- BN -- -- -- -- --
-- -- BP -- WP -- -- BQ
-- -- WP -- WP -- -- --
-- -- WN -- -- -- WP --
WP WP -- WP -- -- -- WP
WR -- WB WQ WK WB WN WR
-----------------------
black to move
   400      8  6 ...Qxh2 7 Rxh2
   400      7  6 ...Qxe5 7 Rb1
    40      8  6 ...Qxd1 7 Kxd1 Nxe5
   400      3  6 ...Nxe5 7 Qxh5
   400    329  6 ...Qh6 7 Nf3
   400      2  6 ...Qh4 7 gxh4
   400      6  6 ...Qh3 7 Bxh3
   400    265  6 ...Qg5 7 Nf3
   400      2  6 ...Qf5 7 exf5
   400    218  6 ...Qg6 7 Nf3
   400    294  6 ...Qg4 7 Be2
   400      8  6 ...Qf3 7 Nxf3
   400      2  6 ...Qe2 7 Qxe2
  1060      1  6 ...Nd8 7 Qxh5
  1040      1  6 ...Nce7 7 Qxh5
  1040      1  6 ...Nd4 7 Qxh5
   400      3  6 ...Nb4 7 Qxh5
   400      3  6 ...Na5 7 Qxh5
  1060      1  6 ...Nb8 7 Qxh5
   400      9  6 ...a5 7 Qxh5
   400      9  6 ...a6 7 Qxh5
   400     11  6 ...b5 7 Qxh5
   400      9  6 ...b6 7 Qxh5
   400     19  6 ...d5 7 Qxh5
   121    725  6 ...d6 7 Qxh5 dxe5 8 Qxe5 Nxe5
  1040      1  6 ...f5 7 Qxh5
  1040      1  6 ...f6 7 Qxh5
   400     11  6 ...g5 7 Qxh5
   140    482  6 ...g6 7 Qxh5 gxh5
   400     15  6 ...h6 7 Qxh5
   400      9  6 ...Rb8 7 Qxh5
   400      9  6 ...Ke7 7 Qxh5
   400      9  6 ...Kd8 7 Qxh5
   400      9  6 ...Be7 7 Qxh5
   400     38  6 ...Bd6 7 exd6
   400      9  6 ...Nh6 7 Qxh5
   320   1003  6 ...Nf6 7 exf6 Qxd1 8 Kxd1 gxf6
   400      9  6 ...Nge7 7 Qxh5
After 6 ...Qxd1 [40] searched 3587 positions in 100.124 sec
-----------------------
BR -- BB -- BK BB BN BR
BP BP -- BP -- BP BP BP
-- -- BN -- -- -- -- --
-- -- BP -- WP -- -- --
-- -- WP -- WP -- -- --
-- -- WN -- -- -- WP --
WP WP -- WP -- -- -- WP
WR -- WB BQ WK WB WN WR
-----------------------
white to move
    40     48  7 Kxd1 Nxe5
    20     41  7 Nxd1 Nxe5
  -760     24  7 Kf2 Qg4
After 7 Kxd1 [40] searched 116 positions in 3.455 sec
-----------------------
BR -- BB -- BK BB BN BR
BP BP -- BP -- BP BP BP
-- -- BN -- -- -- -- --
-- -- BP -- WP -- -- --
-- -- WP -- WP -- -- --
-- -- WN -- -- -- WP --
WP WP -- WP -- -- -- WP
WR -- WB WK -- WB WN WR
-----------------------
black to move
   266     89  7 ...Nxe5 8 Kc2 Nxc4 9 Bxc4
   181     29  7 ...Nd8 8 Kc2
   161     32  7 ...Nce7 8 Kc2
   340     42  7 ...Nd4 8 b3 Nxb3 9 axb3
   360    146  7 ...Nb4 8 Nge2 Nxa2 9 Rxa2
   366    105  7 ...Na5 8 Kc2 Nxc4 9 Bxc4
   181     29  7 ...Nb8 8 Kc2
   360     72  7 ...a5 8 Nf3 Nxe5 9 Nxe5
   360     80  7 ...a6 8 Nf3 Nxe5 9 Nxe5
   365    189  7 ...b5 8 Nf3 bxc4 9 Bxc4 Nxe5 10 Nxe5
   360    128  7 ...b6 8 Nf3 Nxe5 9 Nxe5
   331    304  7 ...d5 8 Nf3 dxe4 9 Nxe4 Nxe5 10 Nxe5
   106    104  7 ...d6 8 exd6 Bxd6
   350    260  7 ...f5 8 Nf3 fxe4 9 Nxe4 Nxe5 10 Nxe5
   120    121  7 ...f6 8 exf6 Nxf6
   374    133  7 ...g5 8 d3 Nxe5 9 Bxg5 Nxc4 10 dxc4
   360     83  7 ...g6 8 Nf3 Nxe5 9 Nxe5
   360     87  7 ...h5 8 Nf3 Nxe5 9 Nxe5
   360    103  7 ...h6 8 Nf3 Nxe5 9 Nxe5
   360     84  7 ...Rb8 8 Nf3 Nxe5 9 Nxe5
   360     82  7 ...Ke7 8 Nf3 Nxe5 9 Nxe5
   360     86  7 ...Kd8 8 Nf3 Nxe5 9 Nxe5
   345     95  7 ...Be7 8 Nf3 Nxe5 9 Nxe5
   435      1  7 ...Bd6 8 exd6
   357    102  7 ...Nh6 8 Nf3 Nxe5 9 Nxe5
   400     33  7 ...Nf6 8 Nf3
   340     94  7 ...Nge7 8 Nf3 Nxe5 9 Nxe5
After 7 ...d6 [106] searched 2740 positions in 76.46 sec
-----------------------
BR -- BB -- BK BB BN BR
BP BP -- -- -- BP BP BP
-- -- BN BP -- -- -- --
-- -- BP -- WP -- -- --
-- -- WP -- WP -- -- --
-- -- WN -- -- -- WP --
WP WP -- WP -- -- -- WP
WR -- WB WK -- WB WN WR
-----------------------
white to move
   106     52  8 exd6 Bxd6
    11    141  8 Rb1 dxe5
    11    122  8 Ke2 dxe5
    11    131  8 Ke1 dxe5
    32    117  8 Kc2 dxe5
    26    162  8 Bg2 dxe5
    -4    472  8 Bh3 dxe5 9 Bxc8 Rxc8
  -104    154  8 Be2 h5 9 Bxh5 Rxh5 10 exd6 Bxd6
   -89    125  8 Bd3 Nb4 9 exd6 Nxd3
   -94    223  8 Nh3 Na5 9 exd6 Nxc4 10 Bxc4 Bxh3 11 Bxf7 Kxf7
    31    147  8 Nge2 dxe5
  -159    173  8 Nf3 dxe5 9 Nxe5 Nxe5
    11    131  8 a4 dxe5
   -84    184  8 a3 Nb4 9 exd6 Bxd6 10 axb4 cxb4 11 Rxa7 Rxa7
  -165    403  8 b4 cxb4 9 exd6 bxc3 10 dxc3 Bxd6
   -94    130  8 b3 Nd4 9 exd6 Nxb3 10 axb3 Bxd6 11 Rxa7 Rxa7
  -165    561  8 d4 cxd4 9 exd6 dxc3 10 bxc3 Bxd6
   -88    194  8 d3 h6 9 exd6 Bxd6 10 Bxh6 Nxh6
  -289    156  8 h4 g5 9 hxg5 dxe5 10 Rxh7 Rxh7
   -94    251  8 h3 Bg4 9 hxg4 dxe5 10 Rxh7 Rxh7
   -94    175  8 Nd5 b6 9 Nxb6 axb6 10 exd6 Bxd6
   -94    114  8 Nce2 Nb4 9 exd6 Nxa2 10 Rxa2 Bxd6 11 Rxa7 Rxa7
  -114    117  8 Nb1 Nb4 9 exd6 Nxa2 10 Rxa2 Bxd6 11 Rxa7 Rxa7
  -194    470  8 Na4 dxe5 9 Nxc5 Bxc5
  -189    195  8 Nb5 dxe5 9 Nxa7 Rxa7
     6    171  8 g4 Bxg4
     6    104  8 e6 Bxe6
After 8 exd6 [106] searched 5402 positions in 158.398 sec
-----------------------
BR -- BB -- BK BB BN BR
BP BP -- -- -- BP BP BP
-- -- BN WP -- -- -- --
-- -- BP -- -- -- -- --
-- -- WP -- WP -- -- --
-- -- WN -- -- -- WP --
WP WP -- WP -- -- -- WP
WR -- WB WK -- WB WN WR
-----------------------
black to move
   346    118  8 ...Bxd6 9 Nh3 Bxg3 10 hxg3 Bxh3 11 Bxh3
   400     79  8 ...Nd8 9 Nb5
   400      4  8 ...Nce7 9 dxe7
   400    205  8 ...Ne5 9 Nb5
   400    100  8 ...Nd4 9 e5
   400    354  8 ...Nb4 9 Nb5
   400    232  8 ...Na5 9 Nb5
   400     79  8 ...Nb8 9 Nb5
   400     75  8 ...a5 9 Nb5
   135     91  8 ...a6 9 d4 Bxd6 10 dxc5 Bxc5
   400      3  8 ...b5 9 Nxb5
   400     94  8 ...b6 9 Nb5
   400    193  8 ...f5 9 Bd3
   400     78  8 ...f6 9 Nb5
   400     43  8 ...g5 9 Nf3
   400     76  8 ...g6 9 Nb5
   400     82  8 ...h5 9 Nb5
   400     94  8 ...h6 9 Nb5
   400     76  8 ...Rb8 9 Nb5
   400     76  8 ...Bd7 9 Nb5
   400    200  8 ...Be6 9 Nb5
   400     15  8 ...Bf5 9 Rb1
   112     32  8 ...Bg4 9 Kc2 Bxd6
   400      2  8 ...Bh3 9 Bxh3
   129     80  8 ...Kd7 9 d4 Kxd6 10 dxc5 Kxc5
   400     76  8 ...Kd8 9 Nb5
   400     73  8 ...Be7 9 Nb5
   400     85  8 ...Nh6 9 Nb5
   115    326  8 ...Nf6 9 d4 Bxd6 10 dxc5 Bxc5
   400     40  8 ...Nge7 9 Nh3
After 8 ...Bg4 [112] searched 3111 positions in 93.795 sec
-----------------------
BR -- -- -- BK BB BN BR
BP BP -- -- -- BP BP BP
-- -- BN WP -- -- -- --
-- -- BP -- -- -- -- --
-- -- WP -- WP -- BB --
-- -- WN -- -- -- WP --
WP WP -- WP -- -- -- WP
WR -- WB WK -- WB WN WR
-----------------------
white to move
    91     65  9 Ke1 Bxd6
   112     65  9 Kc2 Bxd6
   111    147  9 Be2 Bxe2 10 Ngxe2 Bxd6
   111     86  9 Nge2 Bxd6
   -74     62  9 Nf3 Bxf3
    91     95  9 Nce2 Bxd6
After 9 Kc2 [112] searched 526 positions in 15.803 sec
-----------------------
BR -- -- -- BK BB BN BR
BP BP -- -- -- BP BP BP
-- -- BN WP -- -- -- --
-- -- BP -- -- -- -- --
-- -- WP -- WP -- BB --
-- -- WN -- -- -- WP --
WP WP WK WP -- -- -- WP
WR -- WB -- -- WB WN WR
-----------------------
black to move
   367    132  9 ...Bxd6 10 Nh3 Bxh3 11 Bxh3 Bxg3 12 hxg3
   400     82  9 ...Bh5 10 Nb5
   400      2  9 ...Bf5 10 exf5
   400    210  9 ...Be6 10 Nb5
   400     80  9 ...Bd7 10 Nb5
   400     80  9 ...Bc8 10 Nb5
   400      2  9 ...Bh3 10 Bxh3
   400      2  9 ...Bf3 10 Nxf3
   400      2  9 ...Be2 10 Bxe2
   400      2  9 ...Bd1 10 Kxd1
   400    105  9 ...Nd8 10 Nb5
   400      4  9 ...Nce7 10 dxe7
   400    273  9 ...Ne5 10 Nb5
   112      4  9 ...Nd4 10 Kb1 Bxd6
   112     26  9 ...Nb4 10 Kb1 Bxd6
   400    301  9 ...Na5 10 Nb5
   400    105  9 ...Nb8 10 Nb5
   400    101  9 ...a5 10 Nb5
   141    115  9 ...a6 10 d4 Bxd6 11 dxc5 Bxc5
   400      3  9 ...b5 10 Nxb5
   400    116  9 ...b6 10 Nb5
   400     77  9 ...f5 10 Bh3
   400    104  9 ...f6 10 Nb5
   400     15  9 ...g5 10 Bh3
   400    102  9 ...g6 10 Nb5
   400    113  9 ...h5 10 Nb5
   400    123  9 ...h6 10 Nb5
   400    102  9 ...Rb8 10 Nb5
   400    100  9 ...Rc8 10 Nb5
   141    150  9 ...Rd8 10 d4 Bxd6 11 dxc5 Bxc5
   135    118  9 ...Kd7 10 d4 Kxd6 11 dxc5 Kxc5
   400    102  9 ...Kd8 10 Nb5
   120    131  9 ...O-O-O 10 d4 Bxd6 11 dxc5 Bxc5
   400      4  9 ...Be7 10 dxe7
   400    117  9 ...Nh6 10 Nb5
   121    346  9 ...Nf6 10 d4 Bxd6 11 dxc5 Bxc5
   400     54  9 ...Nge7 10 Nh3
After 9 ...Nd4 [112] searched 3542 positions in 114.725 sec
-----------------------
BR -- -- -- BK BB BN BR
BP BP -- -- -- BP BP BP
-- -- -- WP -- -- -- --
-- -- BP -- -- -- -- --
-- -- WP BN WP -- BB --
-- -- WN -- -- -- WP --
WP WP WK WP -- -- -- WP
WR -- WB -- -- WB WN WR
-----------------------
white to move
    -9    102  10 Kd3 Nb3 11 axb3 Bxd6 12 Rxa7 Rxa7
    12    100  10 Kb1 Nb3 11 axb3 Bxd6 12 Rxa7 Rxa7
After 10 Kb1 [12] searched 204 positions in 6.058 sec
-----------------------
BR -- -- -- BK BB BN BR
BP BP -- -- -- BP BP BP
-- -- -- WP -- -- -- --
-- -- BP -- -- -- -- --
-- -- WP BN WP -- BB --
-- -- WN -- -- -- WP --
WP WP -- WP -- -- -- WP
WR WK WB -- -- WB WN WR
-----------------------
black to move
   400     99  10 ...Bxd6 11 b3
   400    110  10 ...Ne6 11 Nb5
   400      3  10 ...Nf5 11 exf5
   400    351  10 ...Nf3 11 Nb5
   400      8  10 ...Ne2 11 Bxe2
   400      2  10 ...Nc2 11 Kxc2
-------------------------------------------------------------------------

What I get from all this is that we have a problem with the strategy of
following captures past a given depth.  It gives the computer the impression
that captures are force moves, since we don't look at any other moves in
the position.  This gives a false reading, since many quite moves exist
that are surperior to the capture.  In essence past a the first depth
cutoff the computer is playing "must take" variant or fairy chess.  This
just will not do.  Is there a way to increase the depth for captures, but
the computer's feet on the ground?

One way might be to include a quiet move or two as an option, just so the
computer would no go off thinking it had to take everything it can.
But which move?

