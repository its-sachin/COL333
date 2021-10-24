import random
import subprocess

def test():
    N =random.randint(30,50)
    D = random.randint(30,50)
    while True:
        m = random.randint(10,50)
        a = random.randint(10,50)
        e = random.randint(10,50)

        if(m+a+e <= N):
            break
    print(str(N) + ',' + str(D) + ',' + str(m) + ',' + str(a) + ',' + str(e))
    file = open('test.csv','w+')
    file.write('N,D,m,a,e\n' + str(N) + ',' + str(D) + ',' + str(m) + ',' + str(a) + ',' + str(e))
    file.close()
    subprocess.run('python A2.py test.csv')

def extensive():
    file = open('ques1_t1.txt','w+')
    file.write('N,D,m,a,e\n')
    for i in range(1000):
        N =random.randint(1,50)
        D = random.randint(1,50)
        while True:
            m = random.randint(0,50)
            a = random.randint(0,50)
            e = random.randint(0,50)

            if(m+a+e <= N):
                break
        # print(str(N) + ',' + str(D) + ',' + str(m) + ',' + str(a) + ',' + str(e))
        file.write(str(N) + ',' + str(D) + ',' + str(m) + ',' + str(a) + ',' + str(e)+'\n')
    file.close()
    subprocess.run('python A2.py ques1_t1.txt')

# test()
extensive()



