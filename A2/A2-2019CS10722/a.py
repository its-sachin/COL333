import subprocess
import threading
import time
from os import getpid,kill

s = time.time()

def doIt():
    subprocess.run('python A2.py Part_B/9.csv')
    print('FINISHED')

t = threading.Thread(target=doIt)
t.start()

while True:
    if(time.time()-s > 5):
        print('BREAKING')
        kill(getpid(),9)

