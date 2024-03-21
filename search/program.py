# COMP30024 Artificial Intelligence, Semester 1 2024
# Project Part A: Single Player Tetress

from .core import PlayerColor, Coord, PlaceAction,  Direction
from .utils import render_board
from collections import deque

BOARD_SIZE = 11 

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
    print(render_board(board, target, ansi=True))

    # Do some impressive AI stuff here to find the solution...
    # ...
    # ... (your solution goes here!)
    # ...

    # Here we're returning "hardcoded" actions as an example of the expected
    # output format. Of course, you should instead return the result of your
    # search algorithm. Remember: if no solution is possible for a given input,
    # return `None` instead of a list.
    queue = []
    

    #If not queue:
    # return none
    
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
    return [Coord(1,0), Coord(2, 0), Coord(3, 0), Coord(4, 0)]
    
def straightHorizontalBlock():
    """
    Provides coordinates for a generical shape of a straight Horizontal block
    """
    return [Coord(0, 1), Coord(0, 2), Coord(0, 3), Coord(0, 4)]

def squareBlock():
    """
    Provides coordinates for a generical shape of Square block
    """
    return[Coord(1,0), Coord(2,0), Coord(1,1), Coord(2,1)]

def TBlock():
    """
    Provides coordinates for a generical shape of a T Block
    """
    return[Coord(1,0), Coord(2,0), Coord(3,0), Coord(2,1)]
def LBlock():
    """
    Provides coordinates for a generical shape of a L block
    """
    return[Coord(1,0), Coord(2,0), Coord(1,1), Coord(1,2)]
def JBlock():
    """
    Provides coordinates for a generical shape of a J block
    """
    return[Coord(1,0), Coord(2,0), Coord(2,1), Coord(2,2)]
def ZBlock():
    """
    Provides coordinates for a generical shape of a Z block
    """
    return[Coord(1,0), Coord(1,1), Coord(2,1), Coord(2,2)]



def checkSides(board: dict[Coord, PlayerColor], check: Coord):
    directions = []
    for value in Direction:
        checking = Coord.__add__(check, value)
        if (board.get(checking, None) == None):
            directions.append(checking)
    return directions
