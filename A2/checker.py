import subprocess

ques = open("ques1_t1.txt",'r+')
ques.readline()
myans = []

i=1
for line in ques.readlines():
    N,D,m,a,e = line.strip().split(',')
    with open("test.txt" , 'w') as file:
        file.write('N,D,m,a,e\n' + str(N) + ',' + str(D) + ',' + str(m) + ',' + str(a) + ',' + str(e))
    print('EVALUATING line',i,end='\r')
    out = subprocess.check_output(["python", "A2.py", "test.txt" ]).decode('utf-8').strip()
    file.close()
    myans.append(out)
    i+=1
ques.close()
ans = open("ques1_t1_ans.txt", "r+").readlines()
for i in range(len(ans)):
    print(i,'\r')
    if(ans[i].strip()!=myans[i].strip()):
        print('\nUNMATCHED AT',i)
        exit()
print('\nMATCHED')