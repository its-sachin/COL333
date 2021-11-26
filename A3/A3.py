from math import degrees, sqrt
import random
import numpy as np
from numpy.core.fromnumeric import shape
from matplotlib import pyplot as plt
from sys import argv

# A class for the functions related to the map such as walls has attributes of the map such as heidth weidth etc and useful fucntions


class Map:
    # initilise the map with the height width walls and depots
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

# A class containing all the functions uselful for the states and attributes for the state


class State:
    # the location of taxi and passenger and whether the pasenger is picked and destination depots form the inique features of the state
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
        # if terminal state then no niegbours
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
            neigh.append(
                State(self.taxiPos, self.passengerPos, self.picked, self.dest))

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
        if((not self.picked) and self.passengerPos == State.map.depots[self.dest]):
            return True
        return False

# A class for managing the table values more efficiently (used in value and policy iterations etc.)


class Table:

    # has map of the problem as an attribute and the mode , mode has 3 options Q(for Q learning) Value and Policy for value and policy iteration respectively
    def __init__(self, map: Map, mode):

        self.mode = mode
        self.map = map
        # intialising the table values for different cases
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

    # given the state and possibly action in case of q learning give the appropriate table value ie utlity of the state
    def getVal(self, s: State, a=None):
        p = 0
        if(s.picked):
            p = 1
        if(self.mode == 'Q'):
            return self.table[s.taxiPos[0]][s.taxiPos[1]][s.passengerPos[0]][s.passengerPos[1]][p][self.map.dtoi(s.dest)][a]
        return self.table[s.taxiPos[0]][s.taxiPos[1]][s.passengerPos[0]][s.passengerPos[1]][p][self.map.dtoi(s.dest)]

    # given the state and possibly action in case of q learning set the appropriate table value ie utlity of the state to val

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

    # given the table returns the sum of all the values (ie utility) for the table
    def summ(self):
        val = 0
        for i in range(self.map.width):
            for j in range(self.map.height):
                for k in range(self.map.width):
                    for l in range(self.map.height):
                        for m in range(2):
                            for n in range(len(self.map.depots)):
                                val += self.table[i][j][k][l][m][n]
        return val

    # Function to change get  the table of mode Policy from table of mode Q.
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
                                P.table[x][y][x][y][p][d] = actions[val.index(
                                    max(val))]

                    else:

                        for i in range(self.map.width):
                            for j in range(self.map.height):
                                for y in range(self.map.height-1, -1, -1):
                                    for x in range(self.map.width):
                                        val = self.table[x][y][i][j][p][d]
                                        P.table[x][y][i][j][p][d] = actions[val.index(
                                            max(val))]
        return P

    # Function to print the values of the table in a correct format
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

# Class implementing the MDP formulation of the taxi domain problem has all the implemetation of the value iteration and policyiteration etc.


