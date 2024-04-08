# COMP30024 Artificial Intelligence, Semester 1 2024
# Project Part A: Single Player Tetress

from contextlib import nullcontext
from .core import PlayerColor, Coord, PlaceAction,  Direction, Vector2
from .utils import render_board
from dataclasses import dataclass
from enum import Enum
from queue import PriorityQueue
import math
import time 
BOARD_SIZE = 11 
PIECE_LENGTH = 4

def search(board: dict[Coord, PlayerColor], target: Coord):
    start = time.time()
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
    pq.put((estimate_number_pieces_remain(board,target) + emptyCellHeuristic(board, target), board, initialCost, initialMoves))
    
    while not pq.empty():
        
        (priority, currentBoard, totalCost, moves) = MVheappop(pq.queue)
        
        for row in range(BOARD_SIZE):
            for col in range(BOARD_SIZE):

                placePosition = Coord(row, col)
                if not isValidSquare(currentBoard, placePosition):
                    continue
                
                for piece in pieces:
                
                    # The sign of a translation will only ever be negative (as setup by our standardisation of pieces)
                    # The negative is resolved in the pieceTranslation function itself
                    for rowTranslation in range(PIECE_LENGTH):
                        for colTranslation in range(PIECE_LENGTH):

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

                                currentMoves.append(PlaceAction(*newState[1]))
                                #Checks whether a row or column needs to be removed
                                for block in newState[1]:
                                    if rowBlocksFilled(newBoard, block.r) == BOARD_SIZE and block.r != target.r:
                                        for c in range(BOARD_SIZE):
                                            newBoard.pop(Coord(block.r, c))
                                    if columnBlocksFilled(newBoard, block.c) == BOARD_SIZE and block.c != target.c:     
                                        for r in range(BOARD_SIZE):
                                            newBoard.pop(Coord(r, block.c))
                                current_target = target

                                newCost = totalCost + 1
                                priority = newCost + (estimate_number_pieces_remain(newBoard, current_target))
                                priority = priority + 0.25 * shortestManhattenDistance(newBoard, current_target, board)
                                
                                
                                if rowBlocksFilled(newBoard, target.r) == BOARD_SIZE or columnBlocksFilled(newBoard, target.c) == BOARD_SIZE:
                                        
                                        return currentMoves
                                MVheappush(pq.queue, (priority, newBoard, newCost, currentMoves))
        
                                 
       
       
    return None
    
  
#checks how many blocks in the targeted row are filled
def rowBlocksFilled(board: dict[Coord, PlayerColor], rowIndex: int):
    """
    Checks whether the row has been completely filled
    """
    filled = 0
    for i in range(BOARD_SIZE):
        if (board.get(Coord(rowIndex, i)) != None):
            filled += 1
    return filled

#Checks how many blocks in targeted column are filled
def columnBlocksFilled(board: dict[Coord, PlayerColor], columnIndex: int):
    
    filled = 0
    for i in range(BOARD_SIZE):
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
    return (updatedBoard, coords)

#Finds the closest block to the target in terms of manhatten distance
def shortestManhattenDistance(board: dict[Coord, PlayerColor], target: Coord, beforeBoard: dict[Coord, PlayerColor]):
    min_dist = BOARD_SIZE + BOARD_SIZE
    
    for piece in board:
        if board.get(piece) == PlayerColor.RED:
                column_dist = abs(target.c - piece.c)
                row_dist = abs(target.r - piece.r)
                if(row_dist + column_dist <= min_dist):
                        min_dist = row_dist + column_dist
                        
    return min_dist

def emptyCellHeuristic(board: dict[Coord, PlayerColor], target: Coord):
    return  - max(rowBlocksFilled(board, target.r), columnBlocksFilled(board, target.c))



#Estimates how many pieces still need to be placed within the target's row/column
def estimate_number_pieces_remain(board: dict[Coord, PlayerColor], target:Coord):
    rowPieceLeft = rowEstimatePiecesRemain(board, target)
    columnPieceLeft = columnEstimatePiecesRemain(board, target)
    #Checks whether a block can't be accessed in the column
    #Checks whether a block can't be accessed 
    checkCol = checkBlockedTargetCol(board, target)
    if checkCol[0] == True:
        #checks which the row above/below or column left/right will take the least blocks to give access to target column
        rows = min(rowEstimatePiecesRemain(board, Coord(checkCol[1], target.c).up()), rowEstimatePiecesRemain(board, Coord(checkCol[2], target.c)))
        columns = min(columnEstimatePiecesRemain(board, target.left()), columnEstimatePiecesRemain(board, target.right()))
        columnPieceLeft += min(rows, columns)

    #Checks whether a block can't be accessed in the row
    checkRow = checkBlockedTargetRow(board, target)
        #Checks whether a block can't be accessed
    if checkRow[0] == True:
        #checks which the row above/below or column left/right will take the least blocks to give access to target row
        rows = min(rowEstimatePiecesRemain(board, target.up()), rowEstimatePiecesRemain(board, target.down()))
        columns = columnEstimatePiecesRemain(board, Coord(target.r, checkRow[1]).left()) + columnEstimatePiecesRemain(board, Coord(target.r, checkRow[2]))
        rowPieceLeft += min(rows, columns)
   
    return min(columnPieceLeft, rowPieceLeft)

