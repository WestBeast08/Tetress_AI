# COMP30024 Artificial Intelligence, Semester 1 2024
# Project Part A: Single Player Tetress

from contextlib import nullcontext
from .core import PlayerColor, Coord, PlaceAction,  Direction, Vector2
from .utils import render_board
from dataclasses import dataclass
from queue import PriorityQueue
BOARD_SIZE = 11 
PIECE_LENGTH = 4

def search(board: dict[Coord, PlayerColor], target: Coord):
    """
    Uses a min heap priority queue storing the heuristic value, board, total cost, and made moves of the current state
    """
    pq = PriorityQueue()
    initialCost = 0
    initialMoves = []
    
    pieces = (straightVerticalBlock(), straightHorizontalBlock(), squareBlock(), TBlockLeft(), TBlockUp(), TBlockDown(),
              TBlockRight(), LBlockUp(), LBlockDown(), LBlockLeft(), LBlockRight(), JBlockDown(), JBlockLeft(), JBlockRight(),
              JBlockUp(), ZBlockHorizontal(), ZBlockVertical(), SBlockHorizontal(), SBlockVertical())
    
    # Initial State
    pq.put((estimatePiecesRemain(board,target) + shortestDistance(board, target), board, initialCost, initialMoves))
    
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

                            if not isValidTranslation(piece, translation):
                                continue

                            if isValidPosition(currentBoard, piece, placePosition - translation):
        
                                newState = addMove(piece, currentBoard, placePosition, translation)
                                newBoard = newState[0]
                                currentMoves = moves.copy()
                                currentMoves.append(PlaceAction(*newState[1]))

                                #Checks whether a row or column needs to be cleared due to a completion
                                for block in newState[1]:
                                    if rowBlocksFilled(newBoard, block.r) == BOARD_SIZE and block.r != target.r:
                                        for c in range(BOARD_SIZE):
                                            newBoard.pop(Coord(block.r, c))
                                    if colBlocksFilled(newBoard, block.c) == BOARD_SIZE and block.c != target.c:
                                        for r in range(BOARD_SIZE):
                                            newBoard.pop(Coord(r, block.c))
                                current_target = target

                                newCost = totalCost + 1

                                # The smaller the priority number is the better it is to expand upon
                                priority = newCost + (estimatePiecesRemain(newBoard, current_target))
                                priority = priority + 0.25 * shortestDistance(newBoard, current_target)
                                
                                
                                if rowBlocksFilled(newBoard, target.r) == BOARD_SIZE or colBlocksFilled(newBoard, target.c) == BOARD_SIZE:
                                        return currentMoves
                                
                                MVheappush(pq.queue, (priority, newBoard, newCost, currentMoves))

    return None

def rowBlocksFilled(board: dict[Coord, PlayerColor], rowIndex: int):
    """
    Checks how many blocks in the targeted row are filled
    """
    filled = 0
    for i in range(BOARD_SIZE):
        if (board.get(Coord(rowIndex, i)) != None):
            filled += 1
    return filled

def colBlocksFilled(board: dict[Coord, PlayerColor], columnIndex: int):
    """
    Checks how many blocks in the targeted column are filled
    """
    filled = 0
    for i in range(BOARD_SIZE):
        if (board.get(Coord(i, columnIndex)) != None):
            filled += 1
    return filled

def addMove(piece: list[Vector2], board: dict[Coord, PlayerColor], placePosition: Coord, translation: Vector2):
    """
    Adds specific piece to the board (need to allow for moving in negative direction next after testing)
    """
    coords = []
    updatedBoard = board.copy()
    relativePosition = placePosition - translation
    for vector in piece:
        updatedBoard[relativePosition + vector] = PlayerColor.RED
        coords.append(relativePosition + vector)
    return (updatedBoard, tuple(coords))

def shortestDistance(board: dict[Coord, PlayerColor], target: Coord):
    """
    Finds the closest block to the target in terms of Manhatten distance
    """
    min_dist = BOARD_SIZE + BOARD_SIZE
    
    for piece in board:
        if board.get(piece) == PlayerColor.RED:
                column_dist = abs(target.c - piece.c)
                row_dist = abs(target.r - piece.r)
                if(row_dist + column_dist <= min_dist):
                        min_dist = row_dist + column_dist
                        
    return min_dist

