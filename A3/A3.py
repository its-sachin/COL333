class Map:
    def __init__(self, height, width, walls, depots):
        self.height = height
        self.width = width
        self.walls = walls
        self.depots = depots
        self.picked = False

    def isWall(self, point1, point2):
        return not (self.walls[point1].get(point2) == None)

    # These functions required only id we need to print map at each step (game type)
    
    def setPassenger(self,pos):
        self.passengerPos = pos

    def setTaxi(self,pos):
        self.taxiPos = pos

    def move(self,direction):
        if(direction == 'N'):
            self.taxiPos[1] += 1
        elif(direction == 'S'):
            self.taxiPos[1] -= 1
        elif(direction == 'E'):
            self.taxiPos[0] += 1
        elif(direction == 'W'):
            self.taxiPos[0] -= 1

        if(self.picked):
            self.passengerPos = self.taxiPos

    def pick(self):
        self.picked = True

    def drop(self):
        self.picked = False

class State:
    def __init__(self,pos,picked):
        self.pos = pos
        self.picked = picked

class MDP:
    def __init__(self,map:Map):
        self.map = map
    
    def T(self,s,a,s1):
        pass

    def R(self,s,a,s1):
        pass

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
        

