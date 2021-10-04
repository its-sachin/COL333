# multiAgents.py
# --------------
# Licensing Information:  You are free to use or extend these projects for
# educational purposes provided that (1) you do not distribute or publish
# solutions, (2) you retain this notice, and (3) you provide clear
# attribution to UC Berkeley, including a link to http://ai.berkeley.edu.
# 
# Attribution Information: The Pacman AI projects were developed at UC Berkeley.
# The core projects and autograders were primarily created by John DeNero
# (denero@cs.berkeley.edu) and Dan Klein (klein@cs.berkeley.edu).
# Student side autograding was added by Brad Miller, Nick Hay, and
# Pieter Abbeel (pabbeel@cs.berkeley.edu).


from util import manhattanDistance
from game import Directions
import random, util

from game import Agent

class ReflexAgent(Agent):
    """
    A reflex agent chooses an action at each choice point by examining
    its alternatives via a state evaluation function.

    The code below is provided as a guide.  You are welcome to change
    it in any way you see fit, so long as you don't touch our method
    headers.
    """


    def getAction(self, gameState):
        """
        You do not need to change this method, but you're welcome to.

        getAction chooses among the best options according to the evaluation function.

        Just like in the previous project, getAction takes a GameState and returns
        some Directions.X for some X in the set {NORTH, SOUTH, WEST, EAST, STOP}
        """
        # Collect legal moves and successor states
        legalMoves = gameState.getLegalActions()
        # print("legalMoves: ",legalMoves)

        # Choose one of the best actions
        scores = [self.evaluationFunction(gameState, action) for action in legalMoves]
        # print("scores: ",scores)
        bestScore = max(scores)
        # print("bestScore: ",bestScore)
        bestIndices = [index for index in range(len(scores)) if scores[index] == bestScore]        
        # print("bestIndices: ",bestIndices)
        chosenIndex = random.choice(bestIndices) # Pick randomly among the best

        if(legalMoves[chosenIndex] == 'Stop'):
            stopPred = -1
            for i in range(len(scores)):
                if(i!=chosenIndex and (stopPred==-1 or scores[stopPred] < scores[i])):
                    stopPred = i
            if(scores[stopPred]>0):
                chosenIndex = stopPred

        return legalMoves[chosenIndex]


    def evaluationFunction(self, currentGameState, action):
        """
        Design a better evaluation function here.

        The evaluation function takes in the current and proposed successor
        GameStates (pacman.py) and returns a number, where higher numbers are better.

        The code below extracts some useful information from the state, like the
        remaining food (newFood) and Pacman position after moving (newPos).
        newScaredTimes holds the number of moves that each ghost will remain
        scared because of Pacman having eaten a power pellet.

        Print out these variables to see what you're getting, then combine them
        to create a masterful evaluation function.
        """
        # Useful information you can extract from a GameState (pacman.py)
        successorGameState = currentGameState.generatePacmanSuccessor(action)
        # print("successorGameState:",type(successorGameState),'\n',successorGameState)
        newPos = successorGameState.getPacmanPosition()
        # print("newPos:",type(newPos),'\n',newPos)
        newFood = successorGameState.getFood()
        # print("newFood:",type(newFood),'\n',newFood)
        newGhostStates = successorGameState.getGhostStates()
        # print("newGhostStates:",type(newGhostStates),'\n',newGhostStates)

        newScaredTimes = [ghostState.scaredTimer for ghostState in newGhostStates]
        # print("newScaredTimes:",type(newScaredTimes),'\n',newScaredTimes,'\n')

        length = (newFood.width**2 + newFood.height**2)**0.5

        def linear(dist,maxScore):
            return maxScore - (maxScore * dist / length)

        def exponential(dist,maxScore,k):
            return maxScore -( maxScore * 2.71 ** (-1*dist * length / k))

        foodList = newFood.asList()
        score = successorGameState.getScore()
        
        dist = length
        for food in foodList:
            dist = min(((food[0]-newPos[0])**2 + (food[1]-newPos[1])**2)**0.5, dist)
        score += linear(dist,10)

        dist = length
        scaredDist = length
        for ghost in newGhostStates:
            ghostPos = ghost.getPosition()
            if(ghostPos!=newPos):
                curr = ((ghostPos[0]-newPos[0])**2 + (ghostPos[1]-newPos[1])**2)**0.5
                if(ghost.scaredTimer==0):
                    dist = min(curr,dist)
                else:
                    scaredDist = min(curr,scaredDist)

        score += exponential(dist,500,6)
        score += exponential(scaredDist,-200,6)

        return score

def scoreEvaluationFunction(currentGameState):
    """
    This default evaluation function just returns the score of the state.
    The score is the same one displayed in the Pacman GUI.

    This evaluation function is meant for use with adversarial search agents
    (not reflex agents).
    """
    return currentGameState.getScore()