class MDP:
    # just has the mapmof mdp as an attribute
    def __init__(self, m: Map):
        self.map = m
        State.map = m

    # Trnsition function of the MDP
    def T(self, s: State, a, s1: State):

        if(a == 'PICK' or a == 'DROP'):
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
                    s2 = State(direc[i], direc[i], True, s.dest)
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

    # helper function which gives the bellaman ford update of the iteration and returns the new uility and policy
    def update(self, gamma, s, V):
        maxx = None
        for a in ['PICK', 'DROP', 'N', 'S', 'W', 'E']:
            neigh = s.getNeighbours(a)
            if(len(neigh) > 0):
                curr = 0
                for s1 in neigh:
                    t = self.T(s, a, s1)
                    if(t > 0):
                        curr += t*(s.R(a, s1) + gamma*V.getVal(s1))
                if(maxx == None or maxx[0] < curr):
                    maxx = [curr, a]
        return maxx

    # helper function which iterates over all of the table and updates the value according to the the update function taken as input
    def iterate(self, update):
        changed = False
        delta = 0
        # iterate over all the state space and then update
        for x1 in range(self.map.width):
            for y1 in range(self.map.height):
                for p in range(2):
                    for d in range(len(self.map.depots)):

                        picked = (p == 1)
                        # if picked then the taxi pos and the passenger pos is the same
                        if(picked):
                            s = State((x1, y1), (x1, y1),
                                      picked, self.map.itod(d))
                            delta = update(s, delta)
                            if(type(delta) == bool and delta):
                                changed = True
                        else:
                            for x2 in range(self.map.width):
                                for y2 in range(self.map.height):
                                    s = State((x1, y1), (x2, y2),
                                              picked, self.map.itod(d))
                                    delta = update(s, delta)
                                    if(type(delta) == bool and delta):
                                        changed = True

        return (delta, changed)

    # Performs value iteration
    # TODO: have to add max-norm using epsilon
    def valueIteration(self, e, gamma=0.9):

        V = Table(self.map, 'VALUE')
        P = Table(self.map, 'POLICY')

        delta = 10
        i = 0

        def update(s, delta):

            maxx = self.update(gamma, s, V)

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
        return P, i

    def policyIteration(self, e, gamma=0.9):
        V = Table(self.map, 'VALUE')
        P = Table(self.map, 'POLICY')
        global policyE

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

        def updateP(s, delta=0):
            boolV = False
            maxx = self.update(gamma, s, V)

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
            policyE.append(V.summ())
            # policy improvement phase
            flag = self.iterate(updateP)[1]

            i += 1
            print('Iteration', i, end='\r')
        # P.printVal()

    def policyIteration_l(self, gamma=0.99):
        w = self.map.width
        h = self.map.height
        de = len(self.map.depots)
        V = Table(self.map, 'VALUE')
        P = Table(self.map, 'POLICY')
        changed = True
        i = 0

        def updateP(s, delta=0):
            boolV = False
            maxx = self.update(gamma, s, V)
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

    def getRandomState(self, dest=None):
        x1 = random.randint(0, self.map.width-1)
        y1 = random.randint(0, self.map.height-1)
        d = dest
        if(dest == None):
            d = self.map.itod(random.randint(1, len(self.map.depots))-1)
        p = d
        while p == d:
            p = self.map.itod(random.randint(1, len(self.map.depots))-1)
        return State((x1, y1), self.map.depots[p], False, d)

    # Generalised learning that can perform any learning specified in question (by changing parameters)
    def generalLearning(self, e, isE_Greedy, isQ, alpha=0.25, gamma=0.99, dest=None):

        Q = Table(self.map, 'Q')
        actions = ['N', 'S', 'W', 'E', 'PICK', 'DROP']

        # Some helper functions
        def getBest(s: State):
            j = 2
            for i in range(6):
                if(Q.getVal(s, i) > Q.getVal(s, j)):
                    j = i
            return j

        def e_greedy(s, e, it=0):
            prob = random.uniform(0, 1)
            if(prob > e):
                return getBest(s)
            else:
                return random.randint(0, 5)

        def decay(s, e, it):
            prob = random.uniform(0, 1)
            # TODO: Can change this decay function
            if(prob > e/sqrt(it)):
                return getBest(s)
            else:
                return random.randint(0, 5)

        def QLearning(policy, it):
            s = self.getRandomState(dest)
            while(not s.isTerminal()):
                a = policy(s, e, it)
                s1, r = s.getNext(actions[a])
                val = (1-alpha)*Q.getVal(s, a) + alpha * \
                    (r + gamma*Q.getVal(s1, getBest(s1)))
                Q.setVal(s, val, a)
                # print(s.taxiPos,s.passengerPos,s.picked,s.dest,'[Action: ',actions[a],']->',s1.taxiPos,s1.passengerPos,s1.picked,s1.dest,'[Reward',r,']')
                s = s1

        def SARSA(policy, it):
            s = self.getRandomState(dest)
            a = policy(s, e, it)
            while(not s.isTerminal()):
                s1, r = s.getNext(actions[a])
                a1 = policy(s1, e, it)
                val = (1-alpha)*Q.getVal(s, a) + alpha * \
                    (r + gamma*Q.getVal(s1, a1))
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

        # print()
        return Q.QtoP()

#    Utilise thsese Q table as per output format

    def Qlearning_E(self, e, alpha=0.25, dest=None):
        return self.generalLearning(e, True, True, alpha, dest=dest)

    def Qlearning_D(self, e, alpha=0.25, dest=None):
        return self.generalLearning(e, False, True, alpha, dest=dest)

    def SARSA_E(self, e, alpha=0.25, dest=None):
        return self.generalLearning(e, True, False, alpha, dest=dest)

    def SARSA_D(self, e, alpha=0.25, dest=None):
        return self.generalLearning(e, False, False, alpha, dest=dest)


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


def randomStartState(m: Map, dest=None):
    t = m.itod(random.randint(1, len(m.depots))-1)
    d = dest
    if(dest == None):
        d = m.itod(random.randint(1, len(m.depots))-1)
    p = d
    while p == d:
        p = m.itod(random.randint(1, len(m.depots))-1)
    return State(m.depots[t], m.depots[p], False, d)


def quesA1b(t, p, d):

    print('\n\n-----------RUNNING QUES A.1.b--------------\n\n')
    s = State(M1.depots[t], M1.depots[p], False, d)
    State.map = M1
    actions = ['PICK', 'DROP', 'N', 'S', 'W', 'E']

    while True:

        print('STATE: ', s.taxiPos, s.passengerPos, s.picked, s.dest)
        a = input('\nACTION: ')
        if(a not in actions):
            if(a == 'STOP'):
                break
            print('INVALID ACTION')
        else:
            s1, r = s.getNext(a)
            print('REWARD: ', r)
        s = s1


