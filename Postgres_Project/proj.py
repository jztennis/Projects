
#======================================================================
# 
#  NAME:    Jared Zaugg
#  ASSIGN:  Final Project
#  COURSE:  CPSC 321, Fall 2024
#  DESC:    Final project functions and running the program.
# 
#======================================================================

# TODO:
# format queries so they look nice
# add comments

import psycopg as pg
import config as config
from tabulate import tabulate

#######   FUNCTIONS   #######

# Gets Input #
def get_general_input():
    print('-----------------------------------------------------------------------------------------------------------------------------------------------------')
    print('#####################################################################################################################################################')
    print('-----------------------------------------------------------------------------------------------------------------------------------------------------')
    print('1) Find All')
    print('2) Search')
    print('3) Add Row')
    print('4) Delete Rows')
    print('5) Update Rows')
    print('6) Get Metrics')
    print("7) Get Players' Wins By Surface")
    print('8) Get Head-to-Head For 2 Players')
    print('9) Rafa Retired...')
    print('0) Exit')
    t = int(input('Enter your choice(0-9): '))
    print('-----------------------------------------------------------------------------------------------------------------------------------------------------')
    print('#####################################################################################################################################################')
    print('-----------------------------------------------------------------------------------------------------------------------------------------------------')
    return t
###

# Option 1: Find All
def option1():
    a = input('Table Name...............')
    with pg.connect(host=config.HOST, user=config.USER, password=config.PASSWORD, dbname=config.DATABASE) as cn:
        # make a cursor
        with cn.cursor() as rs: 
            # execute a query
            q = 'SELECT * FROM %s' % (a)
            rs.execute(q)

            # display results
            colnames = [desc[0] for desc in rs.description]

            # get array of rows
            rows = [list(row) for row in rs]

            # print table
            print(tabulate(rows, headers=colnames, tablefmt="grid"))
###

# Option 2: Basic Search
def option2():
    with pg.connect(host=config.HOST, user=config.USER, password=config.PASSWORD, dbname=config.DATABASE) as cn:
        b = input('Table...............')
        print("'For the below options, enter '~' to leave that option blank.")
        c = input('Column to match...............')
        d = input('(>, <, >=, <=, =, !=)...............')
        e = input("Value to match...............")
        f = input('Order by...............')
        g = ''
        if f != '~':
            g = input('Highest-Lowest(H) | Lowest-Highest(L)...............')

        if c == '' or d == '' or e == '':
            return
        elif c != '~':
            if d not in ('>','<','>=', '<=', '=', '!='):
                print('+-------------------+')
                print('|   INVALID INPUT   |')
                print('+-------------------+')  
                return
            if f != '~' and f != '':
                if g == 'H':
                    try:
                        int(e)
                        q = "SELECT * FROM %s WHERE %s %s %s ORDER BY %s DESC" % (b,c,d,e,f)
                    except:
                        q = "SELECT * FROM %s WHERE %s %s '%s' ORDER BY %s DESC" % (b,c,d,e,f)
                elif g == 'L':
                    try:
                        int(e)
                        q = "SELECT * FROM %s WHERE %s %s %s ORDER BY %s ASC" % (b,c,d,e,f)
                    except:
                        q = "SELECT * FROM %s WHERE %s %s '%s' ORDER BY %s ASC" % (b,c,d,e,f)
                else:
                    print('+-------------------+')
                    print('|   INVALID INPUT   |')
                    print('+-------------------+')
                    return
            elif f == '~':
                try:
                    int(e)
                    q = "SELECT * FROM %s WHERE %s %s %s" % (b,c,d,e)
                except:
                    q = "SELECT * FROM %s WHERE %s %s '%s'" % (b,c,d,e)
            else:
                print('+-------------------+')
                print('|   INVALID INPUT   |')
                print('+-------------------+')
                return
        else:
            print('+-------------------+')
            print('|   INVALID INPUT   |')
            print('+-------------------+')
            return
        
        # make a cursor
        with cn.cursor() as rs: 
            # execute a query
            rs.execute(q)

            # display results
            colnames = [desc[0] for desc in rs.description]

            # get array of rows
            rows = [list(row) for row in rs]

            # print table
            print(tabulate(rows, headers=colnames, tablefmt="grid"))
