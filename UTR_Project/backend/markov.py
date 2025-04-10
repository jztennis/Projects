import numpy as np
import random
import pandas as pd
import time
import joblib
from network import TennisPredictor, get_prop, get_player_profiles, get_player_history
# from model import TennisPredictor
# from predict import get_player_profiles, get_player_history

'''
Need to recalculate 30-30(DEUCE) and HOLD/BREAK row
to account for changing probabilities.
'''

class MarkovModel:
    def __init__(self, prop):
        self.curr_state = '0-0'
        self.prop = prop
        if round(0.66*(0.5+prop),10)+round(1-(0.66*(0.5+prop)),10) == 1:
            self.pprop = round(0.66*(0.5+prop),10)
            self.inv_prop = round(1-(0.66*(0.5+prop)),10)
        else:
            self.pprop = round(0.66*(0.5+prop),10) + 0.0000000001
            self.inv_prop = round(1-(0.66*(0.5+prop)),10)
        self.deuce = round((self.pprop**2) / (1 - 2*self.pprop*self.inv_prop),10)
        self.inv_deuce = round(1-((self.pprop**2) / (1 - (2*self.pprop*self.inv_prop))),10)
        '''
        Assume that the below matrix taken from another study is correct.
        '''
        self.pt_matrix = {
            '0-0': {'0-0': 0, '0-15': self.inv_prop, '15-0': self.pprop, '15-15': 0, '0-30': 0, '30-0': 0, '15-30': 0, '30-15': 0, '0-40': 0, '40-0': 0, '15-40': 0, '40-15': 0, '30-30(DEUCE)': 0, '30-40(40-A)': 0, '40-30(A-40)': 0, '40-40(NO AD)': 0, 'HOLD': 0, 'BREAK': 0},
            '0-15': {'0-0': 0, '0-15': 0, '15-0': 0, '15-15': self.pprop, '0-30': self.inv_prop, '30-0': 0, '15-30': 0, '30-15': 0, '0-40': 0, '40-0': 0, '15-40': 0, '40-15': 0, '30-30(DEUCE)': 0, '30-40(40-A)': 0, '40-30(A-40)': 0, '40-40(NO AD)': 0, 'HOLD': 0, 'BREAK': 0},
            '15-0': {'0-0': 0, '0-15': 0, '15-0': 0, '15-15': self.inv_prop, '0-30': 0, '30-0': self.pprop, '15-30': 0, '30-15': 0, '0-40': 0, '40-0': 0, '15-40': 0, '40-15': 0, '30-30(DEUCE)': 0, '30-40(40-A)': 0, '40-30(A-40)': 0, '40-40(NO AD)': 0, 'HOLD': 0, 'BREAK': 0},
            '15-15': {'0-0': 0, '0-15': 0, '15-0': 0, '15-15': 0, '0-30': 0, '30-0': 0, '15-30': self.inv_prop, '30-15': self.pprop, '0-40': 0, '40-0': 0, '15-40': 0, '40-15': 0, '30-30(DEUCE)': 0, '30-40(40-A)': 0, '40-30(A-40)': 0, '40-40(NO AD)': 0, 'HOLD': 0, 'BREAK': 0},
            '0-30': {'0-0': 0, '0-15': 0, '15-0': 0, '15-15': 0, '0-30': 0, '30-0': 0, '15-30': self.pprop, '30-15': 0, '0-40': self.inv_prop, '40-0': 0, '15-40': 0, '40-15': 0, '30-30(DEUCE)': 0, '30-40(40-A)': 0, '40-30(A-40)': 0, '40-40(NO AD)': 0, 'HOLD': 0, 'BREAK': 0},
            '30-0': {'0-0': 0, '0-15': 0, '15-0': 0, '15-15': 0, '0-30': 0, '30-0': 0, '15-30': 0, '30-15': self.inv_prop, '0-40': 0, '40-0': self.pprop, '15-40': 0, '40-15': 0, '30-30(DEUCE)': 0, '30-40(40-A)': 0, '40-30(A-40)': 0, '40-40(NO AD)': 0, 'HOLD': 0, 'BREAK': 0},
            '15-30': {'0-0': 0, '0-15': 0, '15-0': 0, '15-15': 0, '0-30': 0, '30-0': 0, '15-30': 0, '30-15': 0, '0-40': 0, '40-0': 0, '15-40': self.inv_prop, '40-15': 0, '30-30(DEUCE)': self.pprop, '30-40(40-A)': 0, '40-30(A-40)': 0, '40-40(NO AD)': 0, 'HOLD': 0, 'BREAK': 0},
            '30-15': {'0-0': 0, '0-15': 0, '15-0': 0, '15-15': 0, '0-30': 0, '30-0': 0, '15-30': 0, '30-15': 0, '0-40': 0, '40-0': 0, '15-40': 0, '40-15': self.pprop, '30-30(DEUCE)': self.inv_prop, '30-40(40-A)': 0, '40-30(A-40)': 0, '40-40(NO AD)': 0, 'HOLD': 0, 'BREAK': 0},
            '0-40': {'0-0': 0, '0-15': 0, '15-0': 0, '15-15': 0, '0-30': 0, '30-0': 0, '15-30': 0, '30-15': 0, '0-40': 0, '40-0': 0, '15-40': self.pprop, '40-15': 0, '30-30(DEUCE)': 0, '30-40(40-A)': 0, '40-30(A-40)': 0, '40-40(NO AD)': 0, 'HOLD': 0, 'BREAK': self.inv_prop},
            '40-0': {'0-0': 0, '0-15': 0, '15-0': 0, '15-15': 0, '0-30': 0, '30-0': 0, '15-30': 0, '30-15': 0, '0-40': 0, '40-0': 0, '15-40': 0, '40-15': self.inv_prop, '30-30(DEUCE)': 0, '30-40(40-A)': 0, '40-30(A-40)': 0, '40-40(NO AD)': 0, 'HOLD': self.pprop, 'BREAK': 0},
            '15-40': {'0-0': 0, '0-15': 0, '15-0': 0, '15-15': 0, '0-30': 0, '30-0': 0, '15-30': 0, '30-15': 0, '0-40': 0, '40-0': 0, '15-40': 0, '40-15': 0, '30-30(DEUCE)': 0, '30-40(40-A)': self.pprop, '40-30(A-40)': 0, '40-40(NO AD)': 0, 'HOLD': 0, 'BREAK': self.inv_prop},
            '40-15': {'0-0': 0, '0-15': 0, '15-0': 0, '15-15': 0, '0-30': 0, '30-0': 0, '15-30': 0, '30-15': 0, '0-40': 0, '40-0': 0, '15-40': 0, '40-15': 0, '30-30(DEUCE)': 0, '30-40(40-A)': 0, '40-30(A-40)': self.inv_prop, '40-40(NO AD)': 0, 'HOLD': self.pprop, 'BREAK': 0},
            '30-30(DEUCE)': {'0-0': 0, '0-15': 0, '15-0': 0, '15-15': 0, '0-30': 0, '30-0': 0, '15-30': 0, '30-15': 0, '0-40': 0, '40-0': 0, '15-40': 0, '40-15': 0, '30-30(DEUCE)': 0, '30-40(40-A)': 0, '40-30(A-40)': 0, '40-40(NO AD)': 0, 'HOLD': self.deuce, 'BREAK': self.inv_deuce},
            '30-40(40-A)': {'0-0': 0, '0-15': 0, '15-0': 0, '15-15': 0, '0-30': 0, '30-0': 0, '15-30': 0, '30-15': 0, '0-40': 0, '40-0': 0, '15-40': 0, '40-15': 0, '30-30(DEUCE)': self.pprop, '30-40(40-A)': 0, '40-30(A-40)': 0, '40-40(NO AD)': 0, 'HOLD': 0, 'BREAK': self.inv_prop},
            '40-30(A-40)': {'0-0': 0, '0-15': 0, '15-0': 0, '15-15': 0, '0-30': 0, '30-0': 0, '15-30': 0, '30-15': 0, '0-40': 0, '40-0': 0, '15-40': 0, '40-15': 0, '30-30(DEUCE)': self.inv_prop, '30-40(40-A)': 0, '40-30(A-40)': 0, '40-40(NO AD)': 0, 'HOLD': self.pprop, 'BREAK': 0},
            '40-40(NO AD)': {'0-0': 0, '0-15': 0, '15-0': 0, '15-15': 0, '0-30': 0, '30-0': 0, '15-30': 0, '30-15': 0, '0-40': 0, '40-0': 0, '15-40': 0, '40-15': 0, '30-30(DEUCE)': 0, '30-40(40-A)': 0, '40-30(A-40)': 0, '40-40(NO AD)': 0, 'HOLD': self.pprop, 'BREAK': self.inv_prop},
            'HOLD': {'0-0': 0, '0-15': 0, '15-0': 0, '15-15': 0, '0-30': 0, '30-0': 0, '15-30': 0, '30-15': 0, '0-40': 0, '40-0': 0, '15-40': 0, '40-15': 0, '30-30(DEUCE)': 0, '30-40(40-A)': 0, '40-30(A-40)': 0, '40-40(NO AD)': 0, 'HOLD': 1.0, 'BREAK': 0},
            'BREAK': {'0-0': 0, '0-15': 0, '15-0': 0, '15-15': 0, '0-30': 0, '30-0': 0, '15-30': 0, '30-15': 0, '0-40': 0, '40-0': 0, '15-40': 0, '40-15': 0, '30-30(DEUCE)': 0, '30-40(40-A)': 0, '40-30(A-40)': 0, '40-40(NO AD)': 0, 'HOLD': 0, 'BREAK': 1.0},
        }

    def printptmatrix(self):
        print(f'\nGiven Proportion = {self.prop}')
        print('             ', end='')
        t = True
        for col in self.pt_matrix.keys():
            if col == 'HOLD':
                print('          ', col, end=' ')
            elif col == 'BREAK':
                print('         ', col, end=' ')
            else:
                print(col, end=' ')
        print()
        for row_index in self.pt_matrix.keys():
            print(row_index, end=' '*(12-len(row_index)))
            for col in self.pt_matrix[row_index].keys():
                if col == 'HOLD':
                    print(' '*(len(str(col))-(len(str(round(self.pt_matrix[row_index][col],2))))+11), str(round(self.pt_matrix[row_index][col],2)), end='')
                elif col == 'BREAK':
                    print(' '*(len(str(col))-(len(str(round(self.pt_matrix[row_index][col],2))))+10), str(round(self.pt_matrix[row_index][col],2)), end='')
                else:
                    print(' '*(len(str(col))-len(str(round(self.pt_matrix[row_index][col],2)))), str(round(self.pt_matrix[row_index][col],2)), end='')
            print()

    def next_state(self):
        try:
            self.curr_state = np.random.choice(list(self.pt_matrix.keys()), p=list(self.pt_matrix[self.curr_state].values()))
        except:
            print(list(self.pt_matrix[self.curr_state].values()))
            quit()
        return self.curr_state

