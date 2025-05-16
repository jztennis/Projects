import numpy as np
import torch
import torch.nn as nn
import math

class TennisPredictor(nn.Module):
    def __init__(self, input_size):
        super(TennisPredictor, self).__init__()
        self.fc1 = nn.Linear(input_size, 1028)
        self.fc2 = nn.Linear(1028, 512)
        self.fc3 = nn.Linear(512, 256)
        self.fc4 = nn.Linear(256, 128)
        self.fc5 = nn.Linear(128, 64)
        self.fc6 = nn.Linear(64, 32)
        self.fc7 = nn.Linear(32, 16)
        self.fc8 = nn.Linear(16, 1)
        self.relu = nn.ReLU()
        self.sigmoid = nn.Sigmoid()

    def forward(self, x):
        x = self.relu(self.fc1(x))
        x = self.relu(self.fc2(x))
        x = self.relu(self.fc3(x))
        x = self.relu(self.fc4(x))
        x = self.relu(self.fc5(x))
        x = self.relu(self.fc6(x))
        x = self.relu(self.fc7(x))
        x = self.sigmoid(self.fc8(x))
        return x

# Preprocessing function to convert match data into features for the model
def preprocess_match_data(matches, profiles): # log_predict?
    match_vector = [matches['p1_utr']-matches['p2_utr'], 
                        profiles[matches['p1']]['win_vs_lower']-profiles[matches['p2']]['win_vs_lower'],
                        profiles[matches['p1']]['win_vs_higher']-profiles[matches['p2']]['win_vs_higher'],
                        profiles[matches['p1']]['recent10']-profiles[matches['p2']]['recent10'],
                        profiles[matches['p1']]['wvl_utr']-profiles[matches['p2']]['wvl_utr'],
                        profiles[matches['p1']]['wvh_utr']-profiles[matches['p2']]['wvh_utr'],
                        (profiles[matches['p1']]['h2h'][matches['p2']][0] / profiles[matches['p1']]['h2h'][matches['p2']][1])-(profiles[matches['p2']]['h2h'][matches['p1']][0] / profiles[matches['p2']]['h2h'][matches['p1']][1]),
                        ]
    return match_vector

