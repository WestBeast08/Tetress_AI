# COMP30024 Artificial Intelligence, Semester 1 2024
# Project Part A: Single Player Tetress

from contextlib import nullcontext
from .core import PlayerColor, Coord, PlaceAction,  Direction, Vector2
from .utils import render_board
from dataclasses import dataclass
from enum import Enum
from queue import PriorityQueue
BOARD_SIZE = 11 



def search(board: dict[Coord, PlayerColor], target: Coord):
    '''
    Uses a min heap priority queue storing the heuristic value, board, total cost, and made moves of the current state
    '''
    pq = PriorityQueue()
    initialCost = 0
    initialMoves = []

    # Is this the best way or format to store all the pieces/rotations?
    pieces = (straightVerticalBlock(), straightHorizontalBlock(), squareBlock(), TBlockLeft(), TblockUp(), TBlockDown(),
              TBlockRight(), LBlockUp(), LBlockDown(), LBlockLeft(), LBlockRight(), JBlockDown(), JBlockLeft(), JBlockRight(),
              JBlockUp(), ZBlockHorizontal(), ZBlockVertical(), SBlockHorizontal(), SBlockVertical())
    pq.put((emptyCellHeuristic(board, target), board, initialCost, initialMoves))
    
    while not pq.empty():

        (priority, currentBoard, totalCost, moves) = MVheappop(pq.queue)

        if rowBlocksFilled(currentBoard, target.r) == BOARD_SIZE or columnBlocksFilled(currentBoard, target.c) == BOARD_SIZE:
            print(render_board(currentBoard, target, True))
            return moves
        

        for row in range(BOARD_SIZE):
            for col in range(BOARD_SIZE):

                placePosition = Coord(row, col)
                if not isValidSquare(currentBoard, placePosition):
                    continue
                
                for piece in pieces:
                    # The sign of a translation will only ever be negative (as setup by our standardisation of pieces)
                    # The negative is resolved in the pieceTranslation function itself
                    for rowTranslation in range(4):
                        for colTranslation in range(4):

                            translation = Vector2(rowTranslation, colTranslation)

                            # this catches all
                            if not isValidTranslation(piece, translation):
                                continue

                            if isValidPosition(currentBoard, piece, placePosition - translation):
        
                                # havent figured out the logistics of the priority part but it should look something like this
                                # The smaller the priority number is the better it is to expand upon
                                newState = addMove(piece, currentBoard, placePosition, translation)
                                newBoard = newState[0]
                                currentMoves = moves.copy()
                                specificPiece = piece.copy()
                                # for i in range(4):
                                #     specificPiece[i] += placePosition - translation
                                currentMoves.append(PlaceAction(*newState[1]))
                                newCost = totalCost + 1
                                priority = newCost + emptyCellHeuristic(newBoard, target)
                                MVheappush(pq.queue, (priority, newBoard, newCost, currentMoves))

    return None
    
    # return [
    #     PlaceAction(Coord(2, 5), Coord(2, 6), Coord(3, 6), Coord(3, 7)),
    #     PlaceAction(Coord(1, 8), Coord(2, 8), Coord(3, 8), Coord(4, 8)),
    #     PlaceAction(Coord(5, 8), Coord(6, 8), Coord(7, 8), Coord(8, 8)),
    # ]

def rowBlocksFilled(board: dict[Coord, PlayerColor], rowIndex: int):
    """
    Checks whether the row has been completely filled
    """
    filled = 0
    for i in range(11):
        if (board.get(Coord(rowIndex, i)) != None):
            filled += 1
    return filled

def columnBlocksFilled(board: dict[Coord, PlayerColor], columnIndex: int):
    """
    Checks whether the column has been completely filled
    """
    filled = 0
    for i in range(11):
        if (board.get(Coord(i, columnIndex)) != None):
            filled += 1
    return filled

# Make sure move is valid at placePosition before calling function
def addMove(piece: list[Vector2], board: dict[Coord, PlayerColor], placePosition: Coord, translation: Vector2):
    '''
    Adds specific piece to the board (need to allow for moving in negative direction next after testing)
    '''
    coords = []
    updatedBoard = board.copy()
    relativePosition = placePosition - translation
    for vector in piece:
        updatedBoard[relativePosition + vector] = PlayerColor.RED
        coords.append(relativePosition + vector)
    return [updatedBoard, coords]

# Maximum will be 20 since target block is counted (could maybe change to make it not counted)
def emptyCellHeuristic(board: dict[Coord, PlayerColor], target: Coord):
    return BOARD_SIZE * 2 - rowBlocksFilled(board, target.r) - columnBlocksFilled(board, target.c)

# Assume that (0, 0) is the base position of a piece. None return means specified translation is out of bounds of the piece
def isValidTranslation(piece: list[Vector2], translation: Vector2):
    if(translation in piece):
        return True
    return False

def isValidPosition(board: dict[Coord, PlayerColor], piece: list[Vector2], placePosition: Coord):
    for block in piece:
        if (placePosition + block) in board:
            return False
    return True

def isValidSquare(board: dict[Coord, PlayerColor], square: Coord):
    if square in board:
        return False
    for translation in (Vector2(0,1), Vector2(1,0), Vector2(0,-1), Vector2(-1,0)):
        if square + translation in board and board[square + translation] == PlayerColor.RED:
            return True
    return False