def estimatePiecesRemain(board: dict[Coord, PlayerColor], target:Coord):
    """
    Estimates how many pieces still need to be placed to clear the target's row/column
    """
    rowPieceLeft = rowEstimatePiecesRemain(board, target)
    columnPieceLeft = colEstimatePiecesRemain(board, target)

    #Checks whether a block can't be accessed in the column
    checkCol = BlockedTargetCol(board, target)

    if checkCol[0] == True:

        #checks which the row above/below or column left/right will take the least blocks to give access to target column
        rows = min(rowEstimatePiecesRemain(board, Coord(checkCol[1], target.c).up()), rowEstimatePiecesRemain(board, Coord(checkCol[2], target.c)))
        columns = min(colEstimatePiecesRemain(board, target.left()), colEstimatePiecesRemain(board, target.right()))
        columnPieceLeft += min(rows, columns)

    #Checks whether a block can't be accessed in the row
    checkRow = BlockedTargetRow(board, target)

    if checkRow[0] == True:

        #checks which the row above/below or column left/right will take the least blocks to give access to target row
        rows = min(rowEstimatePiecesRemain(board, target.up()), rowEstimatePiecesRemain(board, target.down()))
        columns = colEstimatePiecesRemain(board, Coord(target.r, checkRow[1]).left()) + colEstimatePiecesRemain(board, Coord(target.r, checkRow[2]))
        rowPieceLeft += min(rows, columns)
   
    return min(columnPieceLeft, rowPieceLeft)

def BlockedTargetRow(board: dict[Coord, PlayerColor], target: Coord):
    """
    Checks if a blocks in a row cannot be currently reached
    """
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

def BlockedTargetCol(board: dict[Coord, PlayerColor], target: Coord): 
    """
    Checks if a blocks in a column cannot be currently reached
    """
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

def rowEstimatePiecesRemain(board: dict[Coord, PlayerColor], target:Coord):
    """
    Estimates how many pieces we must place to clear the target's row 
    """
    rowPieceLeft = 0
    count = 0
    check = 0

    for i in range(BOARD_SIZE):

        # If a block is in the path
        if (board.get(Coord(target.r, i)) != None):

            # Check if another block can be placed
            if (check != 0 and (check % PIECE_LENGTH != 0 )):   
                rowPieceLeft += 1

            check = 0
            count = 0
            continue

        else:
            check += 1
        
        # If the board has a blank space
        if board.get(Coord(target.r, i )) == None:
                    count += 1

        # Check if the piece blocks have all been placed
        if(count == PIECE_LENGTH):
            rowPieceLeft += 1
            count = 0
            check = 0
    if(check > 0 and check % PIECE_LENGTH != 0):
        rowPieceLeft += 1
  
    return rowPieceLeft

def colEstimatePiecesRemain(board: dict[Coord, PlayerColor], target: Coord):
    """
    Estimates how many pieces we must place to clear the target's column
    """
    columnPieceLeft = 0
    count = 0
    check = 0
    for i in range(BOARD_SIZE):

        # If a block is in the path
        if (board.get(Coord(i, target.c)) != None ):

            # Check if another block can be placed
            if (check != 0 and (check % PIECE_LENGTH != 0 )):
                columnPieceLeft += 1

            check = 0
            count = 0
            continue

        else:
            check += 1

        # If the board has a blank space
        if board.get(Coord(i, target.c)) == None:
                    count += 1

        # Check if the piece blocks have all been placed
        if(count == PIECE_LENGTH):
            columnPieceLeft += 1
            count = 0
            check = 0
    if(check > 0 and check % PIECE_LENGTH != 0):
        columnPieceLeft += 1

    return columnPieceLeft

def isValidTranslation(piece: list[Vector2], translation: Vector2):
    """
    Checks if the specific piece can be translated the way described in 'translation'
    """
    if(translation in piece):
        return True
    return False

