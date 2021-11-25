from math import degrees
import random
import numpy as np
from numpy.core.fromnumeric import shape
from matplotlib import pyplot as plt


class Map:
    def __init__(self, height, width, walls, depots):
        self.height = height
        self.width = width
        self.walls = walls
        self.depots = depots

        self.dests = list(self.depots.keys())

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
        return self.dests[i]

    # depot to integer (Useful for array indexing)
    def dtoi(self, d):
        return self.dests.index(d)
        

class State:

    def __init__(self, p1, p2, p, d):
        self.taxiPos = (p1[0], p1[1])
        self.passengerPos = p2
        self.picked = p
        self.dest = d

    # Checks if self -> s1 transition possible or not
    def isValidTransition(self, s1):

        pos = s1.taxiPos
        if(pos[1] >= State.map.height or pos[0] < 0 or pos[0] >= State.map.width or pos[1] < 0 or State.map.isWall(self.taxiPos, s1.taxiPos)):
            return False

        return True

    # Reward function
    def R(self, a, s1):

        if(a == 'DROP'):
            if(self.picked and s1.isTerminal()):
                return 20
            elif(s1.passengerPos != s1.taxiPos):
                return -10
            return -1

        if(a == 'PICK' and s1.passengerPos != s1.taxiPos):
            return -10

        return -1

    # Gives all possible tranitions from current state (self)
    def getNeighbours(self, a):
        neigh = []

        if(self.isTerminal()):
            return neigh

        if(a == 'DROP'):
            if(self.picked):
                neigh.append(
                    State(self.taxiPos, self.taxiPos, False, self.dest))
            else:
                neigh.append(
                    State(self.taxiPos, self.passengerPos, self.picked, self.dest))

        elif(a == 'PICK'):
            if((not self.picked) and self.taxiPos == self.passengerPos):
                neigh.append(
                    State(self.taxiPos, self.taxiPos, True, self.dest))
            else:
                neigh.append(
                    State(self.taxiPos, self.passengerPos, self.picked, self.dest))
        else:

            for direc in range(2):
                for step in range(-1, 2, 2):
                    pos = [self.taxiPos[0], self.taxiPos[1]]
                    pos[direc] += step
                    pos2 = self.passengerPos
                    if(self.picked):
                        pos2 = pos
                    s1 = State(pos, pos2, self.picked, self.dest)
                    if(self.isValidTransition(s1)):
                        neigh.append(s1)
            neigh.append(State(self.taxiPos, self.passengerPos, self.picked, self.dest))

        return neigh

    # Gives (next_state,reward) pair for any (state,action) pair
    def getNext(self, a):

        if(a == 'DROP' or a == 'PICK'):
            s1 = self.getNeighbours(a)[0]
            return s1, self.R(a, s1)
        else:

            direc = {
                'N': [0, 1],
                'S': [0, -1],
                'E': [1, 0],
                'W': [-1, 0],
            }

            for i in direc:
                direc[i] = (self.taxiPos[0]+direc[i][0],
                            self.taxiPos[1]+direc[i][1])

            prob = random.uniform(0, 1)
            if(prob <= 0.85):
                if(self.picked):
                    s1 = State(direc[a], direc[a], True, self.dest)
                else:
                    s1 = State(direc[a], self.passengerPos, False, self.dest)
                # print(s1.taxiPos,s1.passengerPos,s1.picked)
                if(self.isValidTransition(s1)):
                    return s1, -1
                return self, -1

            else:
                i = a
                action = ['N', 'S', 'E', 'W']
                while(i == a):
                    i = action[random.randint(0, 3)]

                if(self.picked):
                    s1 = State(direc[i], direc[i], True, self.dest)
                else:
                    s1 = State(direc[i], self.passengerPos, False, self.dest)
                if(self.isValidTransition(s1)):
                    return s1, -1
                return self, -1

    # Checks if state is terminal or not
    def isTerminal(self):
        # print(self.taxiPos,self.passengerPos,self.picked,self.dest)
        # if(self.passenger == self.dest and self.taxiPos ==  self.map.depots[self.passenger]):
        if((not self.picked) and self.passengerPos == State.map.depots[self.dest]):
            return True
        return False


