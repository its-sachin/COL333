from sys import argv
import time
from random import random,randint
import json
from math import log

class CSP:

    def __init__(self,line):

        self.N = int(line[0])
        self.D = int(line[1])
        self.d = int(line[1])
        self.d = min(self.D,8)
        self.bound = {'M':int(line[2]),'A': int(line[3]),'E': int(line[4]), 'R': self.N - int(line[2]) -int(line[3])-int(line[4])}

        if(len(line) == 5):
            self.type = 1
        else:
            self.type = 2
            self.S = int(line[5])
            self.T = int(line[6])
            self.startTime = time.time()

        self.nextNurse =  1
        self.nextDay = 1
        self.next = 1
        self.assigned = 0

        self.assignment = {}

        self.count = {'R':{},'days':{}}
        for i in range(1,self.d+1):
            self.count['days'][i] = {'A':0,'E':0,'M':0,'R':0,'nurse':0}
        for i in range(1,self.N+1):
            self.count['R'][i] = 0

    def dumpAns(self):
        d = {}
        with open("solution.json" , 'w') as file:
            for i in self.assignment:
                for j in self.assignment[i]:
                    d ['N'+str(i-1)+'_'+str(j-1)]=self.assignment[i][j]
            json.dump(d,file)
            file.write("\n")

    
    def checkBounds(self,value,day,notAdded=True):
        d = self.count['days'][day]['A'] + self.count['days'][day]['E'] + self.count['days'][day]['R'] + self.count['days'][day]['M']
        for i in self.bound:
            c=(notAdded and value==i)
            if((self.count['days'][day]['nurse']+c == self.N and self.bound[i] != self.count['days'][day][i] + c) or (self.count['days'][day]['nurse']+c != self.N and (self.bound[i] < self.count['days'][day][i] + c or self.bound[i] > self.N -d -1 +c + self.count['days'][day][i] ))):
                return False
        return True

    def checkRest(self,value,day):
        if(value != 'R'):
            rem = (day)%7
            if(rem!=0):
                l,u = day - rem + 1, day - rem + 8
            else:
                l,u = day - 6, day
            satisfy = False
            for i in range(l,u):
                if(i!= day and (self.assignment.get(self.nextNurse) ==None or self.assignment[self.nextNurse].get(i) == None or self.assignment[self.nextNurse][i]=='R')):
                    satisfy = True
                    break
            if (not satisfy):
                return False
        return True

    def isConsistent(self,value):
        if(value == 'M' and self.nextDay >= 2):
            try:
                prev = self.assignment[self.nextNurse][self.nextDay-1]
                if(prev == 'M' or prev == 'E'):
                    return False
            except:
                pass

        if(self.nextDay <= self.d -1):
            try:
                if('M' == value == self.assignment[self.nextNurse][self.nextDay+1]):
                    return False
            except:
                pass

            try:
                if(value == 'E' and self.assignment[self.nextNurse][self.nextDay+1] == 'M'):
                    return False
            except:
                pass

        return self.checkRest(value,self.nextDay) and self.checkBounds(value,self.nextDay)

    def isComplete(self):
        return self.assigned >= self.N*self.d

    def getValues(self):
        pos = (self.nextNurse,self.nextDay)
        prob = []

        for i in self.bound:
            if(self.bound[i] != 0):

                restScore = 0
                arScore = 0
                if(i=='R'and pos[1] >=2):
                    if(self.count['R'][pos[0]] == 0):
                        restScore=-4
                    else:
                        restScore=1.2
            
                elif(i == 'M' and pos[1] >=2):
                    prev = self.assignment[pos[0]][pos[1]-1]
                    if(prev == 'A' or prev == 'R'):
                        arScore=-1.5
                    
                mrBonus = 0
                if(self.type == 2 and (i=='M' or i=='E')):
                    if(self.nextNurse <= self.S):
                        mrBonus = 0.1
                    else:
                        mrBonus = -0.1

                remScore = self.count['days'][pos[1]][i]/self.bound[i]
                
                score = restScore + 5*arScore + remScore + mrBonus
                # print(pos,i,restScore,arScore,remScore)
                prob.append([score,i])

        out=[]
        prob.sort()
        for i in prob:
            out.append(i[1])
        # print(pos,out)
        return out

    def setNext(self):

        if(self.nextDay==1):
            if(self.nextDay%2==0):
                self.next = -1
            else:
                self.next = 1

            if((self.next == 1 and self.nextNurse == self.N) or (self.next == -1 and self.nextNurse == 1)):
                self.nextDay += 1
                self.setNext()
            else:
                self.nextNurse += self.next

        elif(not self.isComplete()):
            if(self.count['days'][self.nextDay]['M'] != self.bound['M']):
                for i in range(1,self.N+1):
                    if(self.assignment[i][self.nextDay-1]=='R'):
                        try:
                            self.assignment[i][self.nextDay]+'A'
                        except:
                            self.nextNurse = i
                            return
                for i in range(1,self.N+1):
                    if(self.assignment[i][self.nextDay-1]=='A'):
                        try:
                            self.assignment[i][self.nextDay]+'A'
                        except:
                            self.nextNurse = i
                            return

            if(self.count['days'][self.nextDay]['R'] != self.bound['R']):
                for i in range(1,self.N+1):
                    if(self.count['R'][i] == 0):
                        try:
                            self.assignment[i][self.nextDay]+'A'
                        except:
                            self.nextNurse = i
                            return
            
            for i in range(1,self.N+1):
                try:
                    self.assignment[i][self.nextDay]+'A'
                except:
                    self.nextNurse = i
                    return 

            self.nextDay += 1
            self.setNext()

    def addVal(self,value):

        self.assigned += 1
        self.count['days'][self.nextDay][value] += 1
        self.count['days'][self.nextDay]['nurse'] += 1

        if(value=='R'):
            self.count['R'][self.nextNurse] += 1

        if(self.assignment.get(self.nextNurse) == None):
            self.assignment[self.nextNurse] = {self.nextDay:value}
        else:
            self.assignment[self.nextNurse][self.nextDay] = value

    def removeVal(self,value):
        self.assignment[self.nextNurse][self.nextDay] = None
        self.count['days'][self.nextDay][value] -= 1
        self.count['days'][self.nextDay]['nurse'] -= 1
        if(value=='R'):
            self.count['R'][self.nextNurse] -= 1
        self.assigned -= 1

    def build(self):
        conv = []
        pos = {'R':[],'E':[],'A':[],'M':[]}
        for i in range(1,self.N+1):
            pos[self.assignment[i][1]].append(i)
        for i in range(1,self.N+1):
            conv.append(pos[self.assignment[i][8]].pop())

        for i in range(9,self.D+1):
            for j in range(1,self.N+1):
                self.assignment[j][i] = self.assignment[conv[j-1]][i-7]

    def __isSolvable(self):

        if(self.D>=7 and 7*self.bound['R'] < self.N):
            return False
        if(self.bound['A'] + self.bound['R'] < self.bound['M']):
            return False
        if(self.bound['A'] == 0 and self.bound['E'] == 0 and self.bound['M'] > self.N/2):
            return False
        if(self.bound['A']+self.bound['M']+self.bound['E'] > self.N):
            return False
        if(self.bound['R'] == 0 and self.D>=7):
            return False
        return True

    def getWeight(self,e):
        w=0
        for nurse in range(1,self.S+1):
            for day in range(1,self.D+1):
                if(e[nurse][day] == 'M' or e[nurse][day] == 'E'):
                    w+=1
        return w

    def localSearch(self):

        def addR(nurse1,nurse2,day):
            if(E[nurse1][day]=='R' and (day-1)/7<len(self.countR[0]) ):
                self.countR[nurse1][(day-1)/7]-=1
                self.countR[nurse2][(day-1)/7]+=1
            elif(E[nurse2][day]=='R' and (day-1)/7<len(self.countR[0]) ):
                self.countR[nurse2][(day-1)/7]-=1
                self.countR[nurse1][(day-1)/7]+=1
        
        def isPossible(nurse1,nurse2,day):
    
            if(E[nurse1][day] != E[nurse2][day]):
                if(nurse1>nurse2):
                    nurse1,nurse2=nurse2,nurse1

                if((E[nurse1][day]=='R' and (day-1)/7<len(self.countR[0]) and self.countR[nurse1][(day-1)/7]==1) or
                    (E[nurse2][day]=='R' and (day-1)/7<len(self.countR[0]) and self.countR[nurse2][(day-1)/7]==1)):
                    return False

                def check(p1,p2):
                    if(E[p1][day] == 'M'):
                        try:
                            if(E[p2][day+1] == 'M'):
                                return False
                        except:
                            pass
                        try:
                            if(E[p2][day-1] == 'M' or E[p2][day-1] =='E'):
                                return False
                        except:
                            pass
                    
                    elif(E[p1][day] == 'E'):
                        try:
                            if(E[p2][day+1] == 'M'):
                                return False
                        except:
                            pass
                    return True   

                return check(nurse1,nurse2) and check(nurse2,nurse1)   
            return False 

        def deterministic():

            maxNeighbours = {}
            day = 1
            while(day<= self.D):
                currTop,currBottom=[],[]

                for nurse in range(1,self.N+1):
                    val = E[nurse][day]
                    if(nurse<=self.S):
                        if(val== 'A' or (val == 'R' and ((day-1)/7>=len(self.countR[0]) or self.countR[nurse][(day-1)//7] >1) )):
                            if(day==self.D or E[nurse][day+1]=='E'):
                                currTop.append([0,nurse])
                            else:
                                currTop.append([5,nurse])
                    else:
                        if(len(currTop)==0):
                            break
                        if(val=='M' or val=='E'):
                            if(val=='E'):
                                currBottom.append([0,nurse])
                            else:
                                currBottom.append([5,nurse])
                if(len(currTop) > 0 and len(currBottom) > 0):
                    maxNeighbours[day] = [currTop,currBottom]
                day+=1

            # def isPossible(up,bp,day):
            #     if(day<self.D and E[up][day+1]=='M'):
            #         return False
            #     if(E[bp][day] == 'M' and day>1 and (E[up][day-1] == 'E' or E[up][day-1] == 'M')):
            #         return False
            #     return True

            if(len(maxNeighbours)>0):
                
                pos=[]
                for day in maxNeighbours:
                    currTop,currBottom=  maxNeighbours[day][0],maxNeighbours[day][1]
                    for t in currTop:
                        for b in currBottom:
                            if(isPossible(t[1],b[1],day) and (pos==[] or t[0]+b[0] < pos[2])):
                                pos = [ [t[1],day], [b[1],day], t[0] + b[0] ]   
                if(len(pos)>0):
                    print('DETERMINISTIC EXCHANGE',pos)
                    addR(pos[0][0],pos[1][0],pos[0][1])
                    E[pos[0][0]][pos[0][1]],E[pos[1][0]][pos[1][1]] = E[pos[1][0]][pos[1][1]],E[pos[0][0]][pos[0][1]]
                    self.sanity(E)
                    return True
            return False

        def randomize(thres):
            
            done = {}
            for i in range(int(thres)):
                day = randint(1,self.D)
                print('NEW Day',day)
                if(done.get(day)==None):
                    done[day] = []
                got =False
                nurse1 = 1
                while(nurse1 <= self.N and not got):
                    nurse2 = self.N
                    while(nurse2 > 0 and not got):
                        if(nurse1!=nurse2 and (done.get(day) == None or [min(nurse1,nurse2),max(nurse1,nurse2)] not in done[day]) and isPossible(nurse1,nurse2,day)):
                            print('RANDOMIZED EXCHANGE',nurse1,nurse2,day)
                            E[nurse1][day],E[nurse2][day] = E[nurse2][day],E[nurse1][day]
                            done[day].append([min(nurse1,nurse2),max(nurse1,nurse2)])
                            got =True
                        nurse2-=1
                    nurse1+=1
                self.sanity(E)

        def deepCopy(e):
            copy={}
            for i in e:
                copy[i] = {}
                for j in e[i]:
                    copy[i][j] = e[i][j] 
            return copy
            
        done = False
        E,X,it = deepCopy(self.assignment),self.maxWeight,1
        while ((not done) and time.time()-self.startTime < self.T):
            if(not deterministic()):
                
                thres = min(-1*(log(random())*self.T/10*it),self.D+self.N)
                print('threshold = ', thres)
                if(thres >= 1):
                    randomize(thres)
                    it+=1
                    X = self.getWeight(E)
                else:
                    done = True

            else:
                X+=1
                
            print('weight = ',X,'\n')
            if(X > self.maxWeight):
                self.maxWeight,self.assignment = X,deepCopy(E)
                self.dumpAns()

            if(self.maxWeight!=self.getWeight(self.assignment)):
                self.sanity()
                print(self.maxWeight,self.getWeight(self.assignment))
                print('GAND MAR GAYI')
                exit()



        

            

    def maximize(self):

        self.countR = {j: [0 for i in range((self.D-1)//7)] for j in range(self.N)}
        weights = []
        for i in range(1,self.N+1):
            c = 0
            for j in range(1,self.D+1):
                if(self.assignment[i][j] == 'M' or self.assignment[i][j] == 'E'):
                    c+=2
                elif(self.assignment[i][j] == 'R' and (j-1)/7 < len(self.countR[0])):
                    self.countR[i-1][(j-1)//7] +=1
            weights.append([c,i])
            
        weights.sort(reverse=True)

        maxDict = {}
        for i in range(self.N):
            maxDict[i+1] = self.assignment[weights[i][1]]
            for j in range(1,self.D+1):
                maxDict[i+1][j] = self.assignment[weights[i][1]][j]
        self.assignment,self.maxWeight = maxDict,self.getWeight(maxDict)

        print('\n\nMAX FINDING STARTS')
        self.sanity()
        self.dumpAns()
        self.localSearch()

    def backtrackingSearch(self):
        if (self.isComplete()):
            if(self.D > self.d):
                self.build()

            self.dumpAns()
            if(self.type==2):
                self.maximize()
            return self.assignment

        # print('Assigment\n')
        # for i in self.assignment:
        #     print(i ,'- [', self.assignment[i], ']')
        # print('\n')
        try:
            self.st
        except:
            self.st = time.time()
        # if(time.time()-self.st > 200):
        #     return -1
        print(round(100*self.assigned/(self.N*self.d),2),'\t',round(time.time()-self.st,2),end='\r')

        for value in self.getValues():
            # print('checkig',value)
            if(self.isConsistent(value)):

                prev = (self.nextNurse,self.nextDay)
                self.addVal(value) 
                self.setNext()

                result = self.backtrackingSearch()
                if(result!=None):
                    return result

                self.nextNurse,self.nextDay = prev
                self.removeVal(value)

        return None

    def solve(self):
        if(self.__isSolvable()):
            # print('SOLVING')
            return self.backtrackingSearch()

    def sanity(self,d={}):
        if(d=={}):
            d=self.assignment
        count = {'M':[0]*self.D,'A':[0]*self.D,'E':[0]*self.D,'R':[0]*self.D}
        for nurse in d:
            print(nurse,d[nurse])
            for day in d[nurse]:
                if(day < self.D and ( d[nurse][day] == d[nurse][day+1] == 'M' or (d[nurse][day] == 'E' and d[nurse][day+1] == 'M'))):
                    print('NURSE',nurse,' EM/MM AT',day)
                    return
                val=d[nurse][day]
                count[val][day-1] += 1
        for i in count:
            for j in count[i]:
                if(i != 'R' and j != self.bound[i]):
                    print('DAY',i,'NOT MATCHING AT',j)
                    return

        for nurse in d:
            got = False
            day = 1
            while(day <= self.D):
                if(d[nurse][day]  == 'R'):
                    got = True
                if(day%7==0):
                    if(not got):
                        print('NURSE',nurse,'NO REST',day)
                        return 
                    got = False
                day +=1

        print('SANITY MATCHED')
#  ------------------------------------------------------------

try:
    inputFileName = argv[1]
except:
    print('Please enter the input file name')
    exit()

try:
    inputFile = open(inputFileName,'r+')
except:
    print('Input file doest not exists')
    exit()

line = inputFile.readline()
line = inputFile.readline()

def pr(csp):
    d = csp.solve()
    if(d==None):
        print('NOT POSSIBLE')
        return
    else:
        print('POSSIBLE')
        # csp.sanity()

st = time.time()
i=0
while(line):
    line = line.strip().split(',')

    if(len(line) > 0):
        csp = CSP(line)
        # print('ans',csp.solve())
        pr(csp)
    line = inputFile.readline()
    i+=1
    # print(i)

# print(time.time()-st)