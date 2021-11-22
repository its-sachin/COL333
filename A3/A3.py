class Map:
    def __init__(self, height, width, walls, depots):
        self.height = height
        self.width = width
        self.walls = walls
        self.depots = depots
        # self.picked = False

    def isWall(self, point1, point2):
        return not (self.walls[point1].get(point2) == None)

    # These functions required only id we need to print map at each step (game type)

    # def setPassenger(self,pos):
    #     self.passengerPos = pos

    # def setTaxi(self,pos):
    #     self.taxiPos = pos

    # def move(self,direction):
    #     if(direction == 'N'):
    #         self.taxiPos[1] += 1
    #     elif(direction == 'S'):
    #         self.taxiPos[1] -= 1
    #     elif(direction == 'E'):
    #         self.taxiPos[0] += 1
    #     elif(direction == 'W'):
    #         self.taxiPos[0] -= 1

    #     if(self.picked):
    #         self.passengerPos = self.taxiPos

    # def pick(self):
    #     self.picked = True

    # def drop(self):
    #     self.picked = False

class State:
    def __init__(self,taxiPos,passengerPos,picked):
        self.taxiPos = taxiPos
        self.passengerPos = passengerPos
        self.picked = picked

class MDP:
    def __init__(self,map:Map):
        self.map = map

    # Checks if state transition of s -> s1 is valid or not
    # TODO: Will have to think of more constraints if there is any
    def isValidTransition(self,s:State,s1:State):

        def boundCheck(pos):
            if(pos[0] >= self.map.height or pos[0] < 0 or pos[1] >= self.map.width or pos[1] < 0):
                return False
            return True

        def isValidState(self,s:State):
            if(s.picked and s.passengerPos != s.taxiPos):
                return False

            return boundCheck(s.taxiPos) and boundCheck(s.passengerPos)

        if(isValidState(s1)):
            if(((not s1.picked) and s.passengerPos != s1.passengerPos) or
                self.map.isWall(s.taxiPos,s1.taxiPos)):
                return False
            return True
        return False

    # Returns transition probability of s -> s1 if action a is done on s
    # domain of a = ['N','S','E','W','PICK','DROP']
    def T(self,s:State ,a ,s1:State):

        if(not self.isValidTransition(s,s1)):
            return 0

        if(a == 'PICK'):
            if((not s.picked) and s1.picked and s.taxiPos == s.passengerPos):
                return 1
            return 0
        elif(a == 'DROP'):
            if(s.picked and (not s1.picked) and s1.taxiPos == s1.passengerPos):
                return 1
            return 0

        elif(s.picked == s1.picked):

            direc = { 
                'N' : [1,1],
                'S' : [1,-1],
                'E' : [0,1],
                'W' : [0,-1],
            }

            if(s.taxiPos[direc[a][0]] + direc[a][1] == s1.taxiPos):
                return 0.85
            else:
                return 0.05

        return 0

    def R(self,s,a,s1):
        if(not self.isValidTransition(s,s1)):
            return 0

        reward = -1 
        return reward

    def valueIteration(self):
        pass

    def policyIteration(self):
        pass


class RL:
    def __init__(self,map:Map):
        self.map = map  


walls = {
    {(0,0):(0,1)}, 
    {{1,0}:(1,1)},
    {(3,1):(3,2)},
    {(4,1):(4,2)},
    {(0,2):(0,3)},
    {(1,2):(1,3)}
    }

depots = [
    (0,0),
    (4,0),
    (0,3),
    (4,4)
]

M1 = Map(5,5,walls,depots)
        