class Table:

    def __init__(self, map: Map, mode):

        # table[x1][y1][d][p][x2][y2]
        self.mode = mode
        self.map = map
        if(mode == 'Q'):
            self.table = [[[[[[[0 for a in range(6)]for k in range(len(self.map.depots))] for p in range(2)] for l in range(self.map.height)]
                            for m in range(self.map.width)] for i in range(self.map.height)] for j in range(self.map.width)]
        else:
            if(mode == 'VALUE'):
                val = 0
            elif(mode == 'POLICY'):
                val = 'N'

            self.table = [[[[[[val for k in range(len(self.map.depots))] for p in range(2)] for l in range(self.map.height)]
                            for m in range(self.map.width)] for i in range(self.map.height)] for j in range(self.map.width)]

    def getVal(self, s: State, a=None):
        p = 0
        if(s.picked):
            p = 1
        if(self.mode == 'Q'):
            return self.table[s.taxiPos[0]][s.taxiPos[1]][s.passengerPos[0]][s.passengerPos[1]][p][self.map.dtoi(s.dest)][a]
        return self.table[s.taxiPos[0]][s.taxiPos[1]][s.passengerPos[0]][s.passengerPos[1]][p][self.map.dtoi(s.dest)]

    def setVal(self, s: State, val, a=None):
        p = 0
        if(s.picked):
            p = 1
        if(self.mode == 'Q'):
            self.table[s.taxiPos[0]][s.taxiPos[1]][s.passengerPos[0]
                                                   ][s.passengerPos[1]][p][self.map.dtoi(s.dest)][a] = val
        else:
            self.table[s.taxiPos[0]][s.taxiPos[1]][s.passengerPos[0]
                                                   ][s.passengerPos[1]][p][self.map.dtoi(s.dest)] = val

    def QtoP(self):
        if(self.mode == 'Q'):
            P = Table(self.map, 'POLICY')

            actions = ['N', 'S', 'W', 'E', 'PICK', 'DROP']

            for p in range(2):
                for d in range(len(self.map.depots)):
                    if(p == 1):
                        for y in range(self.map.height-1, -1, -1):
                            for x in range(self.map.width):
                                val = self.table[x][y][x][y][p][d]
                                P.table[x][y][x][y][p][d] = actions[val.index(max(val))]

                    else:
    
                        for i in range(self.map.width):
                            for j in range(self.map.height):
                                for y in range(self.map.height-1, -1, -1):
                                    for x in range(self.map.width):
                                        val = self.table[x][y][i][j][p][d]
                                        P.table[x][y][i][j][p][d] = actions[val.index(max(val))]
            return P

    def printVal(self):

        actions = ['N', 'S', 'W', 'E', 'PICK', 'DROP']

        for p in range(2):
            for d in range(len(self.map.depots)):
                if(p == 1):
                    print('\nDEST: ', self.map.itod(d), 'Picked : ', p == 1)
                    for y in range(self.map.height-1, -1, -1):
                        for x in range(self.map.width):
                            val = self.table[x][y][x][y][p][d]
                            if(self.mode == 'Q'):
                                val = actions[val.index(max(val))]
                            elif(self.mode == 'VALUE'):
                                val = '{0:.2f}'.format(val)
                            print(val, end=', ')
                        print()

                else:

                    for i in range(self.map.width):
                        for j in range(self.map.height):
                            print('\nPassenger: ', (i, j), 'DEST: ',
                                  self.map.itod(d), 'Picked : ', p == 1)
                            for y in range(self.map.height-1, -1, -1):
                                for x in range(self.map.width):
                                    val = self.table[x][y][i][j][p][d]
                                    if(self.mode == 'Q'):
                                        val = actions[val.index(max(val))]
                                    elif(self.mode == 'VALUE'):
                                        val = '{0:.2f}'.format(val)
                                    print(val, end=', ')
                                print()


