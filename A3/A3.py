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
        a = ['R','G','B','Y','T']
        return a[i]

    # depot to integer (Useful for array indexing)
    def dtoi(self,d):
        a = ['R','G','B','Y','T']
        return a.index(d)

    # Sets random destination out of 4 depots
    def setDest(self):
        i = random.randint(1,4)
        self.dest = self.itod(i-1)
        

class State:

    def __init__(self,x,y,p):
        self.taxiPos = (x,y)
        self.passenger = p

    # Checks if self -> s1 transition possible or not
    def isValidTransition(self,s1):
        
        pos = s1.taxiPos
        if(State.map.isWall(self.taxiPos,s1.taxiPos) or pos[0] >= State.map.height or pos[0] < 0 or pos[1] >= State.map.width or pos[1] < 0):
            return False

        return False

    # Gives all possible tranitions from current state (self)
    def getNeighbours(self):
        neigh = []
        for direc in range(2):
            for step in range(-1,2,2):
                pos = [self.taxiPos[0],self.taxiPos[1]]
                pos[direc] += step
                s1 = State(pos[0],pos[1],self.passenger)
                if(self.isValidTransition(s1)):
                    neigh.append(s1)

        depo = None
        for i in ['R','G','B','Y']:
            if(State.map.depots[i] == self.taxiPos):
                depo = i
                break
        
        # Assumed PICK and DROP only possible on depots
        if(depo):
            neigh.append(State(self.taxiPos[0],self.taxiPos[1],depo))
            neigh.append(State(self.taxiPos[0],self.taxiPos[1],'T'))
        
        return neigh

        

class MDP:
    def __init__(self,m:Map):
        self.map = m
        State.map = m

    # Trnsition function 
    def T(self,s:State ,a ,s1:State):

        if(a == 'PICK'):
            if(s.passenger != 'T' and s1.passenger == 'T'):
                return 1

        elif(a == 'DROP'):
            if(s.passenger == 'T' and s1.passenger != 'T'):
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
        reward = -1

        if(a == 'DROP'):
            if(s1.passenger == self.map.dest):
                reward += 20
            else:
                reward -= 10

        if(a == 'PICK' and s.passenger != self.map.dest):
            reward -= 10

        return reward

    # Performs value iteration
    # TODO: have to add max-norm using epsilon
    def valueIteration(self, e):

        V = [[[0 for k in range(len(self.map.depots) +1)] for i in range(self.map.width)] for j in range(self.map.height)]
        y = 0.9

        changed = True
        i = 0

        while changed:

            changed = False

            for y in range(self.map.height):
                for x in range(self.map.width):
                    for p in range(len(self.map.depots) +1):
                            
                        s = State(x,y,self.map.itod(p))
                        maxx = None
                        for a in ['N','S','W','E','PICK','DROP']:
                            curr = 0

                            for s1 in s.getNeighbours():
                                t = self.T(s,a,s1)

                                if(t>0):
                                    curr += t*(self.R(s,a,s1) + y*V[s1.taxiPos[1]][s1.taxiPos[0]][self.map.dtoi(s1.passenger)])
                            
                            # print(curr)
                            
                            if(maxx == None or maxx[0] < curr):
                                maxx = [curr,a]
                        
                        if(maxx != None and maxx[0] != V[y][x][p]):
                            changed = True
                             # TODO: Right now only value is stored, but have to store final policies somewhere
                            V[y][x][p] = maxx[0]

                        # print(y,x,p,maxx)

            i+=1
            print('Iteration',i,end='\r')

        for y in range(self.map.height):
            for x in range(self.map.width):
                print(V[y][x],end = ', ')
            print()  

                
                            



    def policyIteration(self):
        pass


class RL:
    def __init__(self,map:Map):
        self.map = map  


walls = {
    (0,0):(0,1), 
    (1,0):(1,1),
    (3,1):(3,2),
    (4,1):(4,2),
    (0,2):(0,3),
    (1,2):(1,3)
}

depots = {
    'R' : (0,0),
    'G' : (4,0),
    'B' : (0,3),
    'Y' : (4,4)
}


# Flow of program: Map created -> destination set -> MDP called -> Value iteration solves MDP -> calls T() and R() in between and makes State class instances 
M1 = Map(5,5,walls,depots)
M1.setDest()

mdp = MDP(M1)
mdp.valueIteration(0.1)
        

