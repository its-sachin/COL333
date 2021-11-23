from math import degrees
import random

class Map:
    def __init__(self, height, width, walls, depots):
        self.height = height
        self.width = width
        self.walls = walls
        self.depots = depots

    # Checks if there is any wall between cell point1 and cell point2 
    def isWall(self, point1, point2):
        try:
            a = self.walls[point1][point2]
        except:
            try:
                a = self.walls[point2][point1]
            except:
                return False
        return True

    # integer to depot
    def itod(self,i):
        a = ['R','G','B','Y','T','X']
        return a[i]

    # depot to integer (Useful for array indexing)
    def dtoi(self,d):
        a = ['R','G','B','Y','T','X']
        return a.index(d)

    # Sets random destination out of 4 depots
    def setDest(self):
        i = random.randint(1,4)
        self.dest = self.itod(i-1)

        while True:
            j = random.randint(1,4)
            if(j != i):
                self.start = self.itod(i-1)
                break
        

class State:

    def __init__(self,x,y,p,d):
        self.taxiPos = (x,y)
        self.passenger = p
        self.dest = d

    # Checks if self -> s1 transition possible or not
    def isValidTransition(self,s1):
        
        pos = s1.taxiPos
        if(State.map.isWall(self.taxiPos,s1.taxiPos) or pos[0] >= State.map.height or pos[0] < 0 or pos[1] >= State.map.width or pos[1] < 0):
            return False

        return True

    # Gives all possible tranitions from current state (self)
    def getNeighbours(self,a):
        neigh = []
        
        if(a == 'DROP'):
            depo = 'X'
            for i in ['R','G','B','Y']:
                if(State.map.depots[i] == self.taxiPos):
                    depo = i
                    break
            neigh.append(State(self.taxiPos[0],self.taxiPos[1],depo,self.dest))

        elif(a == 'PICK'):
            if(self.passenger != 'T' and self.passenger != 'X' and self.taxiPos == self.map.depots[self.passenger]):
                neigh.append(State(self.taxiPos[0],self.taxiPos[1],'T',self.dest))
            else:
                neigh.append(State(self.taxiPos[0],self.taxiPos[1],'X',self.dest))
        else:

            for direc in range(2):
                for step in range(-1,2,2):
                    pos = [self.taxiPos[0],self.taxiPos[1]]
                    pos[direc] += step

                    s1 = State(pos[0],pos[1],self.passenger,self.dest)
                    if(self.isValidTransition(s1)):
                        neigh.append(s1)
        
        return neigh

        

class MDP:
    def __init__(self,m:Map):
        self.map = m
        State.map = m

    # Trnsition function 
    def T(self,s:State ,a ,s1:State):

        if(a == 'PICK'):
            return 1

        elif(a == 'DROP'):
            return 1

        else:

            direc = { 
                'N' : [0,1],
                'S' : [0,-1],
                'E' : [1,0],
                'W' : [-1,0],
            }

            for i in direc:
                direc[i] = (s.taxiPos[0]+direc[i][0],s.taxiPos[1]+direc[i][1])

            for i in direc:
                if(s1.taxiPos == direc[i]):
                    if(a==i):
                        return 0.85
                    else:
                        return 0.05

        return 0

    # Reward function
    def R(self,s,a,s1):

        if(a == 'DROP'):
            if(s.passenger == 'T' and s1.passenger == s1.dest):
                return 20
            else:
                return -10
        
        if(a == 'PICK' and s1.passenger == 'X'):
            return -10

        return -1

    # Performs value iteration
    # TODO: have to add max-norm using epsilon
    def valueIteration(self, e):

        V = [[[[0 for k in range(len(self.map.depots))] for l in range(len(self.map.depots) + 2)] for i in range(self.map.width)] for j in range(self.map.height)]
        P = [[[[None for k in range(len(self.map.depots))] for l in range(len(self.map.depots) + 2)] for i in range(self.map.width)] for j in range(self.map.height)]

        gamma = 0.9

        changed = True
        i = 0

        while changed:

            changed = False

            for x in range(self.map.width):
                for y in range(self.map.height):
                    for p in range(len(self.map.depots) +2):
                        for d in range(len(self.map.depots)):
                            
                            s = State(x,y,self.map.itod(p),self.map.itod(d))
                            maxx = None
                            for a in ['PICK','DROP','N','S','W','E']:

                                neigh = s.getNeighbours(a)
                                if(len(neigh) > 0):
                                    curr = 0
                                    for s1 in neigh:
                                        t = self.T(s,a,s1)
                                        # print(s.taxiPos,s.passenger,s.dest, '=>', s1.taxiPos,s1.passenger,s1.dest, a, t, t*(self.R(s,a,s1) + gamma*V[s1.taxiPos[1]][s1.taxiPos[0]][self.map.dtoi(s1.passenger)][self.map.dtoi(s1.dest)]),V[s1.taxiPos[1]][s1.taxiPos[0]][self.map.dtoi(s1.passenger)][self.map.dtoi(s1.dest)])

                                        if(t>0):
                                            curr += t*(self.R(s,a,s1) + gamma*V[s1.taxiPos[1]][s1.taxiPos[0]][self.map.dtoi(s1.passenger)][self.map.dtoi(s1.dest)])
                                    # print('----CURR: ' ,curr)

                                    if(maxx == None or maxx[0] < curr):
                                        maxx = [curr,a]
                            
                            # print(s.taxiPos,s.passenger, s.dest, maxx,'\n')
                            if(maxx != None and abs(maxx[0] - V[y][x][p][d]) > e):
                                changed = True
                                V[y][x][p][d] = maxx[0]
                                P[y][x][p][d] = maxx[1]

                            # print(y,x,p,maxx)

            i+=1
            print('Iteration',i,end='\r')

        for p in range(len(self.map.depots)+1):
            for d in range(len(self.map.depots)):
                print('\nSTART: ',self.map.itod(p), 'DEST: ', self.map.itod(d))
                for y in range(self.map.height-1,-1,-1):
                    for x in range(self.map.width):
                        # print(['{0:.2f}'.format(i) for i in V[y][x][p][d]],end = ', ')
                        print(P[y][x][p][d],end = ', ')
                    print()  

                
                            



    def policyIteration(self):
        pass


class RL:
    def __init__(self,map:Map):
        self.map = map  


walls = {
    (0,0):(1,0), 
    (0,1):(1,1),
    (1,3):(2,3),
    (1,4):(2,4),
    (2,0):(3,0),
    (2,1):(3,1)
}

depots = {
    'Y' : (0,0),
    'R' : (0,4),
    'B' : (3,0),
    'G' : (4,4)
}


# Flow of program: Map created -> destination set -> MDP called -> Value iteration solves MDP -> calls T() and R() in between and makes State class instances 
M1 = Map(5,5,walls,depots)
# M1.setDest()

mdp = MDP(M1)
mdp.valueIteration(0.1)
        