class MDP:
    def __init__(self, m: Map):
        self.map = m
        State.map = m

    # Trnsition function
    def T(self, s: State, a, s1: State):

        if(a == 'PICK' or a=='DROP'):
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

            if(s.taxiPos == s1.taxiPos):
                p = 0
                for i in direc:
                    s2 = State(direc[i],direc[i],True,s.dest)
                    if(not s.isValidTransition(s2)):
                        # print('lol',s.taxiPos,direc[i],i,a)
                        if(a == i):
                            p += 0.85
                        else:
                            p += 0.05
                return p
            else:

                for i in direc:
                    # print(i,s.taxiPos,'->',s1.taxiPos,direc[i],s.isValidTransition(s1),s1.taxiPos[0] == direc[i][0] and s1.taxiPos[1]==direc[i][1])
                    if(s1.taxiPos == direc[i] and s.isValidTransition(s1)):
                        if(a == i):
                            return 0.85
                        else:
                            return 0.05

        return 0

    def update(self,gamma,s,V):
        maxx = None
        for a in ['PICK', 'DROP', 'N', 'S', 'W', 'E']:

            neigh = s.getNeighbours(a)
            # print(a,len(neigh))
            if(len(neigh) > 0):
                curr = 0
                for s1 in neigh:
                    t = self.T(s, a, s1)
                    if(t > 0):
                        # print(s.taxiPos,s.passengerPos,s.picked,s.dest, a,'=>', s1.taxiPos,s1.passengerPos,s1.picked,s1.dest, s.R(a, s1),t, t*(s.R(a, s1) + gamma*V.getVal(s1)))
                        curr += t*(s.R(a, s1) + gamma*V.getVal(s1))
                # print('----CURR: ' ,curr)

                if(maxx == None or maxx[0] < curr):
                    maxx = [curr, a]
        return maxx

    def iterate(self,update):
        changed = False
        delta = 0
        for x1 in range(self.map.width):
            for y1 in range(self.map.height):
                for p in range(2):
                    for d in range(len(self.map.depots)):

                        picked = (p == 1)

                        if(picked):
                            s = State((x1, y1), (x1, y1),
                                        picked, self.map.itod(d))
                            delta = update(s, delta)
                            if(type(delta)==bool and delta):
                                changed = True
                        else:
                            for x2 in range(self.map.width):
                                for y2 in range(self.map.height):
                                    s = State((x1, y1), (x2, y2),
                                                picked, self.map.itod(d))
                                    delta = update(s, delta)
                                    if(type(delta)==bool and delta):
                                        changed = True

        return (delta,changed)

    # Performs value iteration
    # TODO: have to add max-norm using epsilon
    def valueIteration(self, e, gamma = 0.9):

        V = Table(self.map, 'VALUE')
        P = Table(self.map, 'POLICY')

        delta = 10
        i = 0

        def update(s, delta):

            maxx = self.update(gamma,s,V)

            # print(s.taxiPos,s.passengerPos,s.picked, s.dest, maxx,'\n')
            if(maxx != None):
                # print(V[x1][y1][x2][y2][p][d],maxx[0])
                change = abs(maxx[0] - V.getVal(s))
                V.setVal(s, maxx[0])
                P.setVal(s, maxx[1])
                delta = max(change, delta)
                # print('LOL',P[x1][y1][x2][y2][p][d])
            return delta

        # ---------------------------------------------------------------------------------------

        while delta >= (1-gamma)*e/gamma:

            delta = self.iterate(update)[0]
            i += 1
            # print('Iteration', i, delta, end='\r')

        # P.printVal()
        return P,i

    def policyIteration(self, e, gamma=0.9):
        V = Table(self.map, 'VALUE')
        P = Table(self.map, 'POLICY')

        delta = 10
        i = 0
        flag = True

        def update(s, delta):
            a = P.getVal(s)
            neigh = s.getNeighbours(a)
            # print(a,len(neigh))
            if(len(neigh) > 0):
                curr = 0
                for s1 in neigh:
                    t = self.T(s, a, s1)

                    if(t > 0):
                        # print(s.taxiPos,s.passengerPos,s.picked,s.dest, a,'=>', s1.taxiPos,s1.passengerPos,s1.picked,s1.dest, self.R(s, a, s1),t, t*(self.R(s, a, s1) + gamma*V[s1.taxiPos[0]][s1.taxiPos[1]][s1.passengerPos[0]][s1.passengerPos[1]][s1.picked][self.map.dtoi(s1.dest)]),V[s1.taxiPos[0]][s1.taxiPos[1]][s1.passengerPos[0]][s1.passengerPos[1]][s1.picked][self.map.dtoi(s1.dest)])
                        curr += t*(s.R(a, s1) + gamma*V.getVal(s1))
                change = abs(curr - V.getVal(s))
                V.setVal(s, curr)
                if(change > delta):
                    delta = change
            return delta

        def updateP(s,delta=0):
            boolV = False
            maxx = self.update(gamma,s,V)

            # print(s.taxiPos,s.passengerPos,s.picked, s.dest, maxx,'\n')
            if(maxx != None and maxx[1] != P.getVal(s)):
                P.setVal(s, maxx[1])
                boolV = True
            return boolV

        # ---------------------------------------------------------------------------------------

        while flag:

            # policy evaluation phase
            flag = False
            delta = 10
            while delta >= (1-gamma)*e/gamma:
                delta = self.iterate(update)[0]

            # policy improvement phase
            flag = self.iterate(updateP)[1]

            i += 1
            print('Iteration', i, end='\r')
        P.printVal()

    def policyIteration_l(self, gamma = 0.99):
        w = self.map.width
        h = self.map.height
        de = len(self.map.depots)
        V = Table(self.map, 'VALUE')
        P = Table(self.map, 'POLICY')
        changed = True
        i = 0

        def updateP(s,delta=0):
            boolV = False
            maxx = self.update(gamma,s,V)
            # print(s.taxiPos,s.passengerPos,s.picked, s.dest, maxx,'\n')
            if(maxx != None and maxx[1] != P.getVal(s)):
                P.setVal(s, maxx[1])
                boolV = True
            return boolV

        # ---------------------------------------------------------------------------------------
        while changed:

            matrix = []
            const = []
            changed = False

            for x1 in range(self.map.width):
                for y1 in range(self.map.height):
                    for d in range(len(self.map.depots)):
                        s = State((x1, y1), (x1, y1),
                                  True, self.map.itod(d))
                        a = P.getVal(s)
                        temp = [0 for i in range(w*h*w*h*de+w*h*de)]
                        neigh = s.getNeighbours(a)
                        temp[x1*h*de+y1*de+d] = 1
                        if (len(neigh) > 0):
                            r = 0
                            for s1 in neigh:
                                t = self.T(s, a, s1)
                                if (t != 0):
                                    l = 0
                                    if(s1.picked):
                                        l = 1
                                    r += t*s.R(a, s1)
                                    if (l == 1):
                                        temp[s1.taxiPos[0]*h*de+s1.taxiPos[1] *
                                             de+self.map.dtoi(s1.dest)] = -1*gamma*t
                                    else:
                                        temp[w*h*de+s1.taxiPos[0]*h*w*h*de+s1.taxiPos[1]*w*h*de+s1.passengerPos[0] *
                                             h*de+s1.passengerPos[1]*de+self.map.dtoi(s1.dest)] = -1*gamma*t
                            const.append(r)
                        else:
                            const.append(0)
                        matrix.append(temp)

            for x1 in range(self.map.width):
                for y1 in range(self.map.height):
                    for x2 in range(self.map.width):
                        for y2 in range(self.map.height):
                            for d in range(len(self.map.depots)):
                                s = State((x1, y1), (x2, y2),
                                          False, self.map.itod(d))
                                a = P.getVal(s)
                                temp = [0 for i in range(w*h*w*h*de+w*h*de)]
                                neigh = s.getNeighbours(a)
                                temp[w*h*de + x1*h*w*h*de+y1 *
                                     w*h*de+x2*h*de+y2*de+d] = 1
                                if (len(neigh) > 0):
                                    r = 0
                                    for s1 in neigh:
                                        t = self.T(s, a, s1)
                                        if (t != 0):
                                            l = 0
                                            if(s1.picked):
                                                l = 1
                                            r += t*s.R(a, s1)
                                            if (l == 1):
                                                temp[s1.taxiPos[0]*h*de+s1.taxiPos[1] *
                                                     de+self.map.dtoi(s1.dest)] = -1*gamma*t
                                            else:
                                                temp[w*h*de+s1.taxiPos[0]*h*w*h*de+s1.taxiPos[1]*w*h*de+s1.passengerPos[0] *
                                                     h*de+s1.passengerPos[1]*de+self.map.dtoi(s1.dest)] = -1*gamma*t
                                    const.append(r)
                                else:
                                    const.append(0)
                                matrix.append(temp)
            # print(matrix)
            ans = np.linalg.solve(np.array(matrix), np.array(const))
            for x1 in range(self.map.width):
                for y1 in range(self.map.height):
                    for d in range(len(self.map.depots)):
                        s = State((x1, y1), (x1, y1), True, self.map.itod(d))
                        V.setVal(s, ans[x1*h*de+y1*de+d])
            for x1 in range(self.map.width):
                for y1 in range(self.map.height):
                    for x2 in range(self.map.width):
                        for y2 in range(self.map.height):
                            for d in range(len(self.map.depots)):
                                s = State((x1, y1), (x2, y2),
                                          False, self.map.itod(d))
                                V.setVal(
                                    s, ans[w*h*de + x1*h*w*h*de+y1*w*h*de+x2*h*de+y2*de+d])

            changed = self.iterate(updateP)[1]
            i += 1
            print('Iteration', i, end='\r')
        P.printVal()


