from math import degrees
import random
import numpy as np


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
    def itod(self, i):
        a = ['R', 'G', 'B', 'Y', 'T', 'X']
        return a[i]

    # depot to integer (Useful for array indexing)
    def dtoi(self, d):
        a = ['R', 'G', 'B', 'Y', 'T', 'X']
        return a.index(d)

    # Sets random destination out of 4 depots
    def setDest(self):
        i = random.randint(1, 4)
        self.dest = self.itod(i-1)

        while True:
            j = random.randint(1, 4)
            if(j != i):
                self.start = self.itod(i-1)
                break


class State:

    def __init__(self, x, y, p, d):
        self.taxiPos = (x, y)
        self.passenger = p
        self.dest = d

    # Checks if self -> s1 transition possible or not
    def isValidTransition(self, s1):

        pos = s1.taxiPos
        if(pos[1] >= State.map.height or pos[0] < 0 or pos[0] >= State.map.width or pos[1] < 0 or State.map.isWall(self.taxiPos, s1.taxiPos)):
            return False

        return True

    # Gives all possible tranitions from current state (self)
    def getNeighbours(self, a):
        neigh = []

        if(a == 'DROP'):
            depo = 'X'
            for i in ['R', 'G', 'B', 'Y']:
                if(State.map.depots[i] == self.taxiPos):
                    depo = i
                    break
            if(self.passenger == 'T'):
                neigh.append(
                    State(self.taxiPos[0], self.taxiPos[1], depo, self.dest))
            else:
                neigh.append(
                    State(self.taxiPos[0], self.taxiPos[1], 'X', self.dest))

        elif(a == 'PICK'):
            if(self.passenger != 'T' and self.passenger != 'X' and self.taxiPos == self.map.depots[self.passenger]):
                neigh.append(
                    State(self.taxiPos[0], self.taxiPos[1], 'T', self.dest))
            else:
                neigh.append(
                    State(self.taxiPos[0], self.taxiPos[1], 'X', self.dest))
        else:

            for direc in range(2):
                for step in range(-1, 2, 2):
                    pos = [self.taxiPos[0], self.taxiPos[1]]
                    pos[direc] += step
                    neigh.append(
                        State(pos[0], pos[1], self.passenger, self.dest))

        return neigh

    def getNext(self, a):
        neigh = []

        if(a == 'DROP'):
            depo = 'X'
            for i in ['R', 'G', 'B', 'Y']:
                if(State.map.depots[i] == self.taxiPos):
                    depo = i
                    break

            if(self.passenger != 'T'): deop = 'X'
            s1 = State(self.taxiPos[0], self.taxiPos[1], depo, self.dest)

            if(depo == 'X'):
                return s1,-10

            elif(s1.taxiPos == self.map.depots[s1.passenger]):
                if(s1.passenger == s1.dest):
                    return s1,20
                else:
                    return s1,-1

        elif(a == 'PICK'):
            if(self.passenger != 'T' and self.passenger != 'X' and self.taxiPos == self.map.depots[self.passenger]):
                    return State(self.taxiPos[0], self.taxiPos[1], 'T', self.dest),-1
            else:
                    return State(self.taxiPos[0], self.taxiPos[1], 'X', self.dest),-10
        else:

            direc = {
                'N': [0, 1],
                'S': [0, -1],
                'E': [1, 0],
                'W': [-1, 0],
            }

            for i in direc:
                direc[i] = (self.taxiPos[0]+direc[i][0], self.taxiPos[1]+direc[i][1])

            prob = random.uniform(0,1)
            if(prob <= 0.85):
                s1 = State(direc[a][0],direc[a][1],self.passenger,self.dest)
                if(self.isValidTransition(s1)):
                    return s1,-1
                return self,-1

            else:
                i = a
                action = ['N','S','E','W']
                while(i!=a):
                    i = action[random.randint(0,3)]

                s1 = State(direc[i][0],direc[i][1],self.passenger,self.dest)
                if(self.isValidTransition(s1)):
                    return s1,-1
                return self,-1

    def isTerminal(self):
        # if(self.passenger == self.dest and self.taxiPos ==  self.map.depots[self.passenger]):
        if(self.passenger == self.dest):
            return True
        return False

