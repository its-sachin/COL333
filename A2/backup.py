class CSP:
    
    def __init__(self):

        self.N =5
        self.D =15
        # self.bound = {'M':int(line[2]),'A': int(line[3]),'E': int(line[4]), 'R': self.N - int(line[2]) -int(line[3])-int(line[4])}

        self.nextNurse =  1
        self.nextDay = 1
        self.next = 1

        self.assignment = {
            1: {1: 'E', 2: 'E', 3: 'E', 4: 'E', 5: 'R', 6: 'M',7: 'E', 8: 'E', 9: 'E', 10: 'E', 11: 'A', 12: 'M', 13: 'E', 14: 'A', 15: 'M'}, 
            2: {1: 'E', 2: 'E', 3: 'R', 4: 'E', 5: 'E', 6: 'E',7: 'E', 8: 'E', 9: 'E', 10: 'E', 11: 'A', 12: 'M', 13: 'E', 14: 'A', 15: 'M'}, 
            3: {1: 'M', 2: 'A', 3: 'M', 4: 'A', 5: 'M', 6: 'R',7: 'E', 8: 'E', 9: 'E', 10: 'E', 11: 'A', 12: 'M', 13: 'E', 14: 'A', 15: 'M'}, 
            4: {1: 'M', 2: 'A', 3: 'M', 4: 'A', 5: 'M', 6: 'R',7: 'E', 8: 'E', 9: 'E', 10: 'E', 11: 'A', 12: 'M', 13: 'E', 14: 'A', 15: 'M'}, 
            5: {1: 'M', 2: 'A', 3: 'M', 4: 'A', 5: 'M', 6: 'R',7: 'E', 8: 'E', 9: 'E', 10: 'E', 11: 'A', 12: 'M', 13: 'E', 14: 'A', 15: 'M'}}

        self.count = {}
        for i in range(1,self.D+1):
            self.count[i] = {'A':0,'E':0,'M':0,'R':0,'nurse':0}
        self.assigned = 0

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

    def sanity(self):
        count = {'M':[0]*self.D,'A':[0]*self.D,'E':[0]*self.D,'R':[0]*self.D}
        d = self.assignment

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
c=CSP()
c.sanity()
# bound = {'M':3,'A': 3,'E': 3, 'R': 1}        
# pos = list(map(int,input().split()))

# count = {}
# for i in range(1,11):
#     count[i] = {'A':0,'E':0,'M':0,'R':0,'nurse':0}

# d = 
    
# for nurse in d:
#     for day in d[nurse]:
#         val=d[nurse][day]
#         if(val):
#             count[day][val] += 1
# prob = []
# for i in bound:
#     prob.append([count[pos[1]][i]/bound[i],i])

# prob.sort()
# out=[]
# for i in prob:
#     out.append(i[1])
# print(out)