###

# Option 3: Add
def option3():
    a = input('Table Name...............')
    with pg.connect(host=config.HOST, user=config.USER, password=config.PASSWORD, dbname=config.DATABASE) as cn:
        # get the column names of the table
        with cn.cursor() as rs:
            q = "SELECT * FROM %s" % (a)
            rs.execute(q)

            colnames = [desc[0] for desc in rs.description]

        # get user input
        q = "INSERT INTO %s VALUES (" % (a)
        for col in colnames:
            user_input = input(f'{col}...............')
            try:
                int(user_input)
                q = q + f"{user_input}, "
            except:
                q = q + f"'{user_input}', "
        q = q[:-2] + ")"

        # run add
        with cn.cursor() as rs:
            # execute the insert
            rs.execute(q)
            # make it stick!
            cn.commit()
###

# Option 4: Delete
def option4():
    a = input('Table Name...............')
    with pg.connect(host=config.HOST, user=config.USER, password=config.PASSWORD, dbname=config.DATABASE) as cn:
        # get country codes for deletion
        q = "SELECT * FROM %s" % (a)

        # check that there is a border
        with cn.cursor() as rs:
            rs.execute(q)
            
            colnames = [desc[0] for desc in rs.description]
        
        # get user_input and create query simultaneously
        print("For the following columns, if it can ignored during deletion enter '~', otherwise enter the value.")
        q = "DELETE FROM %s WHERE " % (a)
        for i in range(len(colnames)):
            user_input = input(f"{colnames[i]}...............")
            if user_input != '~':
                try:
                    int(user_input)
                    q = q + "%s = %s AND " % (colnames[i], user_input)
                except:
                    q = q + "%s = '%s' AND " % (colnames[i], user_input)
        q = q[:-5]

        # delete
        with cn.cursor() as rs:
            # make the change
            rs.execute(q)
            # make it stick
            cn.commit()
###

# Option 5: Update
def option5():
    a = input('Table Name...............')
    with pg.connect(host=config.HOST, user=config.USER, password=config.PASSWORD, dbname=config.DATABASE) as cn:
        # make a cursor
        with cn.cursor() as rs: 
            # execute a query
            q = 'SELECT * FROM %s' % (a)
            rs.execute(q)

            # display results
            colnames = [desc[0] for desc in rs.description]

        # develop values to replace
        print("For the following columns, enter the value to update it to, otherwise enter '~' to not update that column.")
        q = "UPDATE %s SET " % (a)
        for i in range(len(colnames)):
            user_input = input(f"{colnames[i]}.....")
            if user_input != '~':
                try:
                    int(user_input)
                    q = q + "%s = %s, " % (colnames[i], user_input)
                except:
                    q = q + "%s = '%s', " % (colnames[i], user_input)
        q = q[:-2] + " WHERE "

        print("For the following columns, enter the current value of the row that needs to be changed, otherwise enter '~' to ignore that column.")
        # develop values to be replaced
        for i in range(len(colnames)):
            user_input = input(f"{colnames[i]}...............")
            if user_input != '~':
                try:
                    int(user_input)
                    q = q + "%s = %s AND " % (colnames[i], user_input)
                except:
                    q = q + "%s = '%s' AND " % (colnames[i], user_input)
        q = q[:-5]
        
        # update
        with cn.cursor() as rs:
            # execute the insert
            rs.execute(q)
            # make it stick!
            cn.commit()
###