def quesA2a():

    print('\n\n-----------RUNNING QUES A.2.a--------------\n\n')

    mdp = MDP(M1)
    _, n = mdp.valueIteration(0.1, 0.9)
    # V.printVal()
    print('\nEPSILON', 0.1, 'NO OF ITERATIONS:', n)


def quesA2b():

    print('\n\n-----------RUNNING QUES A.2.b--------------\n\n')

    mdp = MDP(M1)
    e = 0.1
    rng = [0.01, 0.1, 0.5, 0.8, 0.99]
    x, y = [], []
    for gamma in rng:
        V, n = mdp.valueIteration(e, gamma)
        print('\nGAMMA', gamma, 'NO OF ITERATIONS:', n)
        y.append((1-gamma)*e/gamma)
        x.append(n)
    print(x, y)
    plt.plot(x, y, "r", linewidth=2, marker='o',
             markerfacecolor="r", label="Max-norm dist")
    plt.grid(True, color="k")
    plt.title('Max-norm dist VS No of iterations ')
    plt.ylabel('Max-norm dist')
    plt.xlabel('No of iterations')
    plt.savefig("QA2b.png")

    plt.show()


def quesA2C(M: Map, taxi, passenger, dest):

    print('\n\n-----------RUNNING QUES A.2.c--------------\n\n')

    s = State(M.depots[taxi], M.depots[passenger], False, dest)
    mdp = MDP(M)

    def perform(gamma, s):

        print('[Gamma =', gamma, ']\n')
        print('EVALUATING(Value iteration)')
        P, _ = mdp.valueIteration(0.1, gamma)
        i = 0

        print('SIMULATING')
        while(i < 20 and not s.isTerminal()):
            print('STATE: [', s.taxiPos, s.passengerPos, s.picked, s.dest, ']')
            a = P.getVal(s)
            print('ACTION: [', a, ']\n')
            s1, r = s.getNext(a)

            s = s1
            i += 1

        print('-----------------SIMUALTION ENDED ------------------\n\n')
    perform(0.1, s)
    perform(0.99, s)


policyE = []


def quesA3b():

    print('\n\n-----------RUNNING QUES A.3.b--------------\n\n')

    global policyE
    mdp = MDP(M1)
    e = 0.1
    rng = [0.01, 0.1, 0.5, 0.8, 0.99]
    col = ['r', 'b', 'g', 'c', 'y']
    for i in range(len(rng)):
        policyE = []
        mdp.policyIteration(e, rng[i])
        m = policyE[-1]-policyE[0]
        if m == 0:
            policyE = [0 for i in range(len(policyE))]
        else:
            policyE = [abs((policyE[-1]-policyE[i])/m)
                       for i in range(len(policyE))]
        x = [i for i in range(len(policyE))]
        plt.plot(x, policyE, col[i], linewidth=2, marker='o',
                 markerfacecolor=col[i], label="Policy Loss")
        plt.grid(True, color="k")
    plt.title('Policy Loss VS No of iterations ')
    plt.ylabel('Policy Loss')
    plt.xlabel('No of iterations')
    plt.legend(rng, loc="lower right")
    plt.show()


# ------------------------------------------------------------------------
def quesB2():

    print('\n\n-----------RUNNING QUES B.2--------------\n\n')
    global n
    rl = RL(M1)

    algos = {
        rl.Qlearning_E: 'QLearning_e-greedy',
        rl.Qlearning_D: 'QLearning_exploration-decay',
        rl.SARSA_E: 'SARSA_e-greedy',
        rl.SARSA_D: 'SARSA_exploration-decay'
    }

    for algo in algos:

        rewards = []
        episodes = []

        n = 0
        for i in range(10):

            print('[LEARNING', algos[algo], ' with N = ', n, ']')
            P = algo(0.1)
            episodes.append(n)
            n += 500

            avg = 0
            for ep in range(100):
                s = rl.getRandomState()
                reward = 0
                step = 0
                while(step < 500 and not s.isTerminal()):
                    s1, r = s.getNext(P.getVal(s))
                    reward += r*pow(0.99, step)
                    s = s1
                    step += 1
                avg += reward
            avg = avg/100
            rewards.append(avg)

        figure, plot = plt.subplots()
        plot.plot(episodes, rewards, "c", markerfacecolor="c")
        plot.grid(True, color="k")
        plot.set_title(algos[algo])
        plot.set_ylabel('Discounted Reward')
        plot.set_xlabel('No of episodes')
        figure.canvas.set_window_title(algos[algo])
        # figure.savefig('QB2_' + algos[algo]+".png")
        print()
    plt.show()


