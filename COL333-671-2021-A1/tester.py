import subprocess
from matplotlib import pyplot as plt
import time


def test():

    avg = []
    maxx = []

    map = input('Map : ')

    l = open('test_cases/test_evaluation_fn/grade-agent.test','r+')
    lines = []
    actualines = []
    for i in l.readlines():
        actualines.append(i)
        if(len(i.split()) > 0 and i.split()[0] == 'layoutName:'):
            lines.append(i[:13] + map + '"\n')
        else:
            lines.append(i)

    l.close()
    l = open('test_cases/test_evaluation_fn/grade-agent.test','w+')
    for i in lines:
        l.write(i)
    l.close()


    for i in range(1,int(input("Times: "))+1):
        f = open("in.txt","w+")
        f.write(str(i))
        f.close()

        print('Running with k = ' , i)
        a = subprocess.Popen('python autograder.py -q test_evaluation_fn',shell = True,stdout=subprocess.PIPE)

        m = 0
        while True:
            line = a.stdout.readline()
            if not line:
                break
            line = line.rstrip().decode()
            print(line)

            if(len(line)> 0):
                splitted = line.split()
                if(splitted[0] == 'Average'):
                    avg.append(float(splitted[2]))
                elif(splitted[0] =='Pacman'):
                    m = max(m,float(splitted[4]))
        maxx.append(m)

    print('Average: ',avg)
    print('Maximum: ', maxx)


    l = open('test_cases/test_evaluation_fn/grade-agent.test','w+')
    for i in actualines:
        l.write(i)
    l.close()

    plt.plot(avg, "r", linewidth = 2, marker = 'o', markerfacecolor = "r", label = "Avg Score")
    plt.plot(maxx, "r", linewidth = 2, marker = 'o', markerfacecolor = "r", label = "Max Score")
    plt.grid(True, color = "k")
    plt.title('Score vs K for ghost Dist')
    plt.ylabel('Score')
    plt.xlabel('K value')
    plt.show()

def grade():

    # t = int(input('Times: '))
    t = 5
    maps = [
        'capsuleClassic','contestClassic','mediumClassic','minimaxClassic',
    'originalClassic','powerClassic','smallClassic','testClassic','trappedClassic']
    
    for m in maps: 
        print('\nRunning on : ' + m + '\n' )

        startTime = time.time()
        subprocess.run('python pacman.py -l ' + m + ' -p ExpectimaxAgent -a evalFn=better -q -n ' + str(t))
        endTime = time.time()

        print('\nTime Taken : ' + str(endTime-startTime) + '\n' )

def timetaken():
    cmd = input("Enter command: ")
    startTime = time.time()
    subprocess.run(cmd)
    endTime = time.time()

    print('\nTime Taken : ' + str(endTime-startTime) + '\n' )

# test()
grade()
# timetaken()
    