# Option 6: Metrics
def option6():
    a = input('Table Name...............')
    with pg.connect(host=config.HOST, user=config.USER, password=config.PASSWORD, dbname=config.DATABASE) as cn:
        # make a cursor
        with cn.cursor() as rs: 
            # execute a query
            q = 'SELECT * FROM %s' % (a)
            rs.execute(q)

            # get column names
            colnames = [desc[0] for desc in rs.description]

        b = input("To count, enter 'C'; for the min/max/avg, enter 'A'...............")
        if b == 'C': # Counting
            print("For the following columns, enter 'Y' to consider the column, enter '~' and ignore one and 'ALL' for the rest.")
            q = "SELECT "
            temp = []
            user_input = ''
            for i in range(len(colnames)):
                if user_input != 'ALL':
                    user_input = input(f"{colnames[i]}...............")
                    if user_input != 'ALL':
                        temp.append(user_input)
                    else:
                        temp.append('~')
                else:
                    temp.append('~')
            
            for i in range(len(temp)):
                if temp[i] == 'Y':
                    q = q + f"{colnames[i]}, "
            q = q + "COUNT(*) AS num_%s FROM %s WHERE " % (a,a)

            print("For the following, enter the value of column to include the row in calculations. Enter '~' to ignore one and 'ALL for the rest.")
            t = True
            for i in range(len(colnames)):
                if user_input != 'ALL':
                    user_input = input(f"{colnames[i]}...............")
                    if user_input != '~' and user_input != 'ALL':
                        t = False
                        try:
                            int(user_input)
                            q = q + "%s = %s AND " % (colnames[i], user_input)
                        except:
                            q = q + "%s = '%s' AND " % (colnames[i], user_input)

            if t:
                q = q[:-7]
            else:
                q = q[:-5]

            if 'Y' in temp:
                q = q + " GROUP BY "
                for i in range(len(temp)):
                    if temp[i] == 'Y':
                        q = q + f"{colnames[i]}, "
                q = q[:-2]

        elif b == 'A': # min/max/avg
            print("For the following columns, enter 'Y' to consider the column, enter '~' and to ignore one and 'ALL' to ignore the rest.")
            q = "SELECT "

            # gets columns to be grouped by
            temp = []
            user_input = ''
            for i in range(len(colnames)):
                if user_input != 'ALL':
                    user_input = input(f"{colnames[i]}...............")
                    if user_input != 'ALL':
                        temp.append(user_input)
                    else:
                        temp.append('~')
                else:
                    temp.append('~')

            # puts group by columns in SELECT
            for i in range(len(temp)):
                if temp[i] == 'Y':
                    q = q + f"{colnames[i]}, "
            ui = input("Enter column to take the min/max/avg of...............")
            q = q + "MIN(%s) AS min_%s, MAX(%s) AS max_%s, AVG(%s) AS avg_%s FROM %s WHERE " % (ui, ui, ui, ui, ui, ui, a)

            print("For the following, enter the value of column to include the row in calculations. Enter '~' to ignore one, 'ALL' to ignore the rest.")
            
            # 
            t = True
            user_input = ''
            for i in range(len(colnames)):
                if user_input != 'ALL':
                    user_input = input(f"{colnames[i]}...............")
                    if user_input != '~' and user_input != 'ALL':
                        t = False
                        try:
                            int(user_input)
                            q = q + "%s = %s AND " % (colnames[i], user_input)
                        except:
                            q = q + "%s = '%s' AND " % (colnames[i], user_input)
                else:
                    break

            if t:
                q = q[:-7]
            else:
                q = q[:-5]

            if 'Y' in temp:
                q = q + " GROUP BY "
                for i in range(len(temp)):
                    if temp[i] == 'Y':
                        q = q + f"{colnames[i]}, "
                q = q[:-2]

        else:
            print('+-------------------+')
            print('|   INVALID INPUT   |')
            print('+-------------------+')  

        with cn.cursor() as rs: 
            # execute a query
            rs.execute(q)

            # get array of rows
            rows = [list(row) for row in rs]
            final_colnames = [desc[0] for desc in rs.description]

        # print table
        print(tabulate(rows, headers=final_colnames, tablefmt="grid"))
###

# Option 7: Player's wins by surface
def option7():
    with pg.connect(host=config.HOST, user=config.USER, password=config.PASSWORD, dbname=config.DATABASE) as cn:
        # Count wins by surface query
        q = '''SELECT f_name AS first_name, l_name AS last_name, surface, COUNT(*) AS wins 
               FROM Player JOIN Match ON(player_id=winner_id) JOIN Tournament USING(tourney_id) 
               GROUP BY surface, f_name, l_name 
               ORDER BY l_name, f_name'''
        
        # make cursor
        with cn.cursor() as rs: 
            # execute a query
            rs.execute(q)

            # display results
            colnames = [desc[0] for desc in rs.description]

            # get array of rows
            rows = [list(row) for row in rs]

            # print table
            print(tabulate(rows, headers=colnames, tablefmt="grid"))
