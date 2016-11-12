import os
import networkx as nx
import matplotlib.pyplot as plt
import time

M_1 = 10
M_2 = 4

fname = input('File name?')
if len(fname)<1:
    fname = '28k.txt'
fhand = open(fname)
time1 = time.time()
sentences = []
tem = []
for line in fhand:
    line = line.strip('\n')
    sentence = line.split('。')
    tem = tem + sentence
for sentence in tem:
    if sentence == '':continue
    sentences.append(sentence)
word_set = {}
#word_set:{(word,sentence_num):times}
sentence_num = 0
for sentence in sentences:
    tem = os.popen('echo '+sentence+' | juman | knp -simple').readlines()
    for details in tem:
        if details.startswith('*') or details.startswith('#') or details.startswith('+'):continue
        knpresult = details.split()
        if '普通名詞' not in knpresult:continue
        for keys in knpresult:
            if not keys.startswith('"代表表記:'):continue
            name = keys.split(':')
            word = name[1]
            if word.endswith('v'):continue
            word_set[(word,sentence_num)] = word_set.get((word,sentence_num),0)+1
    sentence_num = sentence_num+1
time2 = time.time()
words = {}
#words:{word:times}
for word,times in word_set.items():
    words[word[0]] = words.get(word[0],0)+times
tem = []
for word,times in words.items():
    tem.append((times,word))
tem.sort(reverse = True)
m_1 = min(M_1,len(words))
tem = tem[:m_1]
HighFreq = []
for (times,word) in tem:
    HighFreq.append(word)
co_occurrence = {}
co_tem = {}
for word1,times1 in word_set.items():
    for word2,times2 in word_set.items():
        if word1[1] != word2[1]:continue
        if word1[0] == word2[0]:continue
        co = times1 * times2
        co_occurrence[(word1[0],word2[0])] = co_occurrence.get((word1[0],word2[0]),0)+co
for pairs,co in co_occurrence.items():
    if (pairs[1],pairs[0]) in co_tem:continue
    co_tem[pairs[0],pairs[1]] = co
co_set = {}
#co_set:{(word1,word2):co}
for word1 in HighFreq:
    for word2 in HighFreq:
        if (word1,word2) in co_tem:
            co_set[(word1,word2)] = co_tem[(word1,word2)]
tem = []
for pairs,co in co_set.items():
    tem.append((co,pairs))
tem.sort(reverse = True)
tem = tem[:m_1-1]
links = []
for (co,pairs) in tem:
    links.append(pairs)
foundations = {}
for word in HighFreq:
    if word not in foundations:
        foundations[word] = []
for (word1,word2) in links:
    foundations[word1].append(word2)
    foundations[word2].append(word1)
'''
foundations_short = {}
for word in foundations:
    if foundations[word] == []:continue
    foundations_short[word] = foundations[word]
'''
G = nx.Graph(foundations)
graphs = list(nx.connected_component_subgraphs(G))
g_s_set = {}
#g_s_set:{(graph_num,sentence_num):g_s}
for word,times in word_set.items():
    for i in range(len(graphs)):
        if word[0] not in graphs[i].nodes():continue
        g_s_set[(i,word[1])]=g_s_set.get((i,word[1]),0) + times
based_set = {}
#based_set:{(word,graph_num):based}
for i in range(len(graphs)):
    for word,times in word_set.items():
        if word[0] in graphs[i].nodes():
            g_minus_w = g_s_set[(i,word[1])] - times
        else:
            g_minus_w = times
        based = times * g_minus_w
        based_set[(word[0],i)] = based_set.get((word[0],i),0)+based
neighbors_set = {}
#neighbors_set:{graph_num:neighbors}
for i in range(len(graphs)):
    for word,times in word_set.items():
        if word[0] in graphs[i].nodes():
            g_minus_w = g_s_set[(i,word[1])] - times
        else:
            g_minus_w = times
        neighbors_set[i] = neighbors_set.get(i,0) + g_minus_w
key_set = {}
tem_set = {}
for word in word_set:
    for i in range(len(graphs)):
        based = based_set[(word[0],i)]
        neighbors = neighbors_set[i]
        tem = 1 - based/neighbors
        tem_set[word[0]] = tem_set.get(word[0],1) * tem
    key_set[word[0]] = 1 - tem
m_2 = min(M_2,len(words))
tem = []
for word,key in key_set.items():
    tem.append((key,word))
tem.sort(reverse = True)
tem = tem[:m_2]
HighKey = []
for (key,word) in tem:
    HighKey.append(word)
keygraph = foundations
for word in HighKey:
    if word not in keygraph:
        keygraph[word] = []
G = nx.Graph(keygraph)
graphs = list(nx.connected_component_subgraphs(G))
new_links = []
for word in HighKey:
    for i in range(len(graphs)):
        if word in graphs[i].nodes():
            mark = i
    for i in range(len(graphs)):
        tem = []
        if i == mark:continue
        for node in graphs[i].nodes():
            if (word,node) in co_occurrence:
                column = co_occurrence[(word,node)]
            tem.append((column,(word,node)))
        tem.sort(reverse = True)
        new_links.append(tem[0][1])
for (word1,word2) in new_links:
    keygraph[word1].append(word2)
    keygraph[word2].append(word1)
c_set = {}
#c_set:{(word1,word2):column}
for word1 in HighKey:
    for word2 in HighFreq:
        if (word1,word2) in co_occurrence:
            c_set[(word1,word2)] = co_occurrence[(word1,word2)]
tem_set = {}
for pairs,c in c_set.items():
     tem_set[pairs[0]] = tem_set.get(pairs[0],0)+c
     tem_set[pairs[1]] = tem_set.get(pairs[1],0)+c
tem = []
for pair,c in tem_set.items():
    tem.append((c,pair))
tem.sort(reverse = True)
tem = tem[:m_2]
keyword = []
for (c,word) in tem:
    keyword.append(word)
time3 = time.time()
print('Keywords:')
for word in keyword:
    print(word)
print('KNP run time: %f s' %(time2-time1))
print('keygraph run time: %f s' %(time3-time2))
G = nx.Graph(keygraph)
for (word1,word2) in links:
    G.edge[word1][word2]['weight'] = 1
for (word1,word2) in new_links:
    G.edge[word1][word2]['weight'] = 0.1
#nx.draw_networkx(G)
elarge=[(u,v) for (u,v,d) in G.edges(data=True) if d['weight'] >0.5]
esmall=[(u,v) for (u,v,d) in G.edges(data=True) if d['weight'] <=0.5]
pos=nx.spring_layout(G)
nx.draw_networkx_nodes(G,pos,node_size=700)
nx.draw_networkx_edges(G,pos,edgelist=elarge,width=6)
nx.draw_networkx_edges(G,pos,edgelist=esmall,width=6,alpha=0.5,edge_color='b',style='dashed')
nx.draw_networkx_labels(G,pos,font_size=20,font_family='sans-serif')
plt.axis('off')
plt.show()
