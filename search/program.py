# COMP30024 Artificial Intelligence, Semester 1 2024
# Project Part A: Single Player Tetress

from contextlib import nullcontext
from .core import PlayerColor, Coord, PlaceAction,  Direction, Vector2
from .utils import render_board
from dataclasses import dataclass
from enum import Enum
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


    #If not queue:
    # return none
    queue = []
    node = Moves(board, [], 0, 0)
    queue.append(node)
    blocks = [
    straightHorizontalBlock(),
    straightVerticalBlock(),
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
    while queue:
        #Pop the first node from the list
        state = queue.pop(0)
        #Find the closest red block to the target
        closest = find_closestCR(board, target)
        #Find which sides can be extend on 
        valid_space = checkSides(board, closest[0])
        
        #For each side that a block can be placed 
        for a in valid_space:
            if (a == Direction.Up):
                y_direction *= -1
            
            if(a == Direction.Left):
                x_direction *= -1
            #For every block type
            for block in blocks:
                current = board.copy()
                block_placed = []
                for c in block:
                    modified_c = Vector2(c.r * y_direction, c.c * x_direction)
                    place = Coord.__add__(valid_space[a], modified_c)
                    #checks whether a block can be placed there and no other blocks are in that location
                    if (current.get(place, None) != None):
                        block_placed.clear()
                        break
                        
                    else:
                        block_placed.append(place)
                    #put blocks on the board
                for completed in block_placed:
                    
                    current[completed] = PlayerColor.RED
                
                print(render_board(current, target, ansi=True))
            y_direction = 1
            x_direction = 1
                    

                
    return [
        PlaceAction(Coord(2, 5), Coord(2, 6), Coord(3, 6), Coord(3, 7)),
        PlaceAction(Coord(1, 8), Coord(2, 8), Coord(3, 8), Coord(4, 8)),
        PlaceAction(Coord(5, 8), Coord(6, 8), Coord(7, 8), Coord(8, 8)),
    ]

def rowCompleted(board: dict[Coord, PlayerColor], rowIndex: Coord):
    """
    Checks whether the row has been completely filled
    """
    for i in range(11):
        if (board.get(Coord(i, rowIndex), None) == None):
            return False
    return True

def columnCompleted(board: dict[Coord, PlayerColor], columnIndex: Coord):
    """
    Checks whether the column has been completely filled
    """
    for i in range(11):
        if (board.get(Coord(columnIndex, i), None) == None):
            return False
    return True

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

def TBlock():
    """
    Provides coordinates for a generical shape of a T Block
    """
    return[Vector2(0,0), Vector2(1,0), Vector2(2,0), Vector2(1,1)]
def LBlockUp():
    """
    Provides coordinates for a generical shape of a L block
    """
    return[Vector2(0,0), Vector2(1,0), Vector2(2,0), Vector2(2,1)]
def JBlock():
    """
    Provides coordinates for a generical shape of a J block
    """
    return[Vector2(0,0), Vector2(1,0), Vector2(1,1), Vector2(1,2)]
def ZBlock():
    """
    Provides coordinates for a generical shape of a Z block
    """
    return[Vector2(0,0), Vector2(0,1), Vector2(1,1), Vector2(1,2)]

def SBlock():
    """
    Provides coordinates for a generical shape of a S block
    """
    return[Vector2(0,0), Vector2(1,0), Vector2(1,1), Vector2(2,1)]

#All are the variation of above blocks 

def Tblockdown():
    return[Vector2(0,0), Vector2(0,1), Vector2(0,2), Vector2(1,1)]


def JBlockDown():
    return[Vector2(0,0), Vector2(0,1), Vector2(1,0), Vector2(2,0)]

def JBlockRight():
    return[Vector2(0,0), Vector2(0,1), Vector2(0,2), Vector2(1,2)]

def LBlockRight():
    return[Vector2(0,0), Vector2(0,1), Vector2(0,2), Vector2(1,0)]

def LBlockDown():
    return[Vector2(0,0), Vector2(0,1), Vector2(1,1), Vector2(2,1)]

def LBlockLeft():
    return[Vector2(0,0), Vector2(0,1), Vector2(0,2), Vector2(-1, 2)]

def TBlockUp():
    return[Vector2(0,0), Vector2(0,1), Vector2(0,2), Vector2(-1,1)]

def TBlockLeft():
    return[Vector2(0,0), Vector2(1,0), Vector2(2,0), Vector2(1, -1)]

def ZBlockVertical():
    return[Vector2(0,0), Vector2(1,0), Vector2(1, -1), Vector2(2, -1)]

def SBlockHorizontal():
    return[Vector2(0,0), Vector2(0,1), Vector2(-1,1), Vector2(-1,2)]
def JBlockUp():
    return[Vector2(0,0), Vector2(0,1), Vector2(-1, 1), Vector2(-2, 1)]


def checkSides(board: dict[Coord, PlayerColor], check: Coord):
    directions = {}
    
    for value in Direction:
        checking = Coord.__add__(check, value)
        if (board.get(checking, None) == None):
            directions[value] = checking
    return directions

def find_closestCR(board, target):
    min_dist = BOARD_SIZE
    closest_piece = nullcontext
    is_column = False
    for piece in board:
        if board[piece] == PlayerColor.RED:
            column_dist = abs(target.c - piece.c)
            row_dist = abs(target.r - piece.r)
            if (column_dist or row_dist) < min_dist:
                min_dist = min(column_dist, row_dist)
                if column_dist < row_dist:
                    is_column = True
                else:
                    is_column = False
                closest_piece = piece

    return [closest_piece, is_column]