def quesB3():

    print('\n\n-----------RUNNING QUES B.3--------------\n\n')

    global n

    n = 5000
    rl = RL(M1)
    P = rl.Qlearning_D(0.1)

    def perform(s):
        step = 0
        while(step < 500 and not s.isTerminal()):
            print('STATE: [', s.taxiPos, s.passengerPos, s.picked, s.dest, ']')
            a = P.getVal(s)
            print('ACTION: [', a, ']\n')
            s1, r = s.getNext(a)
            s = s1
            step += 1

        print('-----------------SIMUALTION ENDED ------------------\n\n')

    for i in range(5):
        s = randomStartState(M1)
        print('RUNNING ON INSTANCE', i+1)
        perform(s)


def quesB4():

    print('\n\n-----------RUNNING QUES B.4--------------\n\n')

    global n
    rl = RL(M1)

    colour = ['b', 'g', 'r', 'c', 'm']
    # (e,alpha)
    values = {
        'alpha=0.1 varying e': [(0, 0.1), (0.05, 0.1), (0.1, 0.1), (0.5, 0.1), (0.9, 0.1)],
        'e=0.1 varying alpha': [(0.1, 0.1), (0.1, 0.2), (0.1, 0.3), (0.1, 0.4), (0.1, 0.5)]
    }

    for part in values:

        figure, plot = plt.subplots()
        plot.grid(True, color="k")
        plot.set_ylabel('Discounted Reward')
        plot.set_xlabel('No of episodes')

        plot.set_title(part)
        figure.canvas.set_window_title(part)

        for trial in range(5):

            e = values[part][trial][0]
            alpha = values[part][trial][1]
            print('\n\nEpsilon = ', e, 'Alpha = ', alpha, '\n')

            rewards = []
            episodes = []

            n = 0
            for i in range(10):

                print('[LEARNING with N = ', n, ']')
                P = rl.Qlearning_E(e=e, alpha=alpha)
                episodes.append(n)
                n += 500

                avg = 0
                for ep in range(100):
                    s = rl.getRandomState()
                    reward = 0
                    step = 0
                    while(step < 500 and not s.isTerminal()):
                        s1, r = s.getNext(P.getVal(s))
                        reward += r*pow(0.99, step)
                        s = s1
                        step += 1
                    avg += reward
                avg = avg/100
                rewards.append(avg)

            plot.plot(episodes, rewards, colour[trial], markerfacecolor="c",
                      label='e = ' + str(e) + ', a = ' + str(alpha))
            plot.legend(loc="lower right")
        # figure.savefig('QB4_' +part[0:part.index('1')+1]+".png")
    plt.show()


def quesB5():
    global n

    n = 10000

    rl = RL(M2)

    def perform(s):
        step = 0
        reward = 0
        while(step < 500 and not s.isTerminal()):
            s1, r = s.getNext(Ps[d].getVal(s))
            reward += r*pow(0.99, step)
            s = s1
            step += 1
        return reward

    Ps = []
    for d in range(len(M2.depots)):
<<<<<<< HEAD
        Ps.append(rl.Qlearning_D(0.2, dest=M2.itod(d)))
=======
        Ps.append(rl.Qlearning_D(0.1,dest=M2.itod(d)))
>>>>>>> 2470606c6cd876ebd5a7a883ae0debe326e1771f
        print()

    avg = 0
    num = 500

    rr = []
    for i in range(num):
        d = random.randint(0, len(M2.depots)-1)
        s = randomStartState(M2, M2.itod(d))

        reward = perform(s)
        avg += reward
        rr.append(reward)

    print('\n\nAVERAGE DISCOUNTED REWARD: ', avg/num)

    figure, plot = plt.subplots()
    plot.plot(rr, label='(x,y)')
    plt.show()


<<<<<<< HEAD
if(len(argv) == 1):
=======
if(len(argv)==1):
    quesA1b('R','Y','G')
>>>>>>> 2470606c6cd876ebd5a7a883ae0debe326e1771f
    quesA2a()
    quesA2b()
    quesA2C(M1, 'R', 'Y', 'G')
    quesA3b()
    quesB2()
    quesB3()
    quesB4()
    quesB5()

else:
    ques = argv[1]
    if(ques == 'A'):
        spart = int(argv[2])
        if(spart == 1):
            quesA1b('R', 'Y', 'G')
        if(spart == 2):
            sspart = argv[3]
            if(sspart == 'a'):
                quesA2a()
            elif(sspart == 'b'):
                quesA2b()
            else:
                quesA2C(M1, 'R', 'Y', 'G')
        else:
            quesA3b()

    else:
        spart = int(argv[2])
        if(spart == 2):
            quesB2()
        elif(spart == 3):
            quesB3()
        elif(spart == 4):
            quesB4()
        else:
            quesB5()
