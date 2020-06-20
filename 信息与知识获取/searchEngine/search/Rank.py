import cmath
import math
from .helper import *
def getSortedDoc(index,nfiles,words,docList,PHRASEDOCLIST,VSM):
    scoreDocList = []
    for doc in docList:
        score = getVSMScore(index,nfiles,doc,words,VSM)
        scoreDocList.append([score,doc])
    for doc in scoreDocList:
        if str(doc[1]) in PHRASEDOCLIST.keys():
            ph_w=1+math.log2(len(PHRASEDOCLIST[str(doc[1])]))
            doc[0] = doc[0] * (1 + ph_w * 0.1)
            # print('whole phrase exist in:'+str(doc[1]))
    return sorted(scoreDocList,reverse = True)

def sortScoreDocList_BM25(index,nfiles,words,docList,AVG_L,LD):
    scoreDocList = []
    for doc in docList:
        score = BM25(index,nfiles,doc,words,AVG_L,LD)
        scoreDocList.append([score,doc])
    return sorted(scoreDocList,reverse = True)


def getVSMScore(index,nfiles,docName,QueryWords,VSM):
    score = 0
    docName = str(docName)
    #分母的两个平方数
    square1=0
    square2=0
    line=VSM[docName]
    #文档的平方数可以直接根据文件计算
    for v in line.values():
        square2+=float(v)**2
    for word in QueryWords.keys():
        if word not in index or docName not in index[word]:
            continue
        df = len(index[word])
        #查询单词的Wf
        w_wf=1 + cmath.log10(QueryWords[word]).real
        idf = cmath.log10(nfiles / df).real
        weight_w=w_wf*idf
        weight_doc=float(line[word])
        #分子
        score +=weight_doc*weight_w
        score=adjust(word,score,docName)
        square1 +=(weight_w)**2

    score=score/(cmath.sqrt(square2*square1).real)
    return score

def BM25(index,nfiles,docName,QueryWords,AVG_L,LD):
    score = 0
    docName = str(docName)
    k1=1.2
    b=0.75
    for word in QueryWords:
        if word not in index or docName not in index[word]:
            continue
        tf = len(index[word][docName])
        df = len(index[word])
        w = cmath.log(2,( nfiles- df + 0.5) / (df + 0.5)).real
        s = (k1 * tf * w) / (tf + k1 * (1 - b + b * LD[docName] /AVG_L))
        s=adjust(word,s,docName)
        score += s
    return score

def adjust(word,temp,docName):
    with open(datapath+ '/adjust.txt','r') as f:
        lines=f.readlines()
        for line in lines:
            templist=line.split(',')
            if templist[0]==word and templist[1]==docName:
                print(adjust)
                if templist[2].strip()=='up':

                    return temp*1.2
                else:
                    return temp*0.8
    return temp