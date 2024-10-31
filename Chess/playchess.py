from chess import *

board = ChessBoard()
print("\nExample Moves: 'Ke1e2', 'Ne1f3'", "\n")
count = 0

while board.checkKing():
    board.printBoard()
    move = input('\nWhite Move?')
    color = 'W'
    while board.move(move, color):
        print("Can't move there.")
        move = input('White Move?')

    if board.checkKing():
        board.printBoard()
        move = input('\nBlack Move?')
        color = 'B'
        while board.move(move, color):
            print("Can't move there.")
            move = input('Black Move?')
    else:
        break

board.printBoard()
print(board.checkKing(), 'loses.')