# (0,0) is the top most piece (leftmost if multiple in the same row). This is for consistency

def straightVerticalBlock():
    """
    Provides coordinates for a generical shape of a straight vertical block
    """
    return [Vector2(0,0), Vector2(1, 0), Vector2(2, 0), Vector2(3, 0)]   
def straightHorizontalBlock():
    """
    Provides coordinates for a generical shape of a straight Horizontal block
    """
    return [Vector2(0, 0), Vector2(0, 1), Vector2(0, 2), Vector2(0, 3)]

def squareBlock():
    """
    Provides coordinates for a generical shape of Square block
    """
    return[Vector2(0,0), Vector2(0,1), Vector2(1,0), Vector2(1,1)]

# 'Up' Rotation Relative to T shape
def TBlockLeft():
    """
    Provides coordinates for a generical shape of a T Block
    """
    return[Vector2(0,0), Vector2(1,0), Vector2(2,0), Vector2(1,1)]
def TblockUp():
    return[Vector2(0,0), Vector2(0,1), Vector2(0,2), Vector2(1,1)]
def TBlockDown():
    return[Vector2(0,0), Vector2(1,-1), Vector2(1,0), Vector2(1,1)]
def TBlockRight():
    return[Vector2(0,0), Vector2(1,0), Vector2(2,0), Vector2(1, -1)]

# 'Up' Rotation Relative to L shape
def LBlockUp():
    """
    Provides coordinates for a generical shape of a L block
    """
    return[Vector2(0,0), Vector2(1,0), Vector2(2,0), Vector2(2,1)]
def LBlockRight():
    return[Vector2(0,0), Vector2(0,1), Vector2(0,2), Vector2(1,0)]
def LBlockDown():
    return[Vector2(0,0), Vector2(0,1), Vector2(1,1), Vector2(2,1)]
def LBlockLeft():
    return[Vector2(0,0), Vector2(1,0), Vector2(1,-1), Vector2(1,-2)]

# 'Up' Rotation Relative to J shape
def JBlockRight():
    """
    Provides coordinates for a generical shape of a J block
    """
    return[Vector2(0,0), Vector2(1,0), Vector2(1,1), Vector2(1,2)]
def JBlockDown():
    return[Vector2(0,0), Vector2(0,1), Vector2(1,0), Vector2(2,0)]
def JBlockLeft():
    return[Vector2(0,0), Vector2(0,1), Vector2(0,2), Vector2(1,2)]
def JBlockUp():
    return[Vector2(0,0), Vector2(1,0), Vector2(2,0), Vector2(2,-1)]

# Horizonal spans 3 across, 2 up. Vice versa for Vertical
def ZBlockHorizontal():
    """
    Provides coordinates for a generical shape of a Z block
    """
    return[Vector2(0,0), Vector2(0,1), Vector2(1,1), Vector2(1,2)]
def ZBlockVertical():
    return[Vector2(0,0), Vector2(1,0), Vector2(1, -1), Vector2(2, -1)]
def SBlockVertical():
    """
    Provides coordinates for a generical shape of a S block
    """
    return[Vector2(0,0), Vector2(1,0), Vector2(1,1), Vector2(2,1)]
def SBlockHorizontal():
    return[Vector2(0,0), Vector2(0,1), Vector2(1,0), Vector2(1,-1)]


# Adapted from heapq.py to allow for comparison of priority but storage of a tuple
def MVsiftdown(heap, startpos, pos):
    newitem = heap[pos]
    while pos > startpos:
        parentpos = (pos - 1) >> 1
        parent = heap[parentpos]
        if newitem[0] < parent[0]:
            heap[pos] = parent
            pos = parentpos
            continue
        break
    heap[pos] = newitem

# Adapted from heapq.py to allow for comparison of priority but storage of a tuple
def MVsiftup(heap, pos):
    endpos = len(heap)
    startpos = pos
    newitem = heap[pos]
    # Bubble up the smaller child until hitting a leaf.
    childpos = 2*pos + 1    # leftmost child position
    while childpos < endpos:
        # Set childpos to index of smaller child.
        rightpos = childpos + 1
        if rightpos < endpos and not heap[childpos][0] < heap[rightpos][0]:
            childpos = rightpos
        # Move the smaller child up.
        heap[pos] = heap[childpos]
        pos = childpos
        childpos = 2*pos + 1
    # The leaf at pos is empty now.  Put newitem there, and bubble it up
    # to its final resting place (by sifting its parents down).
    heap[pos] = newitem
    MVsiftdown(heap, startpos, pos)

# Adapted from heapq.py to allow for comparison of priority but storage of a tuple
def MVheappush(heap, item):
    """Push item onto heap, maintaining the heap invariant."""
    heap.append(item)
    MVsiftdown(heap, 0, len(heap)-1)

# Adapted from heapq.py to allow for comparison of priority but storage of a tuple
def MVheappop(heap):
    """Pop the smallest item off the heap, maintaining the heap invariant."""
    lastelt = heap.pop()    # raises appropriate IndexError if heap is empty
    if heap:
        returnitem = heap[0]
        heap[0] = lastelt
        MVsiftup(heap, 0)
        return returnitem
    return lastelt