###

# Option 8: Player Head-to-Head
def option8():
    with pg.connect(host=config.HOST, user=config.USER, password=config.PASSWORD, dbname=config.DATABASE) as cn:
        p1 = input("player1_id...............")
        p2 = input("player2_id...............")

        # INSANE QUERY
        # DESC: With is necessary to get the wins and losses, combine with the players stats in all match 
        # and reassign winner_id to 0 or 1 for if that player won or lost the match. Then the select below
        # takes the average of all metrics and puts out 2 rows which is the player's head-to-head win-rate
        # as well as some metrics to go along with it.
        q = f'''WITH temp(match_id, player_id, f_name, l_name, win_rate, aces, double_faults, winners, unforced_errors, total_points_won) AS (
                SELECT ms.match_id, player_id, f_name, l_name, CASE 
                                                                WHEN player_id=winner_id THEN 1 
                                                                ELSE 0 
                                                            END AS win_rate, aces, double_faults, winners, unforced_errors, total_points_won 
                FROM Match_Stats ms JOIN Player USING(player_id) JOIN Match USING(match_id) 
                WHERE ms.match_id IN (SELECT match_id 
                                      FROM Match 
                                      WHERE player1_id={p1} AND player2_id={p2} OR player1_id={p2} AND player2_id={p1}) AND 
                      (ms.player_id={p1} OR ms.player_id={p2})
               ) 
               SELECT f_name, l_name, AVG(win_rate) AS win_rate, AVG(aces) AS avg_aces, AVG(double_faults) AS avg_double_faults, AVG(winners) AS avg_winners, AVG(unforced_errors) AS avg_unforced_errors, AVG(total_points_won) AS avg_total_points_won
               FROM temp 
               GROUP BY f_name, l_name
               ORDER BY win_rate DESC'''

        # make a cursor
        with cn.cursor() as rs: 
            # execute a query
            rs.execute(q)

            # display results
            colnames = [desc[0] for desc in rs.description]

            # get array of rows
            rows = [list(row) for row in rs]

            # print table
            print(tabulate(rows, headers=colnames, tablefmt="grid"))
###

# Option 9: Rafa Retired (Cry)
def option9():
    print('                                                            ')
    print('                         ##############                     ')
    print('                    ########        ########                ')
    print('                 #####                    #####             ')
    print('               ###                           ###            ')
    print('              ##                               ##           ')
    print('             ###        ###         ###        ###          ')
    print('             ##         ###         ###         ##          ')
    print('             ##                                 ##          ')
    print('             ##                                 ##          ')
    print('             ##            #########            ##          ')
    print('             ###          ###     ###          ###          ')
    print('              ##         ##         ##         ##           ')
    print('               ###                           ###            ')
    print('                 #####                    #####             ')
    print('                    ########        ########                ')
    print('                         ##############                     ')
    print('                                                            ')
###

# Runs Program
def run():
    general_user_input = -1 # Initialize

    while int(general_user_input) != 0:
        general_user_input = get_general_input() # get user input

        if general_user_input < 0 or general_user_input > 9: # if wrong choice
            print('+-------------------+')
            print('|   INVALID INPUT   |')
            print('+-------------------+')
        elif general_user_input == 1: # Find All
            option1()
        elif general_user_input == 2: # Search
            option2()
        elif general_user_input == 3: # Add Row
            option3()
        elif general_user_input == 4: # Delete Rows
            option4()
        elif general_user_input == 5: # Update Rows
            option5()
        elif general_user_input == 6: # Get Metrics
            option6()
        elif general_user_input == 7: # Get Players' Wins By Surface
            option7()
        elif general_user_input == 8: # Get Head-to-Head For 2 Players
            option8()
        elif general_user_input == 9: # Rafa Retired (Cry)
            option9()

    print('Exit Successful.')
###

## RUN PROGRAM ##
run()           #
#################