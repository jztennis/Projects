from chess import *
import copy

col = ['z','a','b','c','d','e','f','g','h','i']
row = [0,1,2,3,4,5,6,7,8,9]

def checkBoardState(prev, cur):
    if prev == cur:
        return True
    else:
        return False

# Test Pawn Moves
board = ChessBoard()
print('PAWN TEST')
# Bad Moves
for c in col:
    for r in row:
        prev_board = copy.deepcopy(board)
        if r != 3 and r != 4:
            board.move(f'p{c}2{c}{r}', 'W')
            if not checkBoardState(prev_board.board, board.board):
                print(f'The Move p{c}2{c}{r} FAILED')
            board.move(f'p{c}2{c}{r}', 'B')
            if not checkBoardState(prev_board.board, board.board):
                print(f'The Move p{c}2{c}{r} FAILED')

# Test Rook Moves

# Test Knight Moves

# Test Bishop Moves

# Test Queen Moves

# Test King Moves

# Test Checkmate