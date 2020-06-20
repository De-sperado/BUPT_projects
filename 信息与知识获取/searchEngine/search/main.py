import os
import nltk
import json

from .helper import *
from .CreatIndex import *
from .corrector import *
from .search import *
from .Rank import *
from collections import Counter

words = getFile('Words')
INDEX = getFile('Index')
vector = getFile('vector')
LD = getFile('LD')

nfiles = nfiles
#向量空间模型算法
def VSM(Query):
    QueryWords = getStem(Query)
    QueryWords = correct(QueryWords)
    wordset = Counter(QueryWords)
    docs = getDocList(INDEX, wordset)
    phDocs = getPhraseDocList(INDEX, wordset, QueryWords)
    rankDocs = getSortedDoc(INDEX, nfiles, wordset, docs, phDocs, vector)
    print(len(rankDocs))
    if len(rankDocs)>100:
        rankDocs=rankDocs[:100]
    newdocs = []
    docIds = []
    scores = []
    for doc in rankDocs:
        with open(os.path.join(rawpath, doc[1].__str__() + ".json"), 'r') as d:
            newdocs.append(json.loads(d.read()))
        docIds.append(doc[1])
        scores.append(doc[0])
    # for doc in rankDocs:
    #     print("doc ID: ", doc[1], " score: ", "%.4f" % doc[0])
    newdocs = DOCproc(list(zip(newdocs, docIds)))
    return list(zip(newdocs,docIds,scores))
#BM25模型算法
def BM25(Query):
    QueryWords = getStem(Query)
    QueryWords = correct(QueryWords)

    wordset = Counter(QueryWords)

    docs = getDocList(INDEX, wordset)
    rankDocs = sortScoreDocList_BM25(INDEX, nfiles, wordset, docs, AVG_L, LD)
    if len(rankDocs)>100:
        rankDocs=rankDocs[:100]
    newdocs = []
    docIds = []
    scores = []
    for doc in rankDocs:
        with open(os.path.join(rawpath, doc[1].__str__() + ".json"), 'r') as d:
            newdocs.append(json.loads(d.read()))
        docIds.append(doc[1])
        scores.append(doc[0])


    newdocs = DOCproc(list(zip(newdocs, docIds)))
    return list(zip(newdocs, docIds, scores))
#获取文档列表
def DOCproc(keyDoc):
    newDoc=[]
    for doc,id in keyDoc:
        # print(id)
        ndoc={}
        ndoc['Url']=doc['Url'][0]
        ndoc['FirstPublishDate']=doc['FirstPublishDate'][0]
        ndoc['Headline']=doc['Headline'][0]
        ndoc['Article_Body']=doc['Article_Body'][0]
        if doc['MappedSection'] != False:
            ndoc['MappedSection']=doc['MappedSection'][0]
        else:
            ndoc['MappedSection']="None"
        newDoc.append(ndoc)
    return newDoc
#短语查询
def phrase(Query):
    QueryWords = getStem(Query)
    QueryWords = correct(QueryWords)

    wordset = Counter(QueryWords)

    phDocs = searchsortPhrase(INDEX, wordset, QueryWords)
    if 0 == len(phDocs):
        print("Doesn't find \"", QueryWords, '"')
    else:
        newdocs = []
        docIds = []
        for doc in phDocs:
            with open(os.path.join(rawpath, doc[0].__str__() + ".json"), 'r') as d:
                newdocs.append(json.loads(d.read()))
            docIds.append(doc[0])
        newdocs = DOCproc(list(zip(newdocs, docIds)))
        return list(zip(newdocs, docIds))

def getDoc(keyWord,sortKind):
    statement = keyWord
    #查询排序
    if sortKind == '0':
        return VSM(statement)
    elif sortKind == '1':
        return BM25(statement)
    # 近义词查询
    elif sortKind == '4':
        return phrase(statement)
    else:
        return []

