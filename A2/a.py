import random
import subprocess

file = open('ques1_t1.txt','w+')
file.write('N,D,m,a,e\n')
for i in range(20):
    N =random.randint(1,30)
    D = random.randint(1,30)
    while True:
        m = random.randint(0,30)
        a = random.randint(0,30)
        e = random.randint(0,30)

        if(m+a+e <= N):
            break
    # print(str(N) + ',' + str(D) + ',' + str(m) + ',' + str(a) + ',' + str(e))
    file.write(str(N) + ',' + str(D) + ',' + str(m) + ',' + str(a) + ',' + str(e)+'\n')
file.close()
subprocess.run('python A2.py ques1_t1.txt')

