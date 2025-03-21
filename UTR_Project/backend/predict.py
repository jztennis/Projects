import pandas as pd
import csv
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn import metrics
from sklearn.metrics import classification_report
import numpy as np
from sklearn.linear_model import LinearRegression
import random
from colorama import Fore, Style, init
import joblib
from model import LogitRegression

'''
MODELS TESTED:
 - Pseudo Logistic Regression Using tanh()  | Current Version
 - Logistic Regression via Scikit Learn     | Unable to assign proportion (only 0 or 1)
 - Random Forests via Scikit Learn          | Unable to assign proportion (only 0 or 1)
'''

def get_player_profiles(data, history, p1, p2):
    player_profiles = {}

    for i in range(len(data)):
        for player, opponent in [(data['p1'][i], data['p2'][i]), (data['p2'][i], data['p1'][i])]:
            if player == p1 or player == p2:
                utr_diff = data['p1_utr'][i] - data['p2_utr'][i] if data['p1'][i] == player else data['p2_utr'][i] - data['p1_utr'][i]
                
                if player not in player_profiles and player in history:
                    player_profiles[player] = {
                        "win_vs_lower": [],
                        "win_vs_higher": [],
                        "recent10": [],
                        "utr": history[player]['utr'],
                        "h2h": {}
                    }
                elif player not in player_profiles:
                    player_profiles[player] = {
                        "win_vs_lower": [],
                        "win_vs_higher": [],
                        "recent10": [],
                        "utr": data['p1_utr'][i] if data['p1'][i] == player else data['p2_utr'][i],
                        "h2h": {}
                    }

                if opponent not in player_profiles and opponent in history:
                    player_profiles[opponent] = {
                        "win_vs_lower": [],
                        "win_vs_higher": [],
                        "recent10": [],
                        "utr": history[opponent]['utr'],
                        "h2h": {}
                    }
                elif opponent not in player_profiles:
                    player_profiles[opponent] = {
                        "win_vs_lower": [],
                        "win_vs_higher": [],
                        "recent10": [],
                        "utr": data['p1_utr'][i] if data['p1'][i] == opponent else data['p2_utr'][i],
                        "h2h": {}
                    }

                if opponent not in player_profiles[player]['h2h']:
                    player_profiles[player]['h2h'][opponent] = [0,0]
                if player not in player_profiles[opponent]['h2h']:
                    player_profiles[opponent]['h2h'][player] = [0,0]

                if data['winner'][i] == player:
                    player_profiles[player]['h2h'][opponent][0] += 1
                    player_profiles[player]['h2h'][opponent][1] += 1
                    player_profiles[opponent]['h2h'][player][1] += 1
                else:
                    player_profiles[player]['h2h'][opponent][1] += 1
                    player_profiles[opponent]['h2h'][player][0] += 1
                    player_profiles[opponent]['h2h'][player][1] += 1
                
                # Record win rates vs higher/lower-rated opponents
                if utr_diff > 0:  # Player faced a lower-rated opponent
                    player_profiles[player]["win_vs_lower"].append(data["p_win"][i] == 1 if data["p1"][i] == player else data["p_win"][i] == 0)
                else:  # Player faced a higher-rated opponent
                    player_profiles[player]["win_vs_higher"].append(data["p_win"][i] == 1 if data["p1"][i] == player else data["p_win"][i] == 0)
                
                if len(player_profiles[player]["recent10"]) < 10:
                    player_profiles[player]["recent10"].append(data["p_win"][i] == 1 if data["p1"][i] == player else data["p_win"][i] == 0)
                else:
                    player_profiles[player]["recent10"] = player_profiles[player]["recent10"][1:]
                    player_profiles[player]["recent10"].append(data["p_win"][i] == 1 if data["p1"][i] == player else data["p_win"][i] == 0)

    for player in player_profiles:
        profile = player_profiles[player]
        profile["win_vs_lower"] = np.mean(profile["win_vs_lower"]) if len(profile["win_vs_lower"]) > 0 else 0.5
        profile["win_vs_higher"] = np.mean(profile["win_vs_higher"]) if len(profile["win_vs_higher"]) > 0 else 0.5
        profile["recent10"] = np.mean(profile["recent10"]) if len(profile["recent10"]) > 0 else 0
    
    return player_profiles