#Checks if a block cannot be reached in a row
def checkBlockedTargetRow(board: dict[Coord, PlayerColor], target: Coord): 
    possibleBlock = False
    filledBlock = False
    blocked = False
    colStart = 0
    colEnd = 0
    for block in range(BOARD_SIZE):
        #If block can't be accessed
        if possibleBlock and Coord(target.r, block) in board:
            possibleBlock = False
            colStart = possibleColStart
            blocked = True
            colEnd = block 

        #IF the block isn't filled, check if it can be accessed. 
        elif filledBlock and Coord(target.r, block) not in board:
            possibleColStart = block
            possibleBlock = True
            filledBlock = False
            #Checks if block can be accessed from either row above or below it
            if(Coord((target.r + 1)% BOARD_SIZE, block) not in board or Coord((target.r - 1)% BOARD_SIZE, block) not in board):
                possibleBlock = False
            
        
        elif Coord(target.r, block) in board:
            filledBlock = True

    if blocked == False:
        return (False, 0, 0)
    
    return (True, colStart, colEnd)

#Checks if a block cannot be reached in a row
def checkBlockedTargetCol(board: dict[Coord, PlayerColor], target: Coord): 
    possibleBlock = False
    filledBlock = False
    blocked = False
    rowstart = 0
    rowend = 0
    for block in range(BOARD_SIZE):
        #If block can't be accessed 
        if possibleBlock and Coord(block, target.c) in board:
            possibleBlock = False
            rowstart = possiblerowstart
            blocked = True
            rowend = block 
        #If block isn't filled and is in between a filled block, check if block can be accessed
        elif filledBlock and Coord(block, target.c) not in board:
            if(possibleBlock == False):
                possiblerowstart = block
            possibleBlock = True
            filledBlock = False
            #Checks if block can be accessed from either column above or below it
            if(Coord(block , (target.c + 1)% BOARD_SIZE) not in board or Coord(block, (target.c -1)% BOARD_SIZE) not in board):
                possibleBlock = False
            
        elif Coord(block, target.c) in board:
            filledBlock = True
            

    if (blocked == False):
        return (False, 0, 0)
    
    return (True, rowstart, rowend)

#Estimates how many pieces we must place to complete a row 
def rowEstimatePiecesRemain(board: dict[Coord, PlayerColor], target:Coord):
    rowPieceLeft = 0
    count = 0
    check = 0
    for i in range(BOARD_SIZE):
        #If a block is in the path
        if (board.get(Coord(target.r, i)) != None):
            #Check if another block can be placed based on other statistics 
            if (check != 0 and (check % PIECE_LENGTH != 0 )):
                   
                    rowPieceLeft += 1
            check = 0
            count = 0
            continue       
        else:
            check += 1
        
        #If board has blank space
        if board.get(Coord(target.r, i )) == None:
                     count += 1
        #If the piece equals             
        if(count == PIECE_LENGTH):
            rowPieceLeft += 1
            count = 0
            check = 0
    if(check > 0 and check % PIECE_LENGTH != 0):
        rowPieceLeft += 1
  
    return rowPieceLeft

#Estimates how many pieces we must place to complete a column
def columnEstimatePiecesRemain(board: dict[Coord, PlayerColor], target: Coord):
    
    columnPieceLeft = 0
    count = 0
    check = 0
    for i in range(BOARD_SIZE):

        if (board.get(Coord(i, target.c)) != None ):

            if (check != 0 and (check % PIECE_LENGTH != 0 )):
                    columnPieceLeft += 1
            check = 0
            count = 0
            continue
        else:
            check += 1

        if board.get(Coord(i, target.c)) == None:
                     count += 1

        if(count == PIECE_LENGTH):
            columnPieceLeft += 1
            count = 0
            check = 0
    if(check > 0 and check % PIECE_LENGTH != 0):
        columnPieceLeft += 1
    return columnPieceLeft

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