def get_player_profiles(data, history):
    player_profiles = {}

    for r in data.itertuples():
        player = r.p1
        opponent = r.p2
        utr_diff = r.p1_utr - r.p2_utr
        
        if player not in player_profiles and player in history:
            player_profiles[player] = {
                "win_vs_lower": [],
                "wvl_utr": [],
                "win_vs_higher": [],
                "wvh_utr": [],
                "recent10": [],
                "r10_utr": [],
                "momentum": [],
                "utr": history[player]['utr'],
                "h2h": {}
            }
        elif player not in player_profiles:
            player_profiles[player] = {
                "win_vs_lower": [],
                "wvl_utr": [],
                "win_vs_higher": [],
                "wvh_utr": [],
                "recent10": [],
                "r10_utr": [],
                "momentum": [],
                "utr": r.p1_utr if r.p1 == player else r.p2_utr,
                "h2h": {}
            }

        if opponent not in player_profiles and opponent in history:
            player_profiles[opponent] = {
                "win_vs_lower": [],
                "wvl_utr": [],
                "win_vs_higher": [],
                "wvh_utr": [],
                "recent10": [],
                "r10_utr": [],
                "momentum": [],
                "utr": history[opponent]['utr'],
                "h2h": {}
            }
        elif opponent not in player_profiles:
            player_profiles[opponent] = {
                "win_vs_lower": [],
                "wvl_utr": [],
                "win_vs_higher": [],
                "wvh_utr": [],
                "recent10": [],
                "r10_utr": [],
                "momentum": [],
                "utr": r.p1_utr if r.p1 == opponent else r.p2_utr,
                "h2h": {}
            }

        if opponent not in player_profiles[player]['h2h']:
            player_profiles[player]['h2h'][opponent] = [0,0]

        if player not in player_profiles[opponent]['h2h']:
            player_profiles[opponent]['h2h'][player] = [0,0]

        if r.winner == player:
            player_profiles[player]['h2h'][opponent][0] += 1
            player_profiles[player]['h2h'][opponent][1] += 1
            player_profiles[opponent]['h2h'][player][1] += 1
        else:
            player_profiles[player]['h2h'][opponent][1] += 1
            player_profiles[opponent]['h2h'][player][0] += 1
            player_profiles[opponent]['h2h'][player][1] += 1

        # Momentum
        # if r.winner == player:
        #     player_profiles[player]['momentum'].append(1)
        # else:
        #     player_profiles[player]['momentum'].append(0)
        
        # Record win rates vs higher/lower-rated opponents
        if utr_diff > 0:  # Player faced a lower-rated opponent
            if r.winner == player:
                player_profiles[player]["win_vs_lower"].append(1)
                player_profiles[opponent]["win_vs_higher"].append(0)
                player_profiles[player]["wvl_utr"].append(r.p2_utr)
                player_profiles[opponent]["wvh_utr"].append(0)
            else:
                player_profiles[player]["win_vs_lower"].append(0)
                player_profiles[opponent]["win_vs_higher"].append(1)
                player_profiles[opponent]["wvh_utr"].append(r.p1_utr)
                player_profiles[player]["wvl_utr"].append(0)

        else:  # Player faced a higher-rated opponent
            if r.winner == player:
                player_profiles[player]["win_vs_higher"].append(1)
                player_profiles[opponent]["win_vs_lower"].append(0)
                player_profiles[player]["wvh_utr"].append(r.p2_utr)
                player_profiles[opponent]["wvl_utr"].append(0)
            else:
                player_profiles[player]["win_vs_higher"].append(0)
                player_profiles[opponent]["win_vs_lower"].append(1)
                player_profiles[opponent]["wvl_utr"].append(r.p1_utr)
                player_profiles[player]["wvh_utr"].append(0)

        if r.winner == player:
            player_profiles[player]["recent10"].append(1)
            player_profiles[opponent]["recent10"].append(0)
        else:
            player_profiles[player]["recent10"].append(0)
            player_profiles[opponent]["recent10"].append(1)

        if len(player_profiles[player]["recent10"]) > 10:
            player_profiles[player]["recent10"] = player_profiles[player]["recent10"][1:]
        if len(player_profiles[opponent]["recent10"]) > 10:
            player_profiles[opponent]["recent10"] = player_profiles[opponent]["recent10"][1:]

    for player in player_profiles:
        profile = player_profiles[player]
        profile["win_vs_lower"] = np.mean(profile["win_vs_lower"]) if len(profile["win_vs_lower"]) > 0 else 0
        profile["win_vs_higher"] = np.mean(profile["win_vs_higher"]) if len(profile["win_vs_higher"]) > 0 else 0
        profile["recent10"] = np.mean(profile["recent10"]) if len(profile["recent10"]) > 0 else 0
        profile['wvl_utr'] = np.mean(profile['wvl_utr']) if len(profile['wvl_utr']) > 0 else 0
        profile['wvh_utr'] = np.mean(profile['wvh_utr']) if len(profile['wvh_utr']) > 0 else 0
        # if len(profile['momentum']) != 0:
        #     temp = []
        #     for i in range(len(profile['momentum'])):
        #         if profile['momentum'][-(i+1)] != 0:
        #             temp.append(0.8**(i+1))
        #         else:
        #             break
        #     profile['momentum'] = sum(temp)
        # else:
        #     profile['momentum'] = 0
    return player_profiles

def get_player_history(utr_history):
    history = {}

    for i in range(len(utr_history)):
        if utr_history['l_name'][i]+' '+utr_history['f_name'][i][0]+'.' not in history:
            history[utr_history['l_name'][i]+' '+utr_history['f_name'][i][0]+'.'] = {
                'utr': utr_history['utr'][i]
            }
    return history

def get_prop(model, matches, player_profiles):
    # Make one prediction
    X = preprocess_match_data(matches, player_profiles)
    # X_scaled = scaler.fit_transform(X)
    X_tensor = torch.tensor(X, dtype=torch.float32)

    y_test_one = model(X_tensor).squeeze().detach().numpy()
    y_test_one = 1-float(y_test_one)
    return y_test_one