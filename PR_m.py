import json
from numpy import *
from fractions import Fraction

def ini_Pr(c):
    pr = zeros((c.shape[0], 1), dtype = float)
    for i in range(c.shape[0]):
        pr[i] = float(1) / c.shape[0]
    return pr

def PR(p, m, v):
    while ((v == p * dot(m, v) + (1 - p) * v).all() == False):
        v = p * dot(m, v) + (1 - p) * v
        #print(v, p * dot(m, v) + (1 - p) * v)
    return v

def pagerank(outlink):
    global index
    index = []
    graph = {}
    prob = {}
    net = {}
    
    for link in outlink:
        total = 0
        index.append(link)
        for out_link in outlink[link]:
            total += outlink[link][out_link]
        for out_link in outlink[link]:
            outlink[link][out_link] = outlink[link][out_link] / total
            
    count = len(index)
    markov = [[0] * count for i in range(count)]
    for link in index:
        for out_link in outlink[link]:
            markov[index.index(out_link)][index.index(link)] = outlink[link][out_link]
    markov_array = (array(markov))
    pr = ini_Pr(markov_array)
    p = 0.85
    res = PR(p, markov_array, pr).tolist()

    for i in range(count):
        prob[index[i]] = res[i][0] #res每一项都是数组？。。
    prob = sorted(prob.items(), key = lambda x: x[1], reverse = True)
    for i in range(1, 22):
        net[prob[i][0]] = prob[i][1]
    return net

if __name__ == "__main__":
    index = []
    f = open('aaa.txt', 'r')
    outlink = json.loads(f.read())
    print(pagerank(outlink))
    f.close()
