import pandas as pd
import numpy as np
import itertools
import heapq

####  File Parsers ####

# parses state file
def parseStateFile(file):
    file = open(file)
    lines = [line.strip().split() for line in file]
    col_count = int(lines[0][0])
    cols = [lines[i][0] for i in range(1, col_count+1)]
    data = np.ones((col_count, col_count))
    data[:, cols.index('BEGIN')] = 0
    data[cols.index('END')] = 0
    for i in range(col_count+1, len(lines)):
        x,y,score = lines[i]
        data[int(x)][int(y)] = int(score) + 1
    for i in range(len(data)):
        total = sum(data[i])
        data[i] = list(map(lambda x:x/total if x!=0 else 0, data[i]))
    with np.errstate(divide='ignore'):
        return cols, np.log(data)

# parses symbol file
def parseSymbolFile(file,N):
    file = open(file)
    lines = [line.strip().split() for line in file]
    col_count = int(lines[0][0])
    cols = [lines[i][0] for i in range(1, col_count+1)]+['UNK']
    out = np.ones((N,col_count+1))
    for row in lines[(col_count+1):]:
        out[int(row[0]),int(row[1])] = int(row[2])+1
    for index in range(out.shape[0]):
        total = sum(out[index])
        prob = lambda t: t/(total)
        func = np.vectorize(prob)
        out[index]  = func(out[index])
    with np.errstate(divide='ignore'):
        return cols, np.log(out)

def parseQueryFile(file):
    file = open(file)
    return [parseAddress(line.strip()) for line in file]
    



####  Helpers ####

# helper to check if matrix contains value other returns unknown probabilities
def findVect(matrix,symbls, value):
    try: 
        return matrix[:,symbls.index(value)]
    except ValueError:
        return matrix[:,symbls.index('UNK')]

def findVect2(matrix,symbls, value):
    try: 
        return matrix[np.newaxis, :,symbls.index(value)]
    except ValueError:
        return matrix[np.newaxis, :,symbls.index('UNK')]

def findValue(matrix,symbls, x, y):
    try: 
        return matrix[x,symbls.index(y)]
    except ValueError:
        return matrix[x,symbls.index('UNK')]


#helper to find address
def parseAddress(string):
    out = []
    running = ''
    for ch in string:
        if ch in [',','(',')','/','&','-','&', ' ']:
            if running:
                out.append(running)
                running=''
            if ch != ' ':
                out.append(ch)
        else:
            running += ch
    if running:
        out.append(running)
    out.append('END')
    return out



# Question 1
def viterbi_algorithm(State_File, Symbol_File, Query_File): # do not change the heading of the function
    state_cols, state_matrix = parseStateFile(State_File)
    symbol_cols, symbol_matrix = parseSymbolFile(Symbol_File,len(state_cols))
    queries = parseQueryFile(Query_File)
    out = []
    for query in queries:
        N = len(state_cols)
        Q = len(query)
        logprobs    = np.empty((N,Q), 'd')
        paths       = np.empty((N,Q), 'B')
        # special case for begin
        logprobs[:, 0] = state_matrix[state_cols.index("BEGIN")] +  findVect(symbol_matrix,symbol_cols,query[0])
        paths[:, 0] = state_cols.index("BEGIN")
        # normal cases
        for i in range(1, Q):
            logprobs[:, i] = np.max(logprobs[:, i - 1] + state_matrix.T + findVect2(symbol_matrix,symbol_cols,query[i]).T, 1)
            paths[:, i] = np.argmax(logprobs[:, i - 1] + state_matrix.T, 1)
        # case for end
        logprobs[:,Q-1] = np.max(logprobs[:, Q-2] + state_matrix.T)
        # build path
        path = [0 for _ in range(Q)]
        path[-1] = state_cols.index("END")
        for i in reversed(range(1, Q)):
            path[i - 1] = paths[path[i], i]
        path = [state_cols.index("BEGIN")] + path + [np.max(logprobs[:,Q-1])]
        out.append(path)
    return out

