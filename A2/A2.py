from sys import argv
import time
from collections import deque
from random import randint

class CSP:

    def __init__(self,line):

        self.N = int(line[0])
        self.D = int(line[1])
        self.bound = {'M':int(line[2]),'A': int(line[3]),'E': int(line[4]), 'R': self.N - int(line[2]) -int(line[3])-int(line[4])}

        if(len(line) == 5):
            self.type = 1
        else:
            self.type = 2
            self.S = int(line[5])
            self.T = int(line[6])

        self.nextNurse =  1
        self.nextDay = 1
        self.next = 1

        self.assignment = {}

        self.count = {}
        for i in range(1,self.D+1):
            self.count[i] = {'A':0,'E':0,'M':0,'R':0,'nurse':0}
        self.assigned = 0
    
    def checkBounds(self,value,day,notAdded=True):
        d = self.count[day]['A'] + self.count[day]['E'] + self.count[day]['R'] + self.count[day]['M']
        for i in self.bound:
            c=(notAdded and value==i)
            if((self.count[day]['nurse']+c == self.N and self.bound[i] != self.count[day][i] + c) or (self.count[day]['nurse']+c != self.N and (self.bound[i] < self.count[day][i] + c or self.bound[i] > self.N -d -1 +c + self.count[day][i] ))):
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

        if(self.nextDay <= self.D -1):
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

    def revConsistent(self,xi,xj,value1,value2,domain):

        nurse = self.nextNurse
        if(not (self.checkBounds(value1,xi,self.assignment.get(nurse) == None or self.assignment[nurse].get(xi) == None) or
                self.checkBounds(value2,xj,self.assignment.get(nurse) == None or self.assignment[nurse].get(xj) == None))):
            # print('inference false for bound at [',nurse,xi,value1,'] [',nurse,xj,value2,']')
            return False

        if(xi>xj):
            xi,xj=xj,xi
            value1,value2=value2,value1

        if(value1 == 'M' == value2 or (value1 == 'E' and value2 == 'M')):
            # print('inference false for consec at [',nurse,xi,value1,'] [',nurse,xj,value2,']')
            return False

        rem = xi%7
        if(value1 != 'R'):
            if(rem!=0):
                l,u = xi - rem + 1, xi - rem + 8
            else:
                l,u = xi - 6, xi
            satisfy = False
            for i in range(l,u):
                if(i != xi and ((i == xj and value2 == 'R') or ( i != xj and (i <=0 or i > self.D or'R' in domain[nurse][i])))):
                    satisfy = True
                    break
            if (not satisfy):
                # print('inference false for rest at [',nurse,xi,value1,'] [',nurse,xj,value2,']')
                return False
        if(rem == 0 and value2 != 'R'):
            l,u = xj+1,xj+7
            satisfy = False
            for i in range(l,u):
                if(i > self.D or 'R' in domain[nurse][i]):
                    satisfy = True
                    break
            if(not satisfy):
                # print('inference false for rst2 at [',nurse,xi,value1,'] [',nurse,xj,value2,']')
                return False


        return True

    def revise(self,xi,xj,domain):
        revised = False
        index=0
        while(index < len(domain[xi])):
            value1 = domain[xi][index]
            satisfy = False
            for value2 in domain[xj]:
                if(self.revConsistent(xi,xj,value1,value2,domain)):
                    satisfy = True
                    break

            if(not satisfy):
                # print('interference removing',value1,xi)
                domain[xi].pop(index)
                index -= 1
                revised = True
            index+=1
        return revised

    def inference(self,value):
        queue = deque()
        domain = {}

        i = self.nextNurse
        for j in range(1,self.D+1):
            if(self.assignment.get(i) != None and self.assignment[i].get(j)!=None):
                domain[j] = [self.assignment[i][j]]
            else:   
                domain[j] = ['A','R','E','M']
        domain[self.nextDay] = [value]
        # maybe narraw it down
        
        # for n in range(1,self.N+1):
        for i in range(1,self.D):
            queue.append([i,i+1])

        while(len(queue)>0):
            xi,xj = queue.popleft()
            if(self.revise(xi,xj,domain)):
                if(len(domain[xi[0]][xi[1]]) == 0):
                    return False
                if(xj == xi+1 and xi >=2):
                    queue.append([xi-1,xi])
                elif(xj == xi-1 and xi <= self.D-1):
                    queue.append([xi+1,xi])
                
        return True

    def isComplete(self):
        return self.assigned >= self.N*self.D

    def getValues(self):
        pos = (self.nextNurse,self.nextDay)
        prob = []
        for i in self.bound:
            prob.append([self.count[pos[1]][i],i])

        prob.sort(reverse=True)
        out=[]
        for i in prob:
            out.append(i[1])
        return out

    def setNext(self):

        if(self.nextDay%2==0):
            self.next = -1
        else:
            self.next = 1

        if((self.next == 1 and self.nextNurse == self.N) or (self.next == -1 and self.nextNurse == 1)):
            self.nextDay += 1
        else:
            self.nextNurse += self.next

    def addVal(self,value):

        self.assigned += 1
        self.count[self.nextDay][value] += 1
        self.count[self.nextDay]['nurse'] += 1

        if(self.assignment.get(self.nextNurse) == None):
            self.assignment[self.nextNurse] = {self.nextDay:value}
        else:
            self.assignment[self.nextNurse][self.nextDay] = value

    def removeVal(self,value):
        self.assignment[self.nextNurse][self.nextDay] = None
        self.count[self.nextDay][value] -= 1
        self.count[self.nextDay]['nurse'] -= 1
        self.assigned -= 1

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

    def backtrackingSearch(self):
        if (self.isComplete()):
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
        print(round(100*self.assigned/(self.N*self.D),2),'\t',round(time.time()-self.st,2),end='\r')

        for value in self.getValues():
            if(self.isConsistent(value) and self.isConsistent(value) ):

                prev = (self.nextNurse,self.nextDay)
                self.addVal(value) 
                self.setNext()

                result = self.backtrackingSearch()
                if(result!=None):
                    return result

                self.nextNurse,self.nextDay = prev
                self.removeVal(value)
            # elif(not self.isConsistent(value)):
            #     print('----NOT CONSISTENT' , value, 'FOR', self.nextNurse,self.nextDay)
            # else:
            #     print('----NOT INFERENCE' , value, 'FOR', self.nextNurse,self.nextDay)


        return None

    def solve(self):
        if(self.__isSolvable()):
            print('SOLVING')
            return self.backtrackingSearch()

    def sanity(self):
        count = {'M':[0]*self.D,'A':[0]*self.D,'E':[0]*self.D,'R':[0]*self.D}
        d = self.assignment
        for nurse in d:
            print(d[nurse])
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
        # if(d==-1):
        #     print('TIMEOUT')
        # else:
        #     print('POSSIBLE')
        csp.sanity()

st = time.time()
while(line):
    line = line.strip().split(',')

    if(len(line) > 0):
        csp = CSP(line)
        # print('ans',csp.solve())
        pr(csp)
    line = inputFile.readline()

print(time.time()-st)