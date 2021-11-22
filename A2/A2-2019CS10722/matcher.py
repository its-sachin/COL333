import json
import subprocess

def doIt():

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
                if(j != bound[i]):
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

    data = []
    line = '10,14,2,3,2,7,600'
    N,D,m,a,e,S,T = map(int,line.strip().split(',')) 

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
        print(getWeight(d,S,D))
        print()
    else:
        print('NOT POSSIBLE',end=' ')

for i in range(10):
    subprocess.run('python A2.py Part_B/47.csv')
    doIt()