def get_player_history(utr_history):
    history = {}

    for i in range(len(utr_history)):
        if utr_history['l_name'][i]+' '+utr_history['f_name'][i][0]+'.' not in history:
            history[utr_history['l_name'][i]+' '+utr_history['f_name'][i][0]+'.'] = {
                'utr': utr_history['utr'][i]
            }
    return history

def get_score(players, player_profiles, best_of=3):
    utr_diff = [player_profiles[players[0]]["utr"]-player_profiles[players[1]]["utr"], player_profiles[players[1]]["utr"]-player_profiles[players[0]]["utr"]]
    for j in range(len(players)):

        utr_diff[j] += 0.1*player_profiles[players[j]]["recent10"]

        if utr_diff[j] > 0:
            utr_diff[j] *= (1.2 - player_profiles[players[j]]["win_vs_lower"])
        elif utr_diff[j] < 0:
            utr_diff[j] *= (1 + player_profiles[players[j]]["win_vs_higher"])
        
        if j == 0 and players[j+1] in player_profiles[players[j]]['h2h']:
            utr_diff[j] *= ((0.5+player_profiles[players[j]]['h2h'][ps[j+1]][0] / player_profiles[players[j]]['h2h'][players[j+1]][1])**0.4)
        elif j ==1 and players[j-1] in player_profiles[players[j]]['h2h']:
            utr_diff[j] *= ((0.5+player_profiles[players[j]]['h2h'][ps[j-1]][0] / player_profiles[players[j]]['h2h'][players[j-1]][1])**0.4)

    utr_diff[1] = -utr_diff[1]
    utr_diff = np.mean(utr_diff)
    utr_diff *= 0.8

    score = model.score(utr_diff, best_of)

    p1_games = 0
    p2_games = 0
    sets_won = 0
    for i in range(len(score)):
        if i % 4 == 0:
            p1_games += int(score[i])
            p2_games += int(score[i+2])
            if int(score[i]) > int(score[i+2]):
                sets_won += 1
            elif int(score[i]) < int(score[i+2]):
                sets_won -= 1
    if sets_won > 0:
        p1_win = True
    else:
        p1_win = False

    game_prop = p1_games / (p1_games+p2_games)

    return score, p1_win, game_prop

# get data to fit to model
data = pd.read_csv('atp_utr_tennis_matches.csv')
utr_history = pd.read_csv('utr_history.csv')

model = joblib.load('model.sav')

p1 = "Medvedev D."
p2 = "Alcaraz C."
ps = [p1, p2]
best = 5
history = get_player_history(utr_history)
player_profiles = get_player_profiles(data, history, ps[0], ps[1])

score, p1_win, game_prop = get_score(ps, player_profiles, best_of=best)
if p1_win:
    print(f'{p1} is predicted to win ({round(100*game_prop,2)}% of games) against {p2}: ', end='')
else:
    print(f'{p1} is predicted to lose ({round(100*(1-game_prop),2)}% of games) against {p2}:  ', end='')
for i in range(len(score)):
    if i % 4 == 0 and int(score[i]) > int(score[i+2]):
        print(Fore.GREEN + score[i], end='')
    elif i % 4 == 0 and int(score[i]) < int(score[i+2]):
        print(Fore.RED + score[i], end='')
    else:
        print(score[i], end='')
print()
init(autoreset=True)

'''
EXAMPLE OUTPUT:

+-----------------------------------------------------------------------------------------+
|                                                                                         |
|   Medvedev D. is predicted to lose (63.33% of games) against Alcaraz C.:  1-6 6-7 4-6   |
|                                                                                         |
+-----------------------------------------------------------------------------------------+

Output will always be player 1's score first. In this case I had 
player 1 as Medvedev and player 2 as Alcaraz. So in this example 
Medvedev lost to Alcaraz.

'''