import copy
import math

def getEnthropyHelper(data, targetAttribute, targetAttributeValue):
    count = 0
    for instance in data[targetAttribute]:
        if instance == targetAttributeValue:
            count += 1
    
    if count == 0:
        return 0

    return -count * math.log(count/len(data[targetAttribute]), 2) / len(data[targetAttribute])

def getEnthropy(data, targetAttribute, targetPossibleValues = None):
    if targetPossibleValues == None:
        targetPossibleValues = getPossibleValues(data, targetAttribute)
        
    sum = 0
    for value in targetPossibleValues:
        sum += getEnthropyHelper(data, targetAttribute, value)
    
    return sum

def getPossibleValues(data, attribute):
    possibleValues = []
    for instance in data[attribute]:
        if instance not in possibleValues:
            possibleValues.append(instance)
    
    return possibleValues

def getPossibleDivider(data, attribute):
    divider = []
    sortedData = sorted(data[attribute])
    for instance in range(len(sortedData) - 1):
        if sortedData[instance] != sortedData[instance + 1]:
            divider.append((sortedData[instance] + sortedData[instance + 1]) / 2)
            
    return divider
        

def divideData(data, chosenAttribute, chosenPossibleValues = None, includeChosenAttribute = False):
    if chosenPossibleValues == None:
        chosenPossibleValues = getPossibleValues(data, chosenAttribute)
    
    dividedData = []
    for value in chosenPossibleValues:
        indices = []
        dataWithValue = {}
        i = 0
        for instance in data[chosenAttribute]:
            if instance == value:
                indices.append(i)
            i += 1
        
        for attribute in data:
            if not includeChosenAttribute and attribute == chosenAttribute:
                continue
            i = 0
            for instance in data[attribute]:
                if i in indices:
                    if attribute not in dataWithValue:
                        dataWithValue[attribute] = []
                    dataWithValue[attribute].append(instance)
                i += 1
        dividedData.append(dataWithValue)
    
    return dividedData

def divideDataContinu(data, chosenAttribute, targetAttribute):
    chosenKey = []
    
    localdata = data.copy()
    
    for originalattribute in localdata:
        chosenKey.append(originalattribute)
        
    
    dividers = getPossibleDivider(localdata, chosenAttribute)
        
    for divider in dividers:
        inputlist = []
        for instance in localdata[chosenAttribute]:
            if instance <= divider:
                inputlist.append(0)
            else:
                inputlist.append(1)
        localdata[chosenAttribute+"#"+str(divider)] = inputlist
    
    gains = {}
    
    for divider in dividers:
        gains[str(divider)] = getGain(localdata, targetAttribute, chosenAttribute+"#"+str(divider))
    
    maxGain = 0
    key = None
    
    for k,v in gains.items():
        if v > maxGain:
            maxGain = v
            key = k
            
    chosenKey.append(chosenAttribute+"#"+key)
    
    attrNow = []
    
    threshold = float(key)
    
    for attribute in localdata:
        attrNow.append(attribute)
    for attr in attrNow:
        if attr not in chosenKey:
            del localdata[attr]
    del localdata[chosenAttribute]
    
    return localdata, chosenAttribute+"#"+key, threshold
    

def getGain(data, targetAttribute, chosenAttribute):
    chosenPossibleValues = getPossibleValues(data, chosenAttribute)
    
    dividedData = divideData(data, chosenAttribute, chosenPossibleValues)
    
    enthropySum = 0
    for dData in dividedData:
        enthropySum += len(dData[targetAttribute]) * getEnthropy(dData, targetAttribute) / len(data[targetAttribute])
    
    return getEnthropy(data, targetAttribute) - enthropySum

def getSplitInformation(data, targetAttribute, chosenAttribute):
    dividedData = divideData(data, chosenAttribute, getPossibleValues(data, chosenAttribute))
    split = 0
    for dData in dividedData:
        split -= len(dData[targetAttribute]) * math.log(len(dData[targetAttribute]) / len(data[targetAttribute])) / len(data[targetAttribute])
    
    return split

def getGainRatio(data, targetAttribute, chosenAttribute):
    gain = getGain(data, targetAttribute, chosenAttribute)
    split = getSplitInformation(data, targetAttribute, chosenAttribute)
    
    return gain / split

