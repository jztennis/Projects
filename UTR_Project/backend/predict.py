import numpy as np
import random
import pandas as pd
import torch
import joblib
from network import TennisPredictor, get_player_profiles, get_player_history
from colorama import Fore, Style, init

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
            if p1_games == 6 and p2_games < 5 or p2_games == 6 and p1_games < 5: # Good
                break
            elif p1_games == 7 or p2_games == 7:
                break
            
            if (p1_games+p2_games) % 2 == 0: # Good
                hb = game(prop)
            else:
                hb = game(1-prop)

            if first_serve == 0: # Good
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

        num_sets += 1 # Good
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
    # print(score)
    return score

def preprocess_player_data(p1, p2, profiles):
    match_vector = [profiles[p1]['utr']-profiles[p2]['utr'], 
                    profiles[p1]['win_vs_lower'],
                    profiles[p2]['win_vs_lower'],
                    profiles[p1]['win_vs_higher'],
                    profiles[p2]['win_vs_higher'],
                    profiles[p1]['recent10'],
                    profiles[p2]['recent10'],
                    profiles[p1]['wvl_utr'],
                    profiles[p2]['wvl_utr'],
                    profiles[p1]['wvh_utr'],
                    profiles[p2]['wvh_utr'],
                    profiles[p1]['h2h'][p2][0] / profiles[p1]['h2h'][p2][1],
                    profiles[p2]['h2h'][p1][0] / profiles[p2]['h2h'][p1][1]
                    ]
    return match_vector

def get_prop(model, p1, p2, player_profiles):
    # Make one prediction
    X = preprocess_player_data(p1, p2, player_profiles)
    X_tensor = torch.tensor(X, dtype=torch.float32)

    prop = model(X_tensor).squeeze().detach().numpy()
    prop = 1-float(prop)
    return prop

def find_winner(score):
    p1_sets_won = 0
    p2_sets_won = 0
    for j in range(len(score)):
        if j % 4 == 0:
            if int(score[j]) > int(score[j+2]):
                p1_sets_won += 1
            else:
                p2_sets_won += 1
    if p1_sets_won > p2_sets_won:
        pred_winner = 'p1'
    else:
        pred_winner = 'p2'
    return pred_winner

def predict(model, p1, p2, player_profiles, best_of=3):
    prop = get_prop(model, p1, p2, player_profiles)
    score = create_score(prop, best_of)

    pred_winner = find_winner(score)
    if prop >= 0.5:
        true_winner = 'p1'
    else:
        true_winner = 'p2'

    while true_winner != pred_winner:
        score = create_score(prop, best_of)
        pred_winner = find_winner(score)

    return true_winner, score, round(100*prop, 2)

data = pd.read_csv('atp_utr_tennis_matches.csv')
utr_history = pd.read_csv('utr_history.csv')
model = joblib.load('model.sav')

history = get_player_history(utr_history)
player_profiles = get_player_profiles(data, history)

p1 = 'De Minaur A.'
p2 = 'Paul T.'

true_winner, score, prop = predict(model, p1, p2, player_profiles, best_of=3)

if true_winner == 'p1':
    print(f'{p1} is predicted to win against {p2} ({prop}% Confidence): ', end='')
else:
    print(f'{p1} is predicted to lose against {p2} ({prop}% Confidence): ', end='')
for i in range(len(score)):
    if i % 4 == 0 and int(score[i]) > int(score[i+2]):
        print(Fore.GREEN + score[i], end='')
    elif i % 4 == 0 and int(score[i]) < int(score[i+2]):
        print(Fore.RED + score[i], end='')
    else:
        print(score[i], end='')
print()
init(autoreset=True)