# Question 2
def top_k_viterbi(State_File, Symbol_File, Query_File, k): # do not change the heading of the function
    state_cols, state_matrix = parseStateFile(State_File)
    symbol_cols, symbol_matrix = parseSymbolFile(Symbol_File,len(state_cols))
    queries = parseQueryFile(Query_File)
    print(state_matrix)
    for query in queries[0:1]:
        N = len(state_cols)
        Q = len(query)
        logprobs    = np.empty((N,Q,k), 'd')
        paths       = np.empty((N,Q,k), 'B')
        #CHANGE VECTOR FUNCTION
        logprobs[:,0,0] = state_matrix[state_cols.index("BEGIN")] + findVect(symbol_matrix,symbol_cols,query[0])
        for i in range(1,k):
            logprobs[:,0,i] = 0
        paths[:, 0] = state_cols.index("BEGIN")
        for q in range(1, Q):
            for x in range(N):
                queue = []                
                for y in range(N):
                    #  in itertools.product( range(N-1),range(N)):  #range(1), range(1) ): 
                    # print(logprobs[x,q-1,1])

                    for i in range(k):
                        # print("logprob",logprobs[x,q-1,i])
                        # print("state",state_matrix[x,y].T)
                        # print("find",findVect2(symbol_matrix,symbol_cols,query[i]).T)
                        prob = logprobs[x,q-1,i] + state_matrix[x,y].T + findVect2(symbol_matrix,symbol_cols,query[q]).T
                        # print("prob",prob)
                        for s in range(len(prob)):
                            queue.append((prob[s],s))
                
                queue.sort(key=lambda x: x[0], reverse=True)                
                # for i in range(len(queue)):
                #     if np.isinf(queue[i][0]):
                #         queue[i][0][0] = -10000
                # queue.sort(key=lambda x: x[0], reverse=True)          
                        # print(i[0])
                # print(queue)
                # print(queue)
                print(queue[:k])
                for i in range(k):
                    logprobs[x,q,i] = queue[i][0]
                    paths[x,q,i]    = queue[i][1]
                
        print(logprobs[:,:,0])
        print(logprobs[:,:,1])
        print(paths[:,:,0])
        print(paths[:,:,1])

                
                        # heapq.heappush(queue, (prob[s],s)
                        # queue.heappush
                # print(queue)
                
                
                # for t in range(k):
                #     prob
                # print(x,y)
                # for y in range(N):
                # for t in range(k):
                # probs = 
        


    pass # Replace this line with your implementation...


# Question 3 + Bonus
def advanced_decoding(State_File, Symbol_File, Query_File): # do not change the heading of the function
    pass # Replace this line with your implementation...



if __name__=="__main__":
    # pass
    # print(parseAddress('P.O Box 6196, St.Kilda Rd Central, Melbourne, VIC 3001'))
    top_k_viterbi('./dev_set/State_File','./dev_set/Symbol_File','./dev_set/Query_File',2)
    # out = viterbi_algorithm('./dev_set/State_File','./dev_set/Symbol_File','./dev_set/Query_File')
    # '''
    # Unsure of where issues are arising, possibly around dealing with beg / end cases
    # current method:
    # Create transition from states
    #     N.N matrix
    #     End has 0 probability away from it
    #     Begin has 0 probability to it
    #     rest are calculated as ones and value overwritten if in state file (+1)
    #     then probabilities calculated from this
    # create emission from symbols
    #     N.K matrix
    #     all initalised to zeros with column added for unknown
    #     values overwritten from symbol file (+1) 
    #     calculated probabilites
    # 1. find initial probabilities from the transition matrix (BEGIN state)
    #     please confirm?
    # 2. iterate through each observation in y 
    #     most of logic is here
    #     first line T1[:, i - 1] * state_matrix.T * findVect(symbol_matrix,symbol_cols,y[i]).T
    #         times last states * prob next state given state * emission prob of observed
    #         find max of this for each state // prob of that state
    #         to matrix running probabilities
    #     T2 -> this displays index of path. 
    #         similar
    #         last states probs * next states -> array of N by N, then for each N find max prob index.
    # 3. first find argmax of last state 