def getBestAttribute(data, targetAttribute, gainRatio = False):
    bestAttribute = {
        'attributeName': None,
        'gain': 0
    }
    
    for attribute in data:
        if attribute == targetAttribute:
            continue
            
        gain = 0
        if gainRatio:
            gain = getGainRatio(data, targetAttribute, attribute)
        else:
            gain = getGain(data, targetAttribute, attribute)
        if gain > bestAttribute['gain']:
            bestAttribute['attributeName'] = attribute
            bestAttribute['gain'] = gain
    
    return bestAttribute['attributeName']

def getMostCommonValue(data, attribute):
    values = {}
    for instance in data[attribute]:
        if instance not in values:
            values[instance] = 1
        else:
            values[instance] += 1
    
    mostCommon = {
        'value': None,
        'count': 0
    }
    for value in values:
        if mostCommon['count'] < values[value]:
            mostCommon = {
                'value': value,
                'count': values[value]
            }
    
    return mostCommon['value']

# Tree Node Representation
# {
#     attributeName string
#     label boolean
#     children {
#        attributeVal string
#        nextNode node
#     }[]
# }

class Node:
    def __init__(self, attributeName):
        self.attributeName = attributeName
        self.label = True
        self.threshold = None
        self.children = []
    
    def addChildren(self, attributeVal, newNode):
        if newNode == None:
            return
        self.children.append({
            'attributeVal': attributeVal,
            'nextNode': newNode
        })
    
    def describe(self, level = 0):
        for i in range(0, level):
            print('        ', end = '')
        if self.threshold != None:
            print(self.attributeName+" With Threshold "+str(self.threshold))
        else:
            print(self.attributeName)
        for i in range(0, level):
            print('        ', end = '')
        print('Children count:', len(self.children))
        for i in range(0, level):
            print('        ', end = '')
        print('Is Leaf:', self.label)
        for child in self.children:
            for i in range(0, level):
                print('        ', end = '')
            print('If val: ', child['attributeVal'])
            child['nextNode'].describe(level + 1)

def myID3(data, targetAttribute, node, gainRatio = False):
    enthropy = getEnthropy(data, targetAttribute)
    newNode = Node(getMostCommonValue(data, targetAttribute))
    
    bestAttribute = None
    if enthropy > 0:
        bestAttribute = getBestAttribute(data, targetAttribute, gainRatio)
        if bestAttribute != None:
            newNode = Node(bestAttribute)
            newNode.label = False
    
    if node == None:
        node = newNode
    
    if bestAttribute != None:
        nextData = divideData(data, bestAttribute)
        i = 0
        for value in getPossibleValues(data, bestAttribute):
            newNode.addChildren(value, myID3(nextData[i], targetAttribute, node))
            i += 1
        
    return newNode

def myc45(data, targetAttribute, node, continu, gainRatio = False):
    enthropy = getEnthropy(data, targetAttribute)
    newNode = Node(getMostCommonValue(data, targetAttribute))
    
    bestAttribute = None
    if enthropy > 0:
        bestAttribute = getBestAttribute(data, targetAttribute, gainRatio)
        if bestAttribute != None:
            newNode = Node(bestAttribute)
            newNode.label = False
    
    if node == None:
        node = newNode
    
    if bestAttribute != None:
        if bestAttribute in continu:
            discreetedData, attrName, threshold = divideDataContinu(data, bestAttribute, targetAttribute)
            nextData = divideData(discreetedData, attrName)
            i = 0
            for value in getPossibleValues(discreetedData, attrName):
                newNode.attributeName = attrName
                newNode.threshold = threshold
                newNode.addChildren(value, myc45(nextData[i], targetAttribute, node, continu))
                i += 1
        else:
            nextData = divideData(data, bestAttribute)
            i = 0
            for value in getPossibleValues(data, bestAttribute):
                newNode.addChildren(value, myc45(nextData[i], targetAttribute, node, continu))
                i += 1
        
    return newNode

def cleanTree(tree):
    if (len(tree.children) == 0):
        return
    if '#' in tree.attributeName:
        tree.attributeName = tree.attributeName.split('#')[0]
    for child in tree.children:
        cleanTree(child['nextNode'])

def traverseDownTree(tree, instance):
    if (len(tree.children) == 0):
        return tree.attributeName
    else:
        if tree.threshold != None:
            realName = tree.attributeName.split('#')[0]
            if instance[realName] > tree.threshold:
                return traverseDownTree(tree.children[1]['nextNode'], instance)
            else:
                return traverseDownTree(tree.children[0]['nextNode'], instance)
        else:
            for i in tree.children:
                if (i['attributeVal'] == instance[tree.attributeName]):
                    return traverseDownTree(i['nextNode'], instance)
                
