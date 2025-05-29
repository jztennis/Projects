import pandas as pd
import csv

data = pd.read_csv('C:/Users/Jared/Dropbox/Code/Python/UTR_Project/names_and_urls/atp_tennis_abbreviated.csv')
utr_history = pd.read_csv('utr_history.csv')

player_utrs = {}
for i in range(len(utr_history)):
    if utr_history['l_name'][i] not in player_utrs.keys():
        player_utrs[utr_history['l_name'][i]] = []
    player_utrs[utr_history['l_name'][i]].append([utr_history['f_name'][i], utr_history['date'][i], utr_history['utr'][i]])  


with open('atp_utr_tennis_matches.csv', 'w', newline='', encoding='utf-8') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(['tournament', 'date', 'series', 'court', 'surface', 'round', 'best_of', 'p1', 'p1_utr', 'p2', 'p2_utr', 'winner', 'p1_games', 'p2_games', 'score', 'p_win'])

    print('Player Data Processing ... START')
    n = 0
    for i in range(len(data)):
        br = False

        if i % 265 == 0:
            print(f'Processing.....{round(n)}%')
            n += 1
        row_data = [data['Tournament'][i], data['Date'][i], data['Series'][i], data['Court'][i], data['Surface'][i], data['Round'][i], data['Best of'][i]]

        match_date = data['Date'][i][-4:]
        if data['Date'][i][1] == '/':
            match_date = match_date + '0' + data['Date'][i][0]
            if data['Date'][i][3] == '/':
                match_date = match_date + '0' + data['Date'][i][2]
            else:
                match_date = match_date + data['Date'][i][2:4]
        else:
            match_date = match_date + data['Date'][i][0:2]
            if data['Date'][i][4] == '/':
                match_date = match_date + '0' + data['Date'][i][3]
            else:
                match_date = match_date + data['Date'][i][3:5]

        temp = match_date[0:4] + '-' + match_date[4:6] + '-' + match_date[-2:]
        row_data = [data['Tournament'][i], temp, data['Series'][i], data['Court'][i], data['Surface'][i], data['Round'][i], data['Best of'][i]]
                
        players = ['Player_1', 'Player_2']
        for player in players:
            row_data.append(data[player][i])
            if data[player][i][:-3] in player_utrs.keys():

                matched = False
                for j in range(len(player_utrs[ data[player][i][:-3] ])):
                    if player_utrs[ data[player][i][:-3] ][j][0][0] == data[player][i][-2]:
                        player_date = player_utrs[ data[player][i][:-3] ][j][1][:4] + player_utrs[ data[player][i][:-3] ][j][1][-5:-3] + player_utrs[ data[player][i][:-3] ][j][1][-2:]
                        if int(player_date) <= int(match_date):
                            num = player_utrs[ data[player][i][:-3] ][j][2]
                            if num < 13 and data['Winner'][i] == data[player][i]:
                                num = 14
                            elif num < 13:
                                num = 13
                            row_data.append(num)
                            matched = True
                            break
                if not matched:
                    num = player_utrs[ data[player][i][:-3] ][ len(player_utrs[ data[player][i][:-3] ])-1 ][2]
                    if num < 13 and data['Winner'][i] == data[player][i]:
                        num = 14
                    elif num < 13:
                        num = 13
                    row_data.append(num)
            else:
                br = True
        if br:
            continue

        row_data.append(data['Winner'][i])

        p1_games = 0
        p2_games = 0
        m = 0
        temp = ''
        for j in range(len(data['Score'][i])):
            if data['Score'][i][j] == '-' or data['Score'][i][j] == ' ':
                if m%2 == 0:
                    p1_games += int(temp)
                    m += 1
                else:
                    p2_games += int(temp)
                    m += 1
                temp = ''
            else:
                temp = temp + data['Score'][i][j]
        p2_games += int(temp)
        row_data.append(p1_games)
        row_data.append(p2_games)

        row_data.append(data['Score'][i])

        if data['Player_1'][i] == data['Winner'][i]:
            row_data.append(0)
        else:
            row_data.append(1)
        
        writer.writerow(row_data)
        
print('Player Data Processing ... END')

'''
Last Row in .csv should be:
Fritz | 15.90 | Sinner | 16.21
'''