class MultiAgentSearchAgent(Agent):
    """
    This class provides some common elements to all of your
    multi-agent searchers.  Any methods defined here will be available
    to the MinimaxPacmanAgent, AlphaBetaPacmanAgent & ExpectimaxPacmanAgent.

    You *do not* need to make any changes here, but you can if you want to
    add functionality to all your adversarial search agents.  Please do not
    remove anything, however.

    Note: this is an abstract class: one that should not be instantiated.  It's
    only partially specified, and designed to be extended.  Agent (game.py)
    is another abstract class.
    """

    def __init__(self, evalFn = 'scoreEvaluationFunction', depth = '2'):
        self.index = 0 # Pacman is always agent index 0
        self.evaluationFunction = util.lookup(evalFn, globals())
        self.depth = int(depth)

class MinimaxAgent(MultiAgentSearchAgent):
    """
    Your minimax agent (question 2)
    """

    def getAction(self, gameState):
        """
        Returns the minimax action from the current gameState using self.depth
        and self.evaluationFunction.

        Here are some method calls that might be useful when implementing minimax.

        gameState.getLegalActions(agentIndex):
        Returns a list of legal actions for an agent
        agentIndex=0 means Pacman, ghosts are >= 1

        gameState.generateSuccessor(agentIndex, action):
        Returns the successor game state after an agent takes an action

        gameState.getNumAgents():
        Returns the total number of agents in the game

        gameState.isWin():
        Returns whether or not the game state is a winning state

        gameState.isLose():
        Returns whether or not the game state is a losing state
        """
        "*** YOUR CODE HERE ***"
        
        def minrec(state,ghostID,depth):

            if(ghostID >= state.getNumAgents()):
                _,currScore = maxrec(state,depth+1)
                return currScore
            
            ghostActions = state.getLegalActions(ghostID)

            if(state.isWin() or state.isLose() or len(ghostActions)==0):
                return self.evaluationFunction(state)

            ans = None
            for index in range(len(ghostActions)):
                currState = state.generateSuccessor(ghostID,ghostActions[index])
                currScore = minrec(currState,ghostID+1,depth)
                if(ans==None or ans > currScore):
                    ans = currScore
            return ans

        def maxrec(state,depth):
            
            playerActions  = state.getLegalActions()

            if(depth == self.depth or state.isWin() or state.isLose() or len(playerActions)==0):
                return None,self.evaluationFunction(state)

            ans = None
            for index in range(len(playerActions)):
                currState = state.generateSuccessor(0,playerActions[index])
                currScore = minrec(currState,1,depth)
                if(ans==None or ans[1] < currScore):
                    ans = [index,currScore]
            return playerActions[ans[0]],ans[1]

        ans,_ = maxrec(gameState,0)
        return ans
            


class AlphaBetaAgent(MultiAgentSearchAgent):
    """
    Your minimax agent with alpha-beta pruning (question 3)
    """

    def getAction(self, gameState):
        """
        Returns the minimax action using self.depth and self.evaluationFunction
        """
        "*** YOUR CODE HERE ***"
        
        def minrec(state,ghostID,depth,alpha,beeta):
    
            if(ghostID >= state.getNumAgents()):
                _,currScore = maxrec(state,depth+1,alpha,beeta)
                return currScore
            
            ghostActions = state.getLegalActions(ghostID)

            if(state.isWin() or state.isLose() or len(ghostActions)==0):
                return self.evaluationFunction(state)

            ans = None
            for index in range(len(ghostActions)):
                currState = state.generateSuccessor(ghostID,ghostActions[index])
                currScore = minrec(currState,ghostID+1,depth,alpha,beeta)
                if(ans==None or ans > currScore):
                    ans = currScore
                if(ans<alpha): 
                    return ans
                beeta = min(beeta,ans)
            return ans

        def maxrec(state,depth,alpha,beeta):
            
            playerActions  = state.getLegalActions()

            if(depth == self.depth or state.isWin() or state.isLose() or len(playerActions)==0):
                return None,self.evaluationFunction(state)

            ans = None
            for index in range(len(playerActions)):
                currState = state.generateSuccessor(0,playerActions[index])
                currScore = minrec(currState,1,depth,alpha,beeta)
                if(ans==None or ans[1] < currScore):
                    ans = [index,currScore]
                if(ans[1]>beeta):
                    return playerActions[ans[0]],ans[1]
                alpha = max(alpha,ans[1])
            return playerActions[ans[0]],ans[1]

        ans,_ = maxrec(gameState,0,-10**10,10**10)
        return ans