class MDP:
    def __init__(self, m: Map):
        self.map = m
        State.map = m

    # Trnsition function
    def T(self, s: State, a, s1: State):

        if(a == 'PICK'):
            return 1

        elif(a == 'DROP'):
            return 1

        else:

            direc = {
                'N': [0, 1],
                'S': [0, -1],
                'E': [1, 0],
                'W': [-1, 0],
            }

            for i in direc:
                direc[i] = (s.taxiPos[0]+direc[i][0], s.taxiPos[1]+direc[i][1])

            for i in direc:
                if(s1.taxiPos == direc[i] and s.isValidTransition(s1)):
                    if(a == i):
                        return 0.85
                    else:
                        return 0.05

        return 0

    # Reward function
    def R(self, s, a, s1):

        if(a == 'DROP'):
            if(s1.passenger == 'X'):
                return -10

            elif(s1.taxiPos == self.map.depots[s1.passenger]):
                if(s1.passenger == s1.dest):
                    return 20
                else:
                    return -1

        if(a == 'PICK' and s1.passenger == 'X'):
            return -10

        return -1

    # Performs value iteration
    # TODO: have to add max-norm using epsilon
    def valueIteration(self, e):

        V = [[[[0 for k in range(len(self.map.depots))] for l in range(len(
            self.map.depots) + 2)] for i in range(self.map.height)] for j in range(self.map.width)]
        P = [[[['N' for k in range(len(self.map.depots))] for l in range(len(
            self.map.depots) + 2)] for i in range(self.map.height)] for j in range(self.map.width)]

        gamma = 0.9

        changed = True
        i = 0

        while changed:

            changed = False

            for x in range(self.map.width):
                for y in range(self.map.height):
                    for p in range(len(self.map.depots) + 2):
                        for d in range(len(self.map.depots)):

                            s = State(x, y, self.map.itod(p), self.map.itod(d))
                            maxx = None
                            for a in ['PICK', 'DROP', 'N', 'S', 'W', 'E']:

                                neigh = s.getNeighbours(a)
                                if(len(neigh) > 0):
                                    curr = 0
                                    for s1 in neigh:
                                        t = self.T(s, a, s1)

                                        if(t > 0):
                                            # print(s.taxiPos,s.passenger,s.dest, '=>', s1.taxiPos,s1.passenger,s1.dest, a, t, t*(self.R(s,a,s1) + gamma*V[s1.taxiPos[0]][s1.taxiPos[1]][self.map.dtoi(s1.passenger)][self.map.dtoi(s1.dest)]),V[s1.taxiPos[0]][s1.taxiPos[1]][self.map.dtoi(s1.passenger)][self.map.dtoi(s1.dest)])
                                            curr += t*(self.R(s, a, s1) + gamma*V[s1.taxiPos[0]][s1.taxiPos[1]][self.map.dtoi(
                                                s1.passenger)][self.map.dtoi(s1.dest)])
                                    # print('----CURR: ' ,curr)

                                    if(maxx == None or maxx[0] < curr):
                                        maxx = [curr, a]

                            # print(s.taxiPos,s.passenger, s.dest, maxx,'\n')
                            if(maxx != None and abs(maxx[0] - V[x][y][p][d]) > e):
                                changed = True
                                V[x][y][p][d] = maxx[0]
                                P[x][y][p][d] = maxx[1]

                            # print(y,x,p,maxx)

            i += 1
            print('Iteration', i, end='\r')

        for p in range(len(self.map.depots)+1):
            for d in range(len(self.map.depots)):
                print('\nSTART: ', self.map.itod(
                    p), 'DEST: ', self.map.itod(d))
                for y in range(self.map.height-1, -1, -1):
                    for x in range(self.map.width):
                        # print(['{0:.2f}'.format(i) for i in V[y][x][p][d]],end = ', ')
                        print(P[x][y][p][d], end=', ')
                    print()

    def policyIteration(self, e):
        V = [[[[0 for k in range(len(self.map.depots))] for l in range(len(
            self.map.depots) + 2)] for i in range(self.map.height)] for j in range(self.map.width)]
        P = [[[['N' for k in range(len(self.map.depots))] for l in range(len(
            self.map.depots) + 2)] for i in range(self.map.height)] for j in range(self.map.width)]
        i = 0
        j = 0
        changed = True
        gamma = 0.9
        while changed:

            changed = False

            # policy evaluation  step
            for x in range(self.map.width):
                for y in range(self.map.height):
                    for p in range(len(self.map.depots) + 2):
                        for d in range(len(self.map.depots)):

                            s = State(x, y, self.map.itod(p), self.map.itod(d))
                            action = P[x][y][p][d]
                            neigh = s.getNeighbours(action)
                            if len(neigh) > 0:
                                val = 0
                                for neigbours in neigh:
                                    t = self.T(s, action, neigbours)
                                    if (t > 0):
                                        val += t*(self.R(s, action, neigbours)+gamma*V[neigbours.taxiPos[0]][neigbours.taxiPos[1]][self.map.dtoi(
                                            neigbours.passenger)][self.map.dtoi(neigbours.dest)])
                                if (abs(val-V[x][y][p][d]) > e):
                                    changed = True
                                    V[x][y][p][d] = val

            # Policy improvement phase
            if not changed:
                for x in range(self.map.width):
                    for y in range(self.map.height):
                        for p in range(len(self.map.depots) + 2):
                            for d in range(len(self.map.depots)):

                                s = State(x, y, self.map.itod(
                                    p), self.map.itod(d))
                                maxx = None
                                for a in ['PICK', 'DROP', 'N', 'S', 'W', 'E']:

                                    neigh = s.getNeighbours(a)
                                    if(len(neigh) > 0):
                                        curr = 0
                                        for s1 in neigh:
                                            t = self.T(s, a, s1)

                                            if(t > 0):
                                                curr += t*(self.R(s, a, s1) + gamma*V[s1.taxiPos[0]][s1.taxiPos[1]][self.map.dtoi(
                                                    s1.passenger)][self.map.dtoi(s1.dest)])

                                        if(maxx == None or maxx[0] < curr):
                                            maxx = [curr, a]

                                if(maxx != None and maxx[1] != P[x][y][p][d]):
                                    changed = True
                                    P[x][y][p][d] = maxx[1]
                j += 1
            i += 1
            print('Iteration(Policy changes)', j, end='\r')
            print('Iteration(Policy eval)', i, end='\r')
        for p in range(len(self.map.depots)+1):
            for d in range(len(self.map.depots)):
                print('\nSTART: ', self.map.itod(
                    p), 'DEST: ', self.map.itod(d))
                for y in range(self.map.height-1, -1, -1):
                    for x in range(self.map.width):
                        # print(['{0:.2f}'.format(i) for i in V[y][x][p][d]],end = ', ')
                        print(P[x][y][p][d], end=', ')
                    print()

    def policyIteration_l(self):
        w = self.map.width
        h = self.map.height
        de = len(self.map.depots)
        gamma = 0.9
        V = [[[[0 for k in range(len(self.map.depots))] for l in range(len(
            self.map.depots) + 2)] for i in range(self.map.height)] for j in range(self.map.width)]
        P = [[[['N' for k in range(len(self.map.depots))] for l in range(len(
            self.map.depots) + 2)] for i in range(self.map.height)] for j in range(self.map.width)]
        changed = True
        i = 0
        while changed:
            matrix = []
            const = []
            changed = False
            for x in range(self.map.width):
                for y in range(self.map.height):
                    for p in range(len(self.map.depots) + 2):
                        for d in range(len(self.map.depots)):
                            action = P[x][y][p][d]
                            a = [0 for i in range(w*h*de*(de+2))]
                            s = State(x, y, self.map.itod(
                                p), self.map.itod(d))
                            neigh = s.getNeighbours(action)
                            a[x*h*(de+2)*de+y*(de+2)*de+p*de+d] = 1
                            if (len(neigh) > 0):
                                r = 0
                                for s1 in neigh:
                                    t = self.T(s, action, s1)
                                    if (t != 0):
                                        r += t*self.R(s, action, s1)
                                        a[s1.taxiPos[0]*h*(de+2)*de+s1.taxiPos[1]*(de+2)*de+self.map.dtoi(
                                            s1.passenger)*de+self.map.dtoi(s1.dest)] = -1*gamma*t
                                const.append(r)
                            else:
                                const.append(0)
                            matrix.append(a)
            # matrix = np.array(matrix)
            # const = np.array(const)
            ans = np.linalg.solve(np.array(matrix), np.array(const))
            for x in range(self.map.width):
                for y in range(self.map.height):
                    for p in range(len(self.map.depots) + 2):
                        for d in range(len(self.map.depots)):
                            V[x][y][p][d] = ans[x*h *
                                                (de+2)*de+y*(de+2)*de+p*de+d]
            if not changed:
                for x in range(self.map.width):
                    for y in range(self.map.height):
                        for p in range(len(self.map.depots) + 2):
                            for d in range(len(self.map.depots)):

                                s = State(x, y, self.map.itod(
                                    p), self.map.itod(d))
                                maxx = None
                                for a in ['PICK', 'DROP', 'N', 'S', 'W', 'E']:

                                    neigh = s.getNeighbours(a)
                                    if(len(neigh) > 0):
                                        curr = 0
                                        for s1 in neigh:
                                            t = self.T(s, a, s1)

                                            if(t > 0):
                                                curr += t*(self.R(s, a, s1) + gamma*V[s1.taxiPos[0]][s1.taxiPos[1]][self.map.dtoi(
                                                    s1.passenger)][self.map.dtoi(s1.dest)])

                                        if(maxx == None or maxx[0] < curr):
                                            maxx = [curr, a]

                                if(maxx != None and maxx[1] != P[x][y][p][d]):
                                    changed = True
                                    P[x][y][p][d] = maxx[1]
            i += 1
            print('Iteration', i, end='\r')
        for p in range(len(self.map.depots)+1):
            for d in range(len(self.map.depots)):
                print('\nSTART: ', self.map.itod(
                    p), 'DEST: ', self.map.itod(d))
                for y in range(self.map.height-1, -1, -1):
                    for x in range(self.map.width):
                        # print(['{0:.2f}'.format(i) for i in V[y][x][p][d]],end = ', ')
                        print(P[x][y][p][d], end=', ')
                    print()


