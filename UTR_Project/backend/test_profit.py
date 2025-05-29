import random

profit = 0
bet_amount = 10
for i in range(100000):
    num = random.randint(-4,4) # 0 = win, 1 = lose
    '''for positive profit, winrate needs to be around 45% or higher with the below conditions'''
    if num > 0:
        num1 = random.randint(-1,1) # 0 = low, 1 = high
        if num1 <= 0:
            profit += 4
        else:
            profit += 24
    else:
        profit -= 10

print(f'Profit = ${profit}')