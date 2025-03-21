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


'''
MODELS TESTED:
 - Pseudo Logistic Regression Using tanh()  | Current Version
 - Logistic Regression via Scikit Learn     | Unable to assign proportion (only 0 or 1)
 - Random Forests via Scikit Learn          | Unable to assign proportion (only 0 or 1)
'''

class LogitRegression(LinearRegression):

    def fit(self, x, p):
        p = np.asarray(p)
        y = np.log(p / (1 - p))
        return super().fit(x, y)

    def predict(self, x):
        y = super().predict(x)
        return 1 / (np.exp(-y) + 1)
    
    def score(self, utr_diff, best_of):
        prop = self.predict([[utr_diff]])[0][0]
        score = ''
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
                val = random.uniform(0,1)
                if val < prop:
                    p1_games += 1
                else:
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

# get data to fit to model
data = pd.read_csv('atp_utr_tennis_matches.csv')
utr_history = pd.read_csv('utr_history.csv')

x = np.empty(1)
for i in range(len(data)):
    x = np.append(x, data['p1_utr'][i]-data['p2_utr'][i])

x = x.reshape(-1,1)

p = np.tanh(x) / 2 + 0.5
tmodel = LogitRegression()
tmodel.fit(0.9*x, p)

# Assuming 'model' is your trained model
joblib.dump(tmodel, 'model.sav')

'''
To load the model later:

model = joblib.load('model.sav')
'''