def game(prop):
    model = MarkovModel(prop)
    while model.curr_state != 'HOLD' and model.curr_state != 'BREAK':
        model.next_state()
    return model.curr_state

def create_score(prop, best_of):
    score = ''
    first_serve = random.randint(0,1)
    sets_won = 0
    num_sets = 0
    for _ in range(best_of):
        p1_games = 0
        p2_games = 0
        done = True
        while done:
            if p1_games == 6 and p2_games < 5 or p2_games == 6 and p1_games < 5:
                break
            elif p1_games == 7 or p2_games == 7:
                break
            
            if (p1_games+p2_games) % 2 == 0:
                hb = game(prop)
            else:
                hb = game(1-prop)

            if first_serve == 0:
                if hb == 'HOLD' and (p1_games+p2_games) % 2 == 0:
                    p1_games += 1
                elif hb == 'HOLD' and (p1_games+p2_games) % 2 == 1:
                    p2_games += 1
                elif hb == 'BREAK' and (p1_games+p2_games) % 2 == 0:
                    p2_games += 1
                elif hb == 'BREAK' and (p1_games+p2_games) % 2 == 1:
                    p1_games += 1
            else:
                if hb == 'HOLD' and (p1_games+p2_games) % 2 == 0:
                    p2_games += 1
                elif hb == 'HOLD' and (p1_games+p2_games) % 2 == 1:
                    p1_games += 1
                elif hb == 'BREAK' and (p1_games+p2_games) % 2 == 0:
                    p1_games += 1
                elif hb == 'BREAK' and (p1_games+p2_games) % 2 == 1:
                    p2_games += 1

        num_sets += 1
        if p1_games > p2_games:
            sets_won += 1
        else:
            sets_won -= 1
        score = score + str(p1_games) + '-' + str(p2_games) + ' '
        if abs(sets_won) == round(best_of/3)+1:
            break
        elif abs(sets_won) == 2 and num_sets > 2:
            break
    score = score[:-1]
    return score