# Change this value for number of episodes in learning
n = 50000


class RL:

    def __init__(self, map: Map):
        self.map = map
        State.map = map

    # Generalised learning that can perform any learning specified in question (by changing parameters)
    def generalLearning(self, e, isE_Greedy, isQ, alpha=0.25, gamma=0.99, maxLen = None):

        Q = Table(self.map, 'Q')
        actions = ['N', 'S', 'W', 'E', 'PICK', 'DROP']

        # Some helper functions
        def getBest(s: State):
            j = 2
            for i in range(6):
                if(Q.getVal(s, i) > Q.getVal(s, j)):
                    j = i
            return j

        def getRandomState():
            x1 = random.randint(0, self.map.width-1)
            y1 = random.randint(0, self.map.height-1)
            d = self.map.itod(random.randint(1, len(self.map.depots))-1)
            p = random.randint(0, 1)

            if(p == 1):
                return State((x1, y1), (x1, y1), True, d)
            else:
                while True:
                    x2 = random.randint(0, self.map.width-1)
                    y2 = random.randint(0, self.map.height-1)
                    if((x2, y2) != self.map.depots[d]):
                        break

                return State((x1, y1), (x2, y2), False, d)

        def e_greedy(s, e, it=0):
            prob = random.uniform(0, 1)
            if(prob > e):
                return getBest(s)
            else:
                return random.randint(0, 5)

        def decay(s, e, it):
            prob = random.uniform(0, 1)
            # TODO: Can change this decay function
            if(prob > e/it):
                return getBest(s)
            else:
                return random.randint(0, 5)

        def QLearning(policy, it):
            s = getRandomState()
            while(not s.isTerminal()):
                a = policy(s, e, it)
                s1, r = s.getNext(actions[a])
                val = (1-alpha)*Q.getVal(s, a) + alpha * (r + gamma*Q.getVal(s1, getBest(s1)))
                Q.setVal(s, val, a)
                # print(s.taxiPos,s.passengerPos,s.picked,s.dest,'[Action: ',actions[a],']->',s1.taxiPos,s1.passengerPos,s1.picked,s1.dest,'[Reward',r,']')
                s = s1         

        def SARSA(policy, it):
            s = getRandomState()
            a = policy(s, e, it)
            while(not s.isTerminal()):
                s1, r = s.getNext(actions[a])
                a1 = policy(s1, e, it)
                val = (1-alpha)*Q.getVal(s, a) + alpha * (r + gamma*Q.getVal(s1, a1))
                Q.setVal(s, val, a)
                # print(s.taxiPos,s.passengerPos,s.picked,s.dest,'[Action: ',actions[a],']->',s1.taxiPos,s1.passengerPos,s1.picked,s1.dest,'[Reward',r,']')
                s = s1
                a = a1

    # ---------------------------------------------------------------------------------

        # Actual Computation

        if(isE_Greedy):
            policy = e_greedy
        else:
            policy = decay

        for _ in range(1, n+1):        
            if(isQ):
                QLearning(policy, _)
            else:
                SARSA(policy, _)

            print('Iteration', _, end='\r')

        print()
        return Q.QtoP()

