import random
import subprocess
import json

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

def sanity(d,N,D,m,a,e):
    
    if(d=={}):
        print('NOT POSSIBLE',end=' ')
        return
    count = {'M':[0]*D,'A':[0]*D,'E':[0]*D,'R':[0]*D}
    bound = {'M':m,'A':a,'E':e,'R':N-m-a-e}
    for nurse in d:
        # print(nurse,d[nurse])
        for day in d[nurse]:
            if(day < D and ( d[nurse][day] == d[nurse][day+1] == 'M' or (d[nurse][day] == 'E' and d[nurse][day+1] == 'M'))):
                print('NURSE',nurse,' EM/MM AT',day)
                return
            val=d[nurse][day]
            count[val][day-1] += 1
    for i in count:
        for j in count[i]:
            if(i != 'R' and j != bound[i]):
                print('DAY',i,'NOT MATCHING AT',j)
                return

    for nurse in d:
        got = False
        day = 1
        while(day <= D):
            if(d[nurse][day]  == 'R'):
                got = True
            if(day%7==0):
                if(not got):
                    print('NURSE',nurse,'NO REST',day)
                    return 
                got = False
            day +=1

    print('SANITY MATCHED',end=' ')

def getWeight(e,s,d):
    if(len(e)==0):
        return 0
    w=0
    for nurse in range(1,s+1):
        for day in range(1,d+1):
            if(e[nurse][day] == 'M' or e[nurse][day] == 'E'):
                w+=1
    return w


def extensive(t=1):


    ques = open('ques2.txt','w+')
    if(t==1):
        ques.write('N,D,m,a,e\n')
    else:
        ques.write('N,D,m,a,e,S,T\n')

    for i in range(100):
        N =random.randint(1,50)
        D = random.randint(1,50)
        S = random.randint(1,1+N//2)
        T =  min(4*(N+D),100)
        while True:
            m = random.randint(0,50)
            a = random.randint(0,50)
            e = random.randint(0,50)

            if(m+a+e <= N):
                break
        file = open('test.txt','w+')
        if(t==1):
            file.write('N,D,m,a,e\n')
            print(str(N) + ',' + str(D) + ',' + str(m) + ',' + str(a) + ',' + str(e))
            file.write(str(N) + ',' + str(D) + ',' + str(m) + ',' + str(a) + ',' + str(e)+'\n')
            ques.write(str(N) + ',' + str(D) + ',' + str(m) + ',' + str(a) + ',' + str(e)+'\n')
        else:
            file.write('N,D,m,a,e,S,T\n')
            print(str(N) + ',' + str(D) + ',' + str(m) + ',' + str(a) + ',' + str(e)+',' + str(S)+',' + str(T))
            file.write(str(N) + ',' + str(D) + ',' + str(m) + ',' + str(a) + ',' + str(e)+',' + str(S)+',' + str(T)+'\n')
            ques.write(str(N) + ',' + str(D) + ',' + str(m) + ',' + str(a) + ',' + str(e)+',' + str(S)+',' + str(T)+'\n')
        file.close()
        subprocess.run('python A2.py test.txt')

        data = []

        with open('solution.json') as f:
            for line in f:
                data.append(json.loads(line))
        type(data)==type([])
        f.close()

        for line,sol in enumerate(data):
            assert type(sol)==type({})
        d = {}
        i,j=0,0
        for item in sol:
            if(j%D==0):
                j=0
                i+=1
                d[i]={}
            j+=1
            d[i][j] = sol[item]
        sanity(d,N,D,m,a,e)
        if(t==2):
            print(100*getWeight(d,S,D)/(m+e))
            print()


def extensive1(t=1):
    
    ques = open('ques1_t1.txt','r+')
    ques.readline()
    for line in ques.readlines():
        file = open('test.txt','w+')
        if(t==1):
            N,D,m,a,e = map(int,line.strip().split(',')) 
            file.write('N,D,m,a,e\n')
            print('\n'+str(N) + ',' + str(D) + ',' + str(m) + ',' + str(a) + ',' + str(e))
            file.write(str(N) + ',' + str(D) + ',' + str(m) + ',' + str(a) + ',' + str(e)+'\n')
            ques.write(str(N) + ',' + str(D) + ',' + str(m) + ',' + str(a) + ',' + str(e)+'\n')
        else:
            N,D,m,a,e,S,T = map(int,line.strip().split(',')) 
            file.write('N,D,m,a,e,S,T\n')
            print('\n'+str(N) + ',' + str(D) + ',' + str(m) + ',' + str(a) + ',' + str(e)+',' + str(S)+',' + str(T))
            file.write(str(N) + ',' + str(D) + ',' + str(m) + ',' + str(a) + ',' + str(e)+',' + str(S)+',' + str(T)+'\n')
            ques.write(str(N) + ',' + str(D) + ',' + str(m) + ',' + str(a) + ',' + str(e)+',' + str(S)+',' + str(T)+'\n')
        file.close()
        subprocess.run('python A2.py test.txt')

        data = []

        with open('solution.json') as f:
            for line in f:
                data.append(json.loads(line))
        type(data)==type([])
        f.close()

        for line,sol in enumerate(data):
            assert type(sol)==type({})
        if(sol!={}):
            d = {}
            for i in range(N):
                d[i+1]={}
                for j in range(D):
                    d[i+1][j+1] = sol['N'+str(i) + '_' + str(j)]
            sanity(d,N,D,m,a,e)
            if(t==2):
                print(getWeight(d,S,D))
                print()
        else:
            print('NOT POSSIBLE',end=' ')


# test()
# extensive(1)
extensive1(1)