def simulate(prop, best_of):
    return create_score(prop, best_of)

def error(data, player_profiles, model=False, nn=1):
    total_games = 0
    loss = 0
    total_pred_games = 0
    total_matches = 0
    correct_match_pred = 0
    n = 0
    for i in range(len(data)):
        if i % round(len(data)/5) == 0:
            print(f'Testing..... {20*n}%')
            n += 1
        num_sets = round(len(data['score'][i]))
        p1_sets_won = 0
        p2_sets_won = 0
        for j in range(len(data['score'][i])):
            if j % 4 == 0:
                if int(data['score'][i][j]) > int(data['score'][i][j]):
                    p1_sets_won += 1
                else:
                    p2_sets_won += 1
        # if p1_sets_won > p2_sets_won:
        #     true_winner = 'p1'
        # else:
        #     true_winner = 'p2'

        if num_sets < 3:
            best_of = 3
        elif num_sets > 3:
            best_of = 5
        elif num_sets == 3 and abs(p1_sets_won-p2_sets_won) == 3:
            best_of = 5
        else:
            best_of = 3
        
        if not model:
            prop = nn*0.5
        else:
            prop = get_prop(model, data.iloc[i], player_profiles)
            
        score = simulate(prop, best_of)

        p1_sets_won = 0
        p2_sets_won = 0
        for j in range(len(score)):
            if j % 4 == 0:
                if int(score[j]) > int(score[j+2]):
                    p1_sets_won += 1
                else:
                    p2_sets_won += 1
            if j % 2 == 0 and j < len(data['score'][i]):
                try:
                    loss += abs(int(data['score'][i][j])-int(score[j]))
                except:
                    continue
                total_games += (int(data['score'][i][j]))
                total_pred_games += int(score[j])
            elif j % 2 == 0:
                loss += int(score[j])
                total_pred_games += int(score[j])
        # if p1_sets_won > p2_sets_won:
        #     pred_winner = 'p1'
        # else:
        #     pred_winner = 'p2'

        total_matches += 1
        for j in range(len(score)):
            if j % 4 == 0:
                try:
                    if score[j] == data['score'][i][j] and score[j+2] == data['score'][i][j]:
                        correct_match_pred += 1
                except:
                    continue
                
    print('\n           |  Total |   %   |')
    print('-----------+--------+-------+--------')
    print(f'Loss       | {loss} | {round(100*(loss/total_pred_games),2)} |')
    print(f'True Games | {total_games} |       |')
    print(f'Accuracy   |        | {round(100*(correct_match_pred/total_matches),2)} |')

data = pd.read_csv('atp_utr_tennis_matches.csv')
# logit_model = joblib.load('model.sav')
model = joblib.load('nn.sav')

utr_history = pd.read_csv('utr_history.csv')
history = get_player_history(utr_history)
player_profiles = get_player_profiles(data, history)

markovmodel = MarkovModel(0.5)
markovmodel.printptmatrix()

# start = time.time()
# print('\nProportion = 0.5')
# error(data, player_profiles, nn=0.8)
# end = time.time()
# print('-----------+--------+-------+--------')
# print(f'Runtime    |        |       | {round(end-start, 2)}s')

start = time.time()
print('\nProportion = UTR_Diff Calc')
error(data, player_profiles, model=model, nn=1)
end = time.time()
print('-----------+--------+-------+--------')
print(f'Runtime    |        |       | {round(end-start, 2)}s')