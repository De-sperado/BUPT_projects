from django.shortcuts import render
from django.http import HttpResponse
from .models import DOC
from .main import *
from .helper import *
from .CreatIndex import *
from .corrector import *
from .search import *
from .Rank import *
import json

def firstpage(request):
    return render(request,"SearchPage.html")


# keyText为用户输入的关键词
# order为选择的排序方式，默认为相关度
def search(request):
    # 关键词放在keyword
    # 然后返回一个DOC列表
    keyword = request.GET.get("keyText","")
    INPUTWORDS = getStem(keyword)
    INPUTWORDS = correct(INPUTWORDS)
    highWord=""
    for word in INPUTWORDS:
        highWord=highWord+" "+word
    sortkind = request.GET.get("order",'0')
    keyDoc =keypages(keyword,sortkind)
    d= {'keyDoc':keyDoc, 'keyword': keyword,'sortKind':sortkind,'highWord':highWord}
    return render(request, "showResult.html", d)


# 返回符合关键词的list
def keypages(keyword,sortKind):
    res = getDoc(keyword,sortKind)
    # res为json列表和id列表
    return res
# Create your views here.

def specificDOC(request,docId):
    with open(os.path.join(rawpath, docId.__str__()+'.json'),'r') as d:
        doc=json.loads(d.read())
    keyword=request.GET.get("keyword")
    ndoc = {}
    ndoc['Url'] = doc['Url'][0]
    ndoc['FirstPublishDate'] = doc['FirstPublishDate'][0]
    ndoc['Headline'] = doc['Headline'][0]
    ndoc['Article_Body'] = doc['Article_Body'][0]
    if doc['MappedSection'] != False:
        ndoc['MappedSection'] = doc['MappedSection'][0]
    else:
        ndoc['MappedSection'] = "None"
    if request.method == 'POST':
        adjustScore(request,docId,keyword)
        return render(request, "specificDOC.html", {'doc': ndoc, 'keyword': keyword, 'id': docId,'show':"True"})
    return render(request,"specificDOC.html",{'doc':ndoc,'keyword':keyword,'id':docId})


def adjustScore(request,docId,keyword):
    if request.POST.get("isUseful")=="有用":
        adjustSTR="up"
    else:
        adjustSTR="down"
    print(keyword)
    if keyword == "":
        return
    INPUTWORDS = getStem(keyword)
    print(INPUTWORDS)
    WORDSET = set(INPUTWORDS)
    with open(datapath+ '/adjust.txt', 'a') as w:
        for word in WORDSET:
            wr=word+","+str(docId)+","+adjustSTR+"\n"
            w.write(wr)
    return