#    Utilise thsese Q table as per output format

    def Qlearning_E(self, e, alpha=0.25, maxLen = None):
        return self.generalLearning(e, True, True, alpha, maxLen= maxLen)

    def Qlearning_D(self, e, alpha=0.25, maxLen = None):
        return self.generalLearning(e, False, True, alpha, maxLen= maxLen)

    def SARSA_E(self, e, alpha=0.25, maxLen = None):
        return self.generalLearning(e, True, False, alpha, maxLen= maxLen)

    def SARSA_D(self, e, alpha=0.25, maxLen = None):
        return self.generalLearning(e, False, False, alpha, maxLen= maxLen)


walls1 = {
    (0, 0): {(1, 0): True},
    (0, 1): {(1, 1): True},
    (1, 3): {(2, 3): True},
    (1, 4): {(2, 4): True},
    (2, 0): {(3, 0): True},
    (2, 1): {(3, 1): True}
}

depots1 = {
    'Y': (0, 0),
    'R': (0, 4),
    'B': (3, 0),
    'G': (4, 4)
}

walls2 = {
    (0, 0): {(1, 0): True},
    (0, 1): {(1, 1): True},
    (0, 2): {(1, 2): True},
    (0, 3): {(1, 3): True},

    (2, 6): {(3, 6): True},
    (2, 7): {(3, 7): True},
    (2, 8): {(3, 8): True},
    (2, 9): {(3, 9): True},

    (3, 0): {(4, 0): True},
    (3, 1): {(4, 1): True},
    (3, 2): {(4, 2): True},
    (3, 3): {(4, 3): True},

    (5, 4): {(6, 4): True},
    (5, 5): {(6, 5): True},
    (5, 6): {(6, 6): True},
    (5, 7): {(6, 7): True},

    (7, 0): {(8, 0): True},
    (7, 1): {(8, 1): True},
    (7, 2): {(8, 2): True},
    (7, 3): {(8, 3): True},

    (7, 6): {(8, 0): True},
    (7, 7): {(8, 0): True},
    (7, 8): {(8, 0): True},
    (7, 9): {(8, 0): True},
}

