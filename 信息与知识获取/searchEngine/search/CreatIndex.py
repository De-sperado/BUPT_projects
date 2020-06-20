import os
from .helper import *
import json
from nltk.stem import WordNetLemmatizer
from nltk.corpus import wordnet
import nltk
import cmath
def getContent(filename):
    file = open(filename,'r')
    a = json.loads(file.readline())
    if not a['Headline'][0] or not a['Article_Body'][0]:
        return ''
    content=a['Headline'][0]+' '+a['Article_Body'][0]
    words = getStem(content)
    return words



def get_wordnet_pos(treebank_tag):
    if treebank_tag.startswith('J'):
        return wordnet.ADJ
    elif treebank_tag.startswith('V'):
        return wordnet.VERB
    elif treebank_tag.startswith('N'):
        return wordnet.NOUN
    elif treebank_tag.startswith('R'):
        return wordnet.ADV
    else:
        return None
def getStem(sentence):
    result = []
    for word, pos in nltk.pos_tag(nltk.word_tokenize(sentence)):
        pos=get_wordnet_pos(pos)
        if not pos:
            pos=wordnet.NOUN
        flag=0
        #去除字母之外的成分
        for c in word:
            if not c.isalpha():
                flag=1
                break
        if flag:
            continue
        result.append(WordNetLemmatizer().lemmatize(word, pos=pos))
    print(result)

    return result
def createIndex():
    Index = {}
    files = os.listdir(rawpath)
    for file in files:
        content = getContent(rawpath + '\\' + file)
        filename = helper.getFileName(file)
        index = 0
        for word in content:
            if word not in Index.keys():
                docs = {}
                docs[filename] = [index]
                Index[word] = docs
            else:
                if filename not in Index[word]:
                    Index[word][filename] = [index]
                else:
                    Index[word][filename].append(index)
            index += 1
    #获取词项列表
    Words = []
    for word in Index.keys():
        Words.append(word)
    #将数据写入文件中
    helper.Save(Index, helper.datapath + '\\Index.json')
    helper.Save(Words, helper.datapath + '\\Words.json')

def UpdataIndex(Index):
    old=set()
    #获取之前存在的文件列表
    for key,value in Index:
        old=old+set(value.keys())
    path=helper.rawpath
    files = os.listdir(path)
    for file in files:
        filename = helper.getFileName(file)
        #如果在之前的索引中没有该文件
        if filename not in old:
            content = getContent(path + '\\' + file)
            filename = helper.getFileName(file)
            pos = 0
            for word in content:
                if word not in Index:
                    docs = {}
                    docs[filename] = [pos]
                    Index[word] = docs
                else:
                    if filename not in Index[word]:
                        Index[word][filename] = [pos]
                    else:
                        Index[word][filename].append(pos)
                pos += 1
    Words = []
    for word in Index.keys():
        Words.append(word)
    #将数据写入文件中
    helper.Save(Index, helper.datapath + '\\Index.json')
    helper.Save(Words, helper.datapath + '\\Words.json')



def createVSM(index, wordList):
    files = os.listdir(helper.rawpath)
    nfiles = len(files)
    VSM = {}
    for file in files:
        docName = str(helper.getFileName(file))
        score = {}
        for word in wordList:
            if docName not in index[word] :
                continue

            tf = len(index[word][str(docName)])
            wf = 1 + cmath.log10(tf).real
            df = len(index[word])
            idf = cmath.log10(nfiles / df).real
            wf_idf = "%.2f" % float(wf * idf)
            score[word]=wf_idf

        VSM[docName] = score
    helper.Save(VSM, helper.datapath + 'vector.json')

