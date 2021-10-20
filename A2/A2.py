from sys import argv

class CSP:

    def __init__(self,line):

        self.N = int(line[0])
        self.D = int(line[1])
        self.m = int(line[2])
        self.a = int(line[3])
        self.e = int(line[4])

        if(len(line) == 5):
            self.type = 1
        else:
            self.type = 2
            self.S = int(line[5])
            self.T = int(line[6])

        self.last = 1
        self.dict = {}
        for i in range(1,self.N+1):
            self.dict[i] = []
        self.values = ['M','A','E','R']

    def isComplete(self):
        return self.last > self.N

    def addVal(self,value):
        self.dict[self.last].append(value)
        if(len(self.dict[self.last]) == self.D):
            self.last += 1

    def removeVal(self,value):
        if(len(self.dict[self.last]) == 0):
            self.last -= 1
        self.dict[self.last].pop()

    def isConsistent(self,value):

        if(len(self.dict[self.last]) >0 and (self.dict[self.last][-1] == value == 'M' or (value == 'M' and self.dict[self.last][-1] == 'E'))):
            return False

        if(len(self.dict[self.last]) >0 and len(self.dict[self.last])%7 == 0 and value != 'R'):
            for i in range(-6,0,-1):
                if(self.dict[self.last][i]=='R'):
                    break
            else:
                return False

        day = len(self.dict[self.last])
        # print(self.dict)
        count = {'M':0,'A':0,'E':0,'R':0}
        count[value] +=1
        
        for i in range(1,self.last):
            count[self.dict[i][day]] += 1

        if( (count['M'] > self.m or count['A'] > self.a or count['E'] > self.e) or ((self.last == self.N) and (count['M'] != self.m or count['A'] != self.a or count['E'] != self.e))):
            return False

        return True


    def backtrackingSearch(self):
        if (self.isComplete()):
            return self.dict

        for value in self.values:
            if(self.isConsistent(value)):
                # print(self.last, len(self.dict[self.last]),value)
                self.addVal(value)
                result = self.backtrackingSearch()
                if(result):
                    return result
                self.removeVal(value)
                
        return None

        


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

def pr(d):
    count = {'M':[0]*7,'A':[0]*7,'E':[0]*7}
    for i in d:
        print(d[i])
        dy = 0
        for j in d[i]:
            if(j!='R'):
                count[j][dy] += 1
            dy += 1
    print(count,'\n')

while(line):
    line = line.strip().split(',')

    if(len(line) > 0):
        csp = CSP(line)
        pr(csp.backtrackingSearch())
    line = inputFile.readline()