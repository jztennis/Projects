import subprocess
import time

start = time.time()

print('#================================================#\nRunning history.py...') # ~ 2 hours
subprocess.run(['python', 'history.py'])
print('#================================================#\n')

print('#================================================#\nRunning matches.py...') # ~ 1.5 hours
subprocess.run(['python', 'matches.py'])
print('#================================================#\n')

print('#================================================#\nRunning model.py...') # ~ 10 min
subprocess.run(['python', 'model.py'])
print('#================================================#\n')

print('#================================================#\nRunning upcoming.py...') # ~ 5 min
subprocess.run(['python', 'upcoming.py'])
print('#================================================#\n')

print('#================================================#\nRunning predict.py...') # ~ 2 min
subprocess.run(['python', 'predict.py'])
print('#================================================#\n')

end = time.time()
print('All scripts executed successfully.')

seconds = round(end-start)
print(f'Runtime: {seconds}s | {round(seconds/60, 2)}m | {round(seconds/3600, 2)}h')