n = 10000
class RL:
    
    def __init__(self, map: Map):
        self.map = map
        State.map = map

    def generalLearning(self, e, numEpisode , isE_Greedy, isQ):

        Q = [[[[[0 for a in range(6)] for k in range(len(self.map.depots))] 
                for l in range(len(self.map.depots) + 2)] for i in range(self.map.height)] for j in range(self.map.width)]

        alpha = 0.1
        gamma = 0.9

        actions = ['PICK', 'DROP', 'N', 'S', 'W', 'E']

        # Some helper functions

        def getRandomState():
            x = random.randint(0,self.map.width-1)
            y = random.randint(0,self.map.height-1)
            d = self.map.itod(random.randint(1, 4)-1)

            while True:
                p = self.map.itod(random.randint(1, 5)-1)
                if(p!=d):
                    break

            return State(x,y,p,d)

        def getVal(s: State, a):
            return Q[s.taxiPos[0]][s.taxiPos[1]][self.map.dtoi(s.passenger)][self.map.dtoi(s.dest)][a]
        
        def setVal(s: State, a, val):
            Q[s.taxiPos[0]][s.taxiPos[1]][self.map.dtoi(s.passenger)][self.map.dtoi(s.dest)][a] = val

        def getBest(s: State):
            j  = 2
            for i in range(6):
                if(getVal(s,i) > getVal(s,j)):
                    j = i
            return j

        def e_greedy(s,e,it):
            prob = random.uniform(0,1)
            if(prob > e):
                return getBest(s)
            else:
                return random.randint(0,5)

        def decay(s,e,it):
            prob = random.uniform(0,1)
            # TODO: Can change this decay function
            if(prob > e/it):
                return getBest(s)
            else:
                return random.randint(0,5)

        def QLearning(policy,it):
            s = getRandomState()
            while(not s.isTerminal()):
                a = policy(s,e,it)
                s1,r = s.getNext(actions[a])
                val = (1-alpha)*getVal(s,a) + alpha*(r + gamma*getVal(s1,getBest(s1)))
                setVal(s,a,val)
                s = s1
        
        def SARSA(policy,it):
            s = getRandomState()
            a = policy(s,e)
            while(not s.isTerminal()):
                s1,r = s.getNext(actions[a])
                a1 = policy(s1,e,it)
                val = (1-alpha)*getVal(s,a) + alpha*(r + gamma*getVal(s1,a1))
                setVal(s,a,val)
                s = s1
                a = a1

    # ---------------------------------------------------------------------------------

        # Actual Computation

        if(isE_Greedy):
            policy = e_greedy
        else:
            policy = decay

        for _ in range(1,numEpisode+1):
            
            if(isQ):
                QLearning(policy,_)
            else:
                SARSA(policy,_)

            print('Iteration', _, end='\r')

        for p in range(len(self.map.depots)+1):
            for d in range(len(self.map.depots)):
                print('\nSTART: ', self.map.itod(p), 
                        'DEST: ', self.map.itod(d))
                for y in range(self.map.height-1, -1, -1):
                    for x in range(self.map.width):
                        # print(['{0:.2f}'.format(i) for i in Q[y][x][p][d]],end = ', ')
                        print( actions[Q[y][x][p][d].index(max(Q[y][x][p][d]))],end = ', ')
                    print()
        
        return Q

