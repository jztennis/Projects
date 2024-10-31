from colorama import Fore, Back, Style

# Knight = N
# King = K
# Queen = Q
# Bishop = B
# Rook = R
# Pawn = p

class ChessBoard:
    """Stores the Chessboard"""
    board = []

    def __init__(self):
        self.board = [
        ['BR', 'BN', 'BB', 'BQ', 'BK', 'BB', 'BN', 'BR'],
        ['Bp', 'Bp', 'Bp', 'Bp', 'Bp', 'Bp', 'Bp', 'Bp'],
        ['' , '' , '' , '' , '' , '' , '' , '' ],
        ['' , '' , '' , '' , '' , '' , '' , '' ],
        ['' , '' , '' , '' , '' , '' , '' , '' ],
        ['' , '' , '' , '' , '' , '' , '' , '' ],
        ['Wp', 'Wp', 'Wp', 'Wp', 'Wp', 'Wp', 'Wp', 'Wp'],
        ['WR', 'WN', 'WB', 'WQ', 'WK', 'WB', 'WN', 'WR']]

    def printBoard(self):
        for i in range(len(self.board)):
            print('  +---+---+---+---+---+---+---+---+')
            print(f'{8-i} |', end=' ')
            for ii in range(len(self.board[i])):
                if self.board[7-i][ii] == '':
                    print(' ', '|', end=' ')
                elif self.board[7-i][ii][0] == 'B':
                    print(Fore.WHITE+self.board[7-i][ii][1], '|', end=' ')
                else:
                    print(Fore.GREEN+self.board[7-i][ii][1], Fore.WHITE+'|', end=' ')
            print()
        print('  +---+---+---+---+---+---+---+---+')
        print('    a   b   c   d   e   f   g   h')

    def checkKing(self):
        t1 = False
        t2 = False
        for i in range(len(self.board)):
            for ii in range(len(self.board[i])):

                if self.board[i][ii] != '' and self.board[i][ii][1] == 'K':
                    if self.board[i][ii][0] == 'B':
                        t1 = True
                    elif self.board[i][ii][0] == 'W':
                        t2 = True
        if not t1:
            return 'Black'
        elif not t2:
            return 'White'
        else:
            return True
        
    def checkMove(self, move, color):
        # print(ord(move[1]))
        # Pawn?
        if move[0] == 'p':
            # Is it White's Move? (Values will always be 'W' or 'B' because it is from program rather than user)
            if color == 'W':
                # not taking a piece
                if move[1] == move[3]:
                    print('Same file')
                    if int(move[2]) == 2 and int(move[4]) < 5 and int(move[4]) > 2:
                        return True
                    else:
                        return False
                # taking a piece (middle board)
                elif ord(move[1])-97 != 0 and ord(move[1])-97 != 7:
                    if ord(move[1])-96 == ord(move[3]) or ord(move[1])-98 == ord(move[3]):
                        if int(move[2])+1 == move[4]:
                            if self.board[move[3]][move[4]] != '':
                                return True
                            else:
                                return False
                        else:
                            return False
                    else:
                        return False
                # taking a piece on the a file
                elif ord(move[1])-97 == 0:
                    if ord(move[1])-96 == ord(move[3]):
                        return True
                    else:
                        return False
                # taking a piece on the h file
                elif ord(move[1])-97 == 7:
                    if ord(move[1])-98 == ord(move[3]):
                        return True
                    else:
                        return False
                else:
                    return False
            elif color == 'B':
                # not taking a piece
                if move[1] == move[3]:
                    if int(move[2]) == 7 and int(move[4]) < 7 and int(move[4]) > 4:
                        return True
                    else:
                        return False
                # taking a piece (middle board)
                elif ord(move[1])-97 != 0 and ord(move[1])-97 != 7:
                    if ord(move[1])-96 == ord(move[3]) or ord(move[1])-98 == ord(move[3]):
                        if int(move[2])+1 == move[4]:
                            if self.board[move[3]][move[4]] != '':
                                return True
                            else:
                                return False
                        else:
                            return False
                    else:
                        return False
                # taking a piece on the a file
                elif ord(move[1])-97 == 0:
                    if ord(move[1])-96 == ord(move[3]):
                        return True
                    else:
                        return False
                # taking a piece on the h file
                elif ord(move[1])-97 == 7:
                    if ord(move[1])-98 == ord(move[3]):
                        return True
                    else:
                        return False
                else:
                    return False
        # Rook?
        elif move[0] == 'R':
            if move[1] == move[3] and move[2] < move[4]:
                for i in range(8-int(move[2])):
                    if i != int(move[2])-1:
                        if i == int(move[4])-1:
                            return True
                        elif self.board[i+int(move[2])][ord(move[1])-97] != '':
                            return False
            elif move[1] == move[3] and move[2] > move[4]:
                for i in range(int(move[2])):
                    if int(move[2])-1-i != int(move[2])-1:
                        if int(move[2])-1-i == int(move[4])-1:
                            return True
                        elif self.board[int(move[2])-i][ord(move[1])-97] != '':
                            return False
            elif move[1] < move[3] and move[2] == move[4]:
                pass
            elif move[1] > move[3] and move[2] == move[4]:
                pass
            else:
                return False
        # Knight?
        elif move[0] == 'N':
            pass
        # Bishop?
        elif move[0] == 'B':
            pass
        # Queen?
        elif move[0] == 'Q':
            pass
        # King?
        elif move[0] == 'K':
            pass
        # No pieces left
        else:
            print('Invalid Piece')
            return False

    def move(self, move, color):
        if int(move[2]) <= 8 and int(move[2]) >= 1 and int(move[4]) <= 8 and int(move[4]) >= 1:
            if self.checkMove(move, color):
                temp = self.board[int(move[2])-1][ord(move[1])%97]
                self.board[int(move[2])-1][ord(move[1])%97] = ''
                self.board[int(move[4])-1][ord(move[3])%97] = temp
                return False
            else:
                return True
        else:
            return True