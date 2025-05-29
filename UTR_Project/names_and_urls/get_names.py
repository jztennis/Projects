import pandas as pd
import csv

atp_players = pd.read_csv('atp_players.csv')

distinct_players = pd.read_csv('distinct_players2.csv')

n = 0
data = [atp_players['name_first'].tolist(), atp_players['name_last'].tolist(), atp_players['dob'].tolist()]
newdata = []
for i in range(len(data[2])):
    if data[2][i] > 19870000.0:
        row = [data[0][i], data[1][i], int(data[2][i])]
        newdata.append(row)
# print(newdata)
with open('players.csv', 'w', newline='', encoding='utf-8') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(['f_name','l_name','dob'])
    writer.writerows(newdata)


###

players = pd.read_csv('players.csv')

tempdata = [players['f_name'].tolist(), players['l_name'].tolist()]
newdata = [['f_name', 'l_name']]
n = 0
with open("distinct_players.csv", 'w', newline='', encoding='utf-8') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(['f_name', 'l_name'])
    print('Starting check.....')
    for ref_name in distinct_players['Name']:
        n += 1
        for i in range(len(players['f_name'])):
            if type(players['f_name'][i]) == str and ref_name[:-3] == str(players['l_name'][i]) and ref_name[-2] == players['f_name'][i][0]:
                row = [players['f_name'][i], ref_name[:-3]]
                writer.writerow(row)
                break
        if n % 18 == 0:
            print(f'................... {(round(n/18))}%')