#   Utilise thsese Q table as per output format 

    def Qlearning_E(self,e):
        Q = self.generalLearning(e,n,True,True)
    
    def Qlearning_D(self,e):
        Q = self.generalLearning(e,n,False,True)

    def SARSA_E(self,e):
        Q = self.generalLearning(e,n,True,False)

    def SARSA_D(self,e):
        Q = self.generalLearning(e,n,False,False)



walls = {
    (0, 0): {(1, 0): True},
    (0, 1): {(1, 1): True},
    (1, 3): {(2, 3): True},
    (1, 4): {(2, 4): True},
    (2, 0): {(3, 0): True},
    (2, 1): {(3, 1): True}
}

depots = {
    'Y': (0, 0),
    'R': (0, 4),
    'B': (3, 0),
    'G': (4, 4)
}


# Flow of program: Map created -> destination set -> MDP called -> Value iteration solves MDP -> calls T() and R() in between and makes State class instances
M1 = Map(5, 5, walls, depots)
# M1.setDest()

# mdp = MDP(M1)
# mdp.valueIteration(0.1)
# mdp.policyIteration(0.1)
# mdp.policyIteration_l()

rl = RL(M1)
# rl.Qlearning_E(0.1)
rl.Qlearning_D(0.1)
# rl.SARSA_E(0.1)
# rl.SARSA_D(0.1)