def isValidPosition(board: dict[Coord, PlayerColor], piece: list[Vector2], placePosition: Coord):
    """
    Checks if the position and translation of the piece does not overlap with any red or blue block
    """
    for block in piece:
        if (placePosition + block) in board:
            return False

    return True

def isValidSquare(board: dict[Coord, PlayerColor], square: Coord):
    """
    Checks if the square is adjacent to a red block
    """
    if square in board:
        return False

    for translation in (Direction.Up(), Direction.Down(), Direction.Left(), Direction.Right()):
        if square + translation in board and board[square + translation] == PlayerColor.RED:
            return True

    return False



# (0,0) is the top most piece (leftmost if multiple in the same row). This is for consistency

def straightVerticalBlock():
    return (Vector2(0,0), Vector2(1, 0), Vector2(2, 0), Vector2(3, 0))
def straightHorizontalBlock():
    return (Vector2(0, 0), Vector2(0, 1), Vector2(0, 2), Vector2(0, 3))

def squareBlock():
    return(Vector2(0,0), Vector2(0,1), Vector2(1,0), Vector2(1,1))

# 'Up' Rotation Relative to T shape
def TBlockLeft():
    return(Vector2(0,0), Vector2(1,0), Vector2(2,0), Vector2(1,1))
def TBlockUp():
    return(Vector2(0,0), Vector2(0,1), Vector2(0,2), Vector2(1,1))
def TBlockDown():
    return(Vector2(0,0), Vector2(1,-1), Vector2(1,0), Vector2(1,1))
def TBlockRight():
    return(Vector2(0,0), Vector2(1,0), Vector2(2,0), Vector2(1, -1))

# 'Up' Rotation Relative to L shape
def LBlockUp():
    return(Vector2(0,0), Vector2(1,0), Vector2(2,0), Vector2(2,1))
def LBlockRight():
    return(Vector2(0,0), Vector2(0,1), Vector2(0,2), Vector2(1,0))
def LBlockDown():
    return(Vector2(0,0), Vector2(0,1), Vector2(1,1), Vector2(2,1))
def LBlockLeft():
    return(Vector2(0,0), Vector2(1,0), Vector2(1,-1), Vector2(1,-2))

# 'Up' Rotation Relative to J shape
def JBlockRight():
    return(Vector2(0,0), Vector2(1,0), Vector2(1,1), Vector2(1,2))
def JBlockDown():
    return(Vector2(0,0), Vector2(0,1), Vector2(1,0), Vector2(2,0))
def JBlockLeft():
    return(Vector2(0,0), Vector2(0,1), Vector2(0,2), Vector2(1,2))
def JBlockUp():
    return(Vector2(0,0), Vector2(1,0), Vector2(2,0), Vector2(2,-1))

# Horizonal spans 3 across, 2 up. Vice versa for Vertical
def ZBlockHorizontal():
    return(Vector2(0,0), Vector2(0,1), Vector2(1,1), Vector2(1,2))
def ZBlockVertical():
    return(Vector2(0,0), Vector2(1,0), Vector2(1, -1), Vector2(2, -1))
def SBlockVertical():
    return(Vector2(0,0), Vector2(1,0), Vector2(1,1), Vector2(2,1))
def SBlockHorizontal():
    return(Vector2(0,0), Vector2(0,1), Vector2(1,0), Vector2(1,-1))


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
    childpos = 2*pos + 1
    while childpos < endpos:
        rightpos = childpos + 1
        if rightpos < endpos and not heap[childpos][0] < heap[rightpos][0]:
            childpos = rightpos
        heap[pos] = heap[childpos]
        pos = childpos
        childpos = 2*pos + 1
    heap[pos] = newitem
    MVsiftdown(heap, startpos, pos)

# Adapted from heapq.py to allow for comparison of priority but storage of a tuple
def MVheappush(heap, item):
    heap.append(item)
    MVsiftdown(heap, 0, len(heap)-1)

# Adapted from heapq.py to allow for comparison of priority but storage of a tuple
def MVheappop(heap):
    lastelt = heap.pop()
    if heap:
        returnitem = heap[0]
        heap[0] = lastelt
        MVsiftup(heap, 0)
        return returnitem
    return lastelt