depots2 = {
    'Y': (0, 1),
    'R': (0, 9),
    'W': (3, 6),
    'B': (4, 0),
    'G': (5, 9),
    'M': (6, 5),
    'C': (8, 9),
    'P': (9, 0)
}


# Flow of program: Map created -> destination set -> MDP called -> Value iteration solves MDP -> calls T() and R() in between and makes State class instances
M1 = Map(5, 5, walls1, depots1)
M2 = Map(10, 10, walls2, depots2)

def quesA2a():
    mdp = MDP(M1)
    _,n = mdp.valueIteration(0.1,0.9)
    # V.printVal()
    print('\nEPSILON',0.1,'NO OF ITERATIONS:',n )

def quesA2b():
    mdp = MDP(M1)
    e = 0.1
    rng = [0.01, 0.1, 0.5, 0.8,0.99]
    x,y = [],[]
    for gamma in rng:
        _,n = mdp.valueIteration(e,gamma)
        print('\nGAMMA',gamma,'NO OF ITERATIONS:',n )
        y.append((1-gamma)*e/gamma)
        x.append(n)
    print(x,y)
    plt.figure(figsize=(10,5))
    plt.plot(x,y, "r", linewidth = 2, marker = 'o', markerfacecolor = "r", label = "Max-norm dist")
    plt.grid(True, color = "k")
    plt.title('No of iterations VS Max-norm dist')
    plt.ylabel('Max-norm dist')
    plt.xlabel('No of iterations')
    plt.savefig("QA2b.png")

    plt.show()

