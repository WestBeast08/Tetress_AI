# COMP30024 Artificial Intelligence, Semester 1 2024
# Project Part A: Single Player Tetress

from contextlib import nullcontext
from .core import PlayerColor, Coord, PlaceAction,  Direction, Vector2
from .utils import render_board
from dataclasses import dataclass
from enum import Enum
from queue import PriorityQueue
BOARD_SIZE = 11 




@dataclass(slots = True)
class Moves:
     """
     This is the class to store a list of moves taken and the current state the board is 
     after those moves. Along with this, it tracks how many blocks in the targeted block
     row/column is filled. 
     """
     board: dict[Coord, PlayerColor]
     actions: list[PlaceAction]
     numBlocksFilledCol: int 
     numBlocksFilledRow: int



def search(
    board: dict[Coord, PlayerColor], 
    target: Coord
) -> list[PlaceAction] | None:
    print(render_board(board, target, ansi=True))
    """
    This is the entry point for your submission. You should modify this
    function to solve the search problem discussed in the Part A specification.
    See `core.py` for information on the types being used here.

    Parameters:
        `board`: a dictionary representing the initial board state, mapping
            coordinates to "player colours". The keys are `Coord` instances,
            and the values are `PlayerColor` instances.  
        `target`: the target BLUE coordinate to remove from the board.
    
    Returns:
        A list of "place actions" as PlaceAction instances, or `None` if no
        solution is possible.
    """
   
    # The render_board() function is handy for debugging. It will print out a
    # board state in a human-readable format. If your terminal supports ANSI
    # codes, set the `ansi` flag to True to print a colour-coded version!
    
    '''
    Occurs when queue is empty
    return none 
    '''
                #Get block
                #Check block can be placed
                #If so put block
                #Check if it completes the target row
                #If yes, return
                #if not, add it to the queue
                #Else continue
                #move the block up, down etc to see another valid condition
    #Need to do
    #Make sure queue works
    #make sure the board being copied worked
    #Make sure that this continues more than one loop and that it is being stored correctly in the nodes
    #If not queue:
    # return none
    queue = []
    startingPosition = Moves(board, [], 0, 0)
    queue.append(node)
    blocks = [
    straightVerticalBlock(),
    straightHorizontalBlock(), 
    squareBlock(), 
    JBlock(), 
    JBlockDown(), 
    JBlockRight(), 
    JBlockUp(),
    LBlockUp(),
    LBlockRight(),
    LBlockDown(),
    LBlockLeft(),
    TBlock(),
    TBlockLeft(),
    TBlockUp(),
    Tblockdown(),
    ZBlock(), 
    ZBlockVertical(),
    SBlock(),
    SBlockHorizontal()
]
    y_direction = 1
    x_direction = 1
    #While the queue isn't empty
    while len(queue) != 0:
        #Pop the first node from the list
        state = queue.pop(0)
        #Find the closest red block to the target
        closest = find_closestCR(state.board, target)
        #Find which sides can be extend on 
        valid_space = checkSides(state.board, closest[0])
        #For each side that a block can be placed 
        for a in valid_space:
            if (a == Direction.Up):
                y_direction *= -1
            if(a == Direction.Left):
                x_direction *= -1
            #For every block type
            for block in blocks:
                can_place = True
                current = state.board.copy()
                block_placed = []
                for c in block:
                    #Modifies the coordinates base on direction 
                    modified_c = Vector2(c.r * y_direction, c.c * x_direction)
                    place = Coord.__add__(valid_space[a], modified_c)
                    #checks whether a block can be placed there and no other blocks are in that location
                    if (current.get(place, None) != None):
                        can_place = False
                    block_placed.append(place)
                    #put blocks on the board
                if (can_place == True):
                    
                    for completed in block_placed:
                        current[completed] = PlayerColor.RED
                    #Writes the information to the node and puts it back into the list
                    actions = state.actions.copy()
                    actions.append(PlaceAction(*block_placed.copy()))
                    
                    if (rowBlocksFilled(current, target.c) == BOARD_SIZE or columnBlocksFilled(current, target.r) == BOARD_SIZE):
                        print(render_board(current, target, ansi=True))
                        return actions
                    #the 0, 0 are placeholders for values we might use for heuristics
                    queue.append(Moves(current.copy(), actions, 0, 0))
                    
                    
                #Currently working on getting all possibilities with the block
                alternate = check_possibilities(state, target, closest[0], valid_space[a], block_placed, a)
                for node in alternate:
                    if (rowBlocksFilled(current, target.c) == BOARD_SIZE or columnBlocksFilled(current, target.r) == BOARD_SIZE):
                        print(render_board(current, target, ansi=True))
                        return actions
                    else:
                        queue.append(node)
            y_direction = 1
            x_direction = 1
    return None
    
    # return [
    #     PlaceAction(Coord(2, 5), Coord(2, 6), Coord(3, 6), Coord(3, 7)),
    #     PlaceAction(Coord(1, 8), Coord(2, 8), Coord(3, 8), Coord(4, 8)),
    #     PlaceAction(Coord(5, 8), Coord(6, 8), Coord(7, 8), Coord(8, 8)),
    # ]

