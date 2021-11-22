import json
import re
import sys

data = []
try:
    with open('solution.json') as f:
        for line in f:
            data.append(json.loads(line))
except Exception as e:
    print(f"FAILED | Not able to read file as a list of jsons (key value are string), make sure every assignment is in different line | Error : {e}")
    sys.exit()

assert type(data)==type([]),"FAILED | Not able to read file as a list of solutions, make sure every assignment is in different line"

for line,sol in enumerate(data):
    assert type(sol)==type({}), f"FAILED | Every solution line should be json | Error in line | {line+1}"
    for key,value in sol.items():
        assert type(key)==type(""),f"FAILED | Key should be of string form | Error in line {line+1} | key : {key}"
        assert type(key) == type(""), f"FAILED | Value should be of string form | Error in line {line+1} | value : {value}"
        k = re.compile(r"[0-9]+").sub("##",key)
        assert k=="N##_##", f"FAILED | Key should be of N#_# where # is number (0,1...) form | Error in line {line} | key : {key}"
        assert value in ["R","M","A","E"], f"FAILED | Value should be one of the following - A,E,M,R | Error in line {line} | value : {value}"

print("FORMAT PASSED")

with open('solution.json') as f:
    for line in f:
        data.append(json.loads(line))
type(data)==type([])

def sanity(d,N,D,m,a,e):
    
    count = {'M':[0]*D,'A':[0]*D,'E':[0]*D,'R':[0]*D}
    bound = {'M':m,'A':a,'E':e,'R':N-m-a-e}
    for nurse in d:
        print(nurse,d[nurse])
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

    print('SANITY MATCHED')

def getWeight(e,s,d):
    w=0
    for nurse in range(1,s+1):
        for day in range(1,d+1):
            if(e[nurse][day] == 'M' or e[nurse][day] == 'E'):
                w+=1
    return w


for line,sol in enumerate(data):
    assert type(sol)==type({})
    d = {}
    N,D,m,a,e = map(int,input().split())
    i,j=0,0
    for item in sol:
        if(j%D==0):
            j=0
            i+=1
            d[i]={}
        j+=1
        d[i][j] = sol[item]
    sanity(d,N,D,m,a,e)
    print(getWeight(d,))
    
