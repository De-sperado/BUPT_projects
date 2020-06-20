# -*- coding: utf-8 -*-
# @Author: 刘威
# @Date:   2020-05-13 17:57:28
# @Last Modified by:   liuwei0012
# @Last Modified time: 2020-06-05 11:26:38
import json
import os
import nltk

projectpath = os.getcwd()
rawpath=projectpath+'/raw'
datapath=projectpath+'/data'
# print("projectpath:",projectpath)
# print("data path",rawpath)

def Save(item,filename):
    # 将数据写入到文件中
    file = open(filename,'w')
    str = json.JSONEncoder().encode(item)
    file.write(str)
    file.close()

#获取文档名中的文档的id
def getFileName(filename):
    end = filename.find('.')
    docName = filename[0:end]
    return int(docName)

def getFile(filename):
    file = open(projectpath +'/data/'+filename+'.json', 'r')
    indexStr = file.read()
    index = json.JSONDecoder().decode(indexStr)
    return index

nfiles=len(os.listdir(rawpath))
def getavg_L():
    files = os.listdir(rawpath)
    n=0
    LD={}
    for filename in files:
        file = open(rawpath+"\\"+filename, 'r')
        a = json.loads(file.readline())
        if 'Headline' in a.keys():
            content = str(a['Headline'][0]) + ' ' + a['Article_Body'][0]
        else:
            content = a['Article_Body'][0]
        n+=len(content)
        LD[filename.split('.')[0]]=len(content)
        Save(LD,'LD.json')
    return n/nfiles

下载需要的依赖文件,第一次运行时下载  后续运行时注释掉
nltk.download("wordnet")
nltk.download("averaged_perceptron_tagger")
nltk.download("punkt")
nltk.download("maxnet_treebank_pos_tagger")

AVG_L=7000