def quesA2C(M:Map,taxi,passenger,dest):
    s = State(M.depots[taxi],M.depots[passenger],False,dest)
    mdp = MDP(M)

    def perform(gamma,s):

        print('[Gamma =',gamma,']\n')
        print('EVALUATING(Value iteration)')
        P,_ = mdp.valueIteration(0.1,gamma)
        i = 0

        print('SIMULATING')
        while(i<20 and not s.isTerminal()):
            print('STATE: [',s.taxiPos,s.passengerPos,s.picked,s.dest, ']')
            a = P.getVal(s)
            print('ACTION: [',a,']\n')
            s1,r =  s.getNext(a)

            s = s1
            i += 1

        print('-----------------SIMUALTION ENDED ------------------\n\n')
    perform(0.1,s)
    perform(0.99,s)

def quesB2():
    global n
    rl = RL(M1)

    algos = {
    rl.Qlearning_E: 'QLearning_e-greedy',
    rl.Qlearning_D: 'QLearning_exploration-decay',
    rl.SARSA_E : 'SARSA_e-greedy',
    rl.SARSA_D: 'SARSA_exploration-decay'
    }

    for algo in algos:
        
        rewards = []
        episodes = []

        n = 0
        for i in range(10):

            print('[LEARNING',algos[algo],' with N = ',n,']')
            P = algo(0.1) 
            episodes.append(n)
            n += 3000

            avg = 0
            for ep in range(10):
                s = rl.getRandomState()
                reward = 0
                step = 0
                while(step < 500 and not s.isTerminal()):
                    s1,r = s.getNext(P.getVal(s))
                    reward += r*pow(0.99,step)
                    s = s1
                    step += 1
                avg += reward
            avg = avg/10
            rewards.append(avg)

        figure,plot = plt.subplots()
        plot.plot(episodes,rewards, "c", markerfacecolor = "c")
        plot.grid(True, color = "k")
        plot.set_title(algos[algo])
        plot.set_ylabel('Discounted Reward')
        plot.set_xlabel('No of episodes')
        figure.canvas.set_window_title(algos[algo])
        figure.savefig('QB2_' + algos[algo]+".png")
    plt.show()

# quesA2a()
# quesA2b()
# quesA2C(M1,'R','Y','G')
quesB2()

# mdp = MDP(M1)
# mdp = MDP(M2)
# mdp.valueIteration(0.1)
# mdp.policyIteration(0.1)
# mdp.policyIteration_l()

# rl = RL(M1)
# rl = RL(M2)
# rl.Qlearning_E(0.1)
# rl.Qlearning_D(0.1)
# a = rl.SARSA_E(0.1)
# a.printVal()
# rl.SARSA_D(0.1)