def getMostCommonValueGivenCondition(data, targetAttribute, condition):
    keys = condition.keys()
    values = {}
    
    for i in range(0,len(data)):
        isCandidateTrue = True
        for j in keys:
            if (data.iloc[i][j] != condition[j]):
                isCandidateTrue = False
                break
        if (isCandidateTrue):
            if (data.iloc[i][targetAttribute] in values):
                values[data.iloc[i][targetAttribute]] += 1
            else:
                values[data.iloc[i][targetAttribute]] = 1
    mostCommon = {
        'value':None,
        'count':0
    }
    for i in values:
        if (values[i] > mostCommon['count']):
            mostCommon['value'] = i
            mostCommon['count'] = values[i]
    return mostCommon
            
                
def measureAccuracy(trees, data, targetAttribute):
    trueCount = 0
    for i in range(0, len(data)):
        if (traverseDownTree(trees, data.iloc[i]) == data.iloc[i][targetAttribute]):
            trueCount += 1
            
    return trueCount / len(data)
    
def reducedErrorPruning(tree, trainingData, validationData, targetAttribute, pruneList, condition):
    if (len(tree.children) == 0):
        return 0
    else:        
        for i in tree.children:
            tempCondition = copy.deepcopy(condition)
            tempCondition[tree.attributeName] = i['attributeVal']
            leaf = Node(getMostCommonValueGivenCondition(trainingData, targetAttribute, condition))
            temp = copy.deepcopy(i['nextNode'])
            i['nextNode'] = leaf
            accuracy = measureAccuracy(tree, validationData, targetAttribute)
            pruneList.append({
                'attributeName':tree.attributeName,
                'accuracy':accuracy,
                'attributeVal':tempCondition[tree.attributeName],
                'leaf':leaf
            })
            i['nextNode'] = temp
        for i in tree.children:
            condition[tree.attributeName] = i['attributeVal']
            reducedErrorPruning(i['nextNode'], trainingData, validationData, targetAttribute, pruneList, condition)
        removedNode = {
            'attributeName':None,
            'value':0,
            'attributeVal':None,
            'leaf':None
        }
        for i in pruneList:
            if (i['accuracy']> removedNode['value']):
                removedNode['attributeName'] = i['attributeName']
                removedNode['value'] = i['accuracy']
                removedNode['attributeVal']=i['attributeVal']
                removedNode['leaf']=i['leaf']
        return removedNode
    
def changeNode(tree, attributeName, attributeValue, value):
    if (len(tree.children) == 0):
        return tree
    else:
        for i in tree.children:
            if (i['nextNode'] == attributeName):
                i['nextNode'] = Node(value)
            changeNode(i, attributeName, attributeValue, value)
    
    
def pruneTree(tree, trainingData, validationData, targetAttribute):
    accuracy = measureAccuracy(tree, validationData, targetAttribute)
    node = reducedErrorPruning(tree, trainingData, validationData, targetAttribute, [], {})
    while (node['value'] > accuracy):
        changeNode(tree, node['attributeName'], node['attributeVal'], node['leaf'])
    return tree

def ultimateC45(trainingData, validationData, targetAttribute, node, continu, gainRatio = False):
    tree = myc45(trainingData, targetAttribute, node, continu, gainRatio)
    cleanTree(tree)
    pruneTree(tree, trainingData, validationData, targetAttribute)
    return tree

def handleMissingAttributeHelper(data, targetAttribute):
    for attribute in data:
        mostCommonValue = getMostCommonValue(data, attribute)
        i = 0
        for instance in data[attribute]:
            if instance == None:
                data[attribute][i] = mostCommonValue
            i += 1

def handleMissingAttribute(data, targetAttribute):
    possibleTargetValues = getPossibleValues(data, targetAttribute)
    dividedData = divideData(data, targetAttribute, includeChosenAttribute = True)
    data = {}
    for dData in dividedData:
        handleMissingAttributeHelper(dData, targetAttribute)
        for attribute in dData:
            if attribute not in data:
                data[attribute] = []
            for instance in dData[attribute]:
                data[attribute].append(instance)
    return data