def rowBlocksFilled(board: dict[Coord, PlayerColor], rowIndex: Coord):
    """
    Checks whether the row has been completely filled
    """
    filled = 0
    for i in range(11):
        if (board.get(Coord(i, rowIndex), None) != None):
            filled += 1
    return filled

def columnBlocksFilled(board: dict[Coord, PlayerColor], columnIndex: Coord):
    """
    Checks whether the column has been completely filled
    """
    filled = 0
    for i in range(11):
        if (board.get(Coord(columnIndex, i), None) != None):
            filled += 1
    return filled

def checkSides(board: dict[Coord, PlayerColor], check: Coord):
    directions = {}
    
    for value in Direction:
        checking = Coord.__add__(check, value)
        if (board.get(checking, None) == None):
            directions[value] = checking
    return directions

def find_closestCR(board, target):
    min_dist = BOARD_SIZE + BOARD_SIZE
    closest_piece = nullcontext
    is_column = False
    for piece in board:
        if board[piece] == PlayerColor.RED:
            column_dist = abs(target.c - piece.c)
            row_dist = abs(target.r - piece.r)
            if (column_dist + row_dist < min_dist):
                min_dist = column_dist + row_dist
                if column_dist < row_dist:
                    is_column = True
                else:
                    is_column = False
                closest_piece = piece

    return (closest_piece, is_column)

def check_possibilities(state: Moves, target: Coord,  build_upon: Coord, valid_spot: Coord, blockCoords: list[Coord], direction: Direction):
    #For directions 
    #move the placed block coords in the direction
    #Based on length/height of block
    #Check if it has the valid spot coord in that list
    #Also check if it didn't delete any blocks
    #If it doesn't break
    #Needs to be check if working with all pieces
    rCol = []
    cCol = []
    confirmed = []
    #Checks height and width of block
    for i in blockCoords:
        rCol.append(i.r)
        cCol.append(i.c)
    rUnique = set(rCol).__len__()
    cUnique = set(cCol).__len__()
    #directions based on what direction we are expanding 
    if (direction == Direction.Up or direction == Direction.Down):
        numBlocks = cUnique
        freq = 0
        for i in blockCoords:
            if (i.c == valid_spot.c):
                freq += 1
                
        directions = [Direction.Left, Direction.Right]
        
    else:
        numBlocks = rUnique
        freq = 0
        for i in blockCoords:
            if (i.r == valid_spot.r):
                freq += 1
    
        directions = [Direction.Up, Direction.Down]
    #Based on the directions avaliable
    for d in directions:
        
        #Copy a board
        checkCoord = blockCoords.copy()
        
        #For the number of tiles we can move
        for i in range(1, numBlocks):
            newBoard = state.board.copy()
            for j in range(len(blockCoords)):
               
                checkCoord[j] = checkCoord[j] + d
            
            checkNum = 0
            #checks if there is a gap when there is not supposed to or is in blocks that is not supposed to be
            if (d == Direction.Up or d == Direction.Down):
                for check in checkCoord:
                    if (check.r == valid_spot.r):
                         checkNum = checkNum + 1  
                if((valid_spot not in checkCoord ) and checkNum != 0 or build_upon in blockCoords):
                    if (abs(checkNum - freq) == 0):
                        multiplier = 1
                    else:
                        multiplier = abs(checkNum - freq)
                    if build_upon in checkCoord:
                        for i in range(len(checkCoord)):
                                checkCoord[i] = checkCoord[i] + (direction * multiplier)
                    else:
                        for i in range(len(checkCoord)):
                                checkCoord[i] = checkCoord[i] + (direction * multiplier * -1)
                  
            else:
                for check in checkCoord:
                    if (check.c == valid_spot.c):
                        checkNum = checkNum + 1
                    
                if(((valid_spot not in checkCoord)) and checkNum != 0 or build_upon in checkCoord):
                    if (abs(checkNum - freq) == 0):
                            multiplier = 1
                    else:
                            multiplier = abs(checkNum - freq)
                    if build_upon in checkCoord:
                        for i in range(len(checkCoord)):
                                checkCoord[i] = checkCoord[i] + (direction * multiplier)
                    else:
                        for i in range(len(checkCoord)):
                            checkCoord[i] = checkCoord[i] + (direction * multiplier * -1)
            #Checks if the original valid spot was there  
            can_place = True
           
            if (valid_spot in checkCoord):
                for coord in checkCoord:
                    if(state.board.get(coord, None) != None):
                        can_place = False
                        break

                if(can_place == True):
                    for completed in checkCoord:
                        newBoard[completed] = PlayerColor.RED  
                    actions = state.actions.copy()
                    actions.append(PlaceAction(*checkCoord.copy()))
                    
                    confirmed.append(Moves(newBoard, actions, 0, 0))
        
    return confirmed


#Probably not applicable since I forgot we have a reoccuring grid
'''
def isValidPosition(piece: list[Vector2], board: dict[Coord, PlayerColor], placePosition: Coord):
    for vector in piece:
        if(placePosition.add(Coord(vector.r, vector.c)) > BOARD_SIZE and placePosition.add(Coord(vector.r, vector.c)) < 0):
            return False
        if(board[placePosition.add(Coord(vector.r, vector.c))]) != None:
            return False
    return True
'''

# Make sure move is valid at placePosition before calling function
def addMove(piece: list[Vector2], board: dict[Coord, PlayerColor], placePosition: Coord, translation: Coord):
    '''
    Adds specific piece to the board (need to allow for moving in negative direction next after testing)
    '''
    updatedBoard = board.copy()
    relativePosition = pieceTranslation(piece, placePosition, translation)
    for vector in piece:
        updatedBoard[relativePosition.add(Coord(vector.r, vector.c))] = PlayerColor.RED
    return updatedBoard

def filledHeuristic(board: dict[Coord, PlayerColor], target: Coord):
    return rowBlocksFilled(board, target) + columnBlocksFilled(board, target)

# Assume that (0, 0) is the base position of a piece. None return means specified translation is out of bounds of the piece
def pieceTranslation(piece: list[Vector2], placePosition: Coord, translation: Coord):
    if(translation in piece):
        return placePosition + translation
    return None


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



def aStarSearch(board: dict[Coord, PlayerColor], target: Coord):
    '''
    Uses a built-in priority queue storing the heuristic value, board, and total cost of the current state
    (more description once finished)
    '''
    pq = PriorityQueue()
    initialCost = 0
    pq.put((filledHeuristic(board, target), board, initialCost))
    
    while not pq.empty():
        heuristic, currentBoard, totalCost = pq.get()

        if rowBlocksFilled(currentBoard, target) == BOARD_SIZE or columnBlocksFilled(currentBoard, target) == BOARD_SIZE:
            return (currentBoard, totalCost)
        
        # now just need to loop over all possible moves for cost calculations

        #for row in range(BOARD_SIZE):
            #for col in range(BOARD_SIZE):
                #if square is not a valid placement (ie not next to another red square):
                    #continue
        
                # Most likely need a list of all pieces. (is quite easy but in what format?)

                #for each piece: (we already have rotations represented as seperate pieces)
                    #for each translation: (any block in a piece can be the a candidate to go in placePosition)
        
                        #placePosition = Coord(col, row)
        
                        # checking for validity in terms of blocks in the way (check_possibilities probably has the right framework)
                        #if isValidPosition(piece, currentBoard, placePosition):
        
                            # havent figured out the logistics of the priority part but it should look something like this
        
                            #newBoard = addMove(piece, currentBoard, placePosition)
                            #newCost = totalCost + 1
                            #priority = newCost + filledHeuristic(newBoard, target)
                            #pq.put((priority, newBoard, totalCost))

    return (None, None)