class ExpectimaxAgent(MultiAgentSearchAgent):
    """
      Your expectimax agent (question 4)
    """
    def getAction(self, gameState):
        """
        Returns the expectimax action using self.depth and self.evaluationFunction

        All ghosts should be modeled as choosing uniformly at random from their
        legal moves.
        """
        "*** YOUR CODE HERE ***"
        
        def exprec(state,ghostID,depth):
    
            if(ghostID >= state.getNumAgents()):
                _,currScore = maxrec(state,depth+1)
                return currScore
            
            ghostActions = state.getLegalActions(ghostID)

            if(state.isWin() or state.isLose() or len(ghostActions)==0):
                return self.evaluationFunction(state)

            ans = 0
            for index in range(len(ghostActions)):
                currState = state.generateSuccessor(ghostID,ghostActions[index])
                currScore = exprec(currState,ghostID+1,depth)
                ans+=currScore
            return ans/len(ghostActions)

        def maxrec(state,depth):
            
            playerActions  = state.getLegalActions()

            if(depth == self.depth or state.isWin() or state.isLose() or len(playerActions)==0):
                return None,self.evaluationFunction(state)

            ans = None
            for index in range(len(playerActions)):
                currState = state.generateSuccessor(0,playerActions[index])
                currScore = exprec(currState,1,depth)
                if(ans==None or ans[1] < currScore):
                    ans = [index,currScore]
            return playerActions[ans[0]],ans[1]

        ans,_ = maxrec(gameState,0)
        return ans

class Score:

    def __init__(self,maxScore,maxMetric,constant=0):
        self.maxScore = maxScore
        self.maxMetric = maxMetric
        self.score = 0
        self.constant = constant
    
    def incScore(self,val,fun):

        self.score += fun(val,self.maxScore,self.maxMetric,self.constant)
      
def linear(score,maxScore,maxMetric,k=0):
        return maxScore - (maxScore * score / maxMetric)

def exponential(score,maxScore,maxMetric,k):
    return maxScore - (maxScore * 2.71 ** (-1*score * maxMetric / k))

def exponential2(score,maxScore,maxMetric,k):
    return (maxScore * 2.71 ** (-1*score * maxMetric / k))

def betterEvaluationFunction(currentGameState):
    """
    Your extreme ghost-hunting, pellet-nabbing, food-gobbling, unstoppable
    evaluation function (question 5).

    DESCRIPTION: <write something here so we know what you did>
    """
    "*** YOUR CODE HERE ***"

    playerPos = currentGameState.getPacmanPosition()
    foodGrid = currentGameState.getFood()
    ghostStates = currentGameState.getGhostStates()

    statescore = currentGameState.getScore()
    maxDist = util.manhattanDistance((0,0),(foodGrid.width,foodGrid.height))
    
    ghostDistScore = Score(100,maxDist,5)
    scaredDistScore = Score(100,maxDist)
    scaredCountScore = Score(100,len(ghostStates))
    scaredCount = 0

    for ghost in ghostStates:

        dist = util.manhattanDistance(playerPos,ghost.getPosition())

        # Ghosts are far away
        if(ghost.scaredTimer==0):
            ghostDistScore.incScore(dist,exponential)

        # Scared ghosts are near
        # --------might also add metric related to scared time here-------------
        else:
            scaredDistScore.incScore(dist,linear)
            scaredCount += 1

    # scared ghosts more
    scaredCountScore.incScore(len(ghostStates)-scaredCount,linear)

    try:
        ExpectimaxAgent.gotInitial
    except:
        
        layout = currentGameState.data.layout
        ExpectimaxAgent.initFood = layout.food.count()
        ExpectimaxAgent.initCapsules = len(layout.capsules)
        ExpectimaxAgent.gotInitial = True

    # less food
    coinCountScore = Score(100,ExpectimaxAgent.initFood,100)
    coinCountScore.incScore(currentGameState.getNumFood(),exponential2)


    # near capsules
    capsulePos = currentGameState.getCapsules()
    dist = maxDist
    for capsule in capsulePos:
        dist = min(dist,util.manhattanDistance(capsule,playerPos))

    capsuleDistScore = Score(100,maxDist)
    capsuleDistScore.incScore(dist,linear)

    # foods are near
    foodGrid = foodGrid.asList()
    dist = 0
    if(len(foodGrid)>0):
        for food in foodGrid:
            dist += util.manhattanDistance(playerPos,food)
        dist /= len(foodGrid)

    coinDistScore = Score(100,maxDist)
    coinDistScore.incScore(dist,linear)

    # less capsules
    powerCountScore = Score(100,ExpectimaxAgent.initCapsules)
    powerCountScore.incScore(len(capsulePos),linear)

    score = 0
    scoreWeight = [
        (currentGameState.getScore(),1.0,'actualScore'),
        (ghostDistScore.score,1.3,'ghostDistScore'),
        (powerCountScore.score,1.3,'powerCountScore'),
        (scaredDistScore.score,1.2,'scaredDistScore'),
        (scaredCountScore.score,1.0,'scaredCountScore'),
        (capsuleDistScore.score,0.5,'capsuleDistScore'),
        (coinCountScore.score,1.0,'coinCountScore'),
        (coinDistScore.score,1.0,'coinDistScore')
        ]

    # print(currentGameState)
    for scores in scoreWeight:
        # print(scores[2],scores[0])
        score += scores[1]*scores[0]
        # print(score)
    # print("final= " ,score,'\n')
    return score
    # return currentGameState.getScore()

# Abbreviation
better = betterEvaluationFunction
