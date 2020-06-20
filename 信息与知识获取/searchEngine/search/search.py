import queue
# 将所有word的结果取并，即所有包含这些word的文档
def getDocList(index, QueryWords):
    if len(QueryWords) == 0:
        return []
    res=[]
    for word in QueryWords.keys():
        if word in index.keys():
            docList = [int(key) for key in index[word].keys()]
            res.append(docList)
    ans=[]
    for list1 in res:
        ans=list(set(list1+ans))
    ans.sort()
    return ans


def getPhraseDocList(index, QueryWords, RawInputList):
    if len(QueryWords) == 0:
        return []
    docQueue = queue.Queue()
    for word in QueryWords.keys():
        if word not in index:
            return []
        else:
            docList = [int(key) for key in index[word].keys()]
            docList.sort()
        docQueue.put(docList)

    while docQueue.qsize() > 1:
        list1 = docQueue.get()
        list2 = docQueue.get()
        list3 = list(set(list1).intersection(set(list2)))
        docQueue.put(list3)
    doclist = docQueue.get()
    result = {}

    if len(RawInputList) == 1:
        for doc in doclist:
            result[doc] = index[RawInputList[0]][str(doc)]
        return result

    for docName in doclist:
        docName = str(docName)
        location = []
        for i in index[RawInputList[0]][docName]:
            temp = i
            flag = True
            for word in RawInputList[1:len(RawInputList)]:
                temp += 1
                try:
                    index[word][docName].index(temp)
                except:
                    flag = False
                    break
            if flag:
                location.append(i)
        if len(location) > 0:
            result[docName] = location
    return result

def searchsortPhrase(INDEX, WORDSET, INPUTWORDS):
    result=getPhraseDocList(INDEX, WORDSET, INPUTWORDS)
    return sorted(result.items(), key=lambda x: len(x[1]), reverse=True)

