import networkx as nx
import sys
import matplotlib.pyplot as plt
import numpy as np
from adjustText import adjust_text

#finds the shortest paths from a starting node to all other nodes in the network
def dijkstraShortest(G, nodeSource):
    targetNodes = list(G.nodes)
    transferTime = 300
    shortestPaths = {} 
    visitedNodePaths = {} 
    lineUsed = {} 
    
    #sets the shortest length to each node to the max size
    maxValue = sys.maxsize
    for node in targetNodes:
        shortestPaths[node] = maxValue
        lineUsed[node] = maxValue
    
    #sets the starting node path length to zero so that algorith will begin with this node
    shortestPaths[nodeSource] = 0
    
    #loops until every target node has been used
    while len(targetNodes) != 0: 
        
        #finds the node with the shortest current path length
        closestNode = None
        for node in targetNodes:
            if closestNode == None:
                closestNode = node
            elif shortestPaths[node] < shortestPaths[closestNode]:
                closestNode = node

        #finds all the edges coming from the chosen node with shortest current path length
        closeNodeEdges = list(G.adj[closestNode])
        for edgeNode in closeNodeEdges:
        
        #checks if the edge is on the same line as the previous edge on the shortest path
            if lineUsed[closestNode] == G.edges[closestNode,edgeNode]["line"]:
                requiresTransfer = 0
            else:
                requiresTransfer = 1
            
            #calculates the length from the start node through each edge coming off the current shortest path node
            initialLength = shortestPaths[closestNode] + G.edges[closestNode,edgeNode]["weight"] + requiresTransfer * transferTime
            
            #tests if the new path is shorter to get to the node at the end of the connecting edge
            #updates shortest path if true
            if initialLength < shortestPaths[edgeNode]:
                shortestPaths[edgeNode] = initialLength
                visitedNodePaths[edgeNode] = closestNode
                lineUsed[edgeNode] = G.edges[closestNode,edgeNode]["line"]
        targetNodes.remove(closestNode)
    return visitedNodePaths, shortestPaths

#assembles the shortest path between two nodes from the dictionary provided by Dijkstra's algorithm
def pathFinder(nodeSource, nodeTarget, visitedNodePaths):
    path = []
    node = nodeTarget
    while node != nodeSource:
        path.append(node)
        node = visitedNodePaths[node]
    path.pop(0)
    return path

#returns the number from the set of data to allow for sorting
def numberGetter(listItem):
    return listItem[1]

#calculates the centrality measures fully and sorts into an ordered list
def orderedList(centralityMeasure, centralityType):
    for node in entranceList:
        if centralityType == "betweeness":
            centrality = (centralityMeasure[node]/numJournies)
            centralityMeasure[node] = centrality
        elif centralityType == "closeness":
            popEntering = tubeNet.nodes[node]["popIn"]
            centrality = (centralityMeasure[node]*popEntering)/((numOfNodes-1)*totalPop)
            centralityMeasure[node] = centrality
            
    #list is sorted as a tuple, from lowest value to highest
    orderedList = sorted(centralityMeasure.items(), key=numberGetter)
    return orderedList

#stores the data from network analysis as an ordered text file from lowest to highest
def file(file, fileType, orderedList):
    resultsFile = open(file, "w")
    resultsFile.write("Station" + "\t" + fileType + "\n")
    resultsFile.close()
    resultsFile = open(file, "a")
    for node in orderedList:
        resultsFile.write(node[0] + "\t" + str(node[1]) + "\n")
    resultsFile.close()

#plots a bar chart displaying a given amount of the top values for the chosen centrality metric
def barPlot(tupleOfValues, numOfBars, centralityType):
    stations = []
    values = []
    
    #collects the top x values from the tuple provided
    end = len(tupleOfValues)
    maxInList = end - numOfBars
    while maxInList < end:
        stations.append(tupleOfValues[maxInList][0])
        values.append(tupleOfValues[maxInList][1])
        maxInList = maxInList + 1
    
    #generates the figure for plotting on
    fig, ax = plt.subplots(figsize = (12,14))
    ax.barh(stations, values)
    
    #removes existing axes and tick marks
    for i in ["top", "right"]:
        ax.spines[i].set_visible(False)
    ax.xaxis.set_ticks_position("none")
    ax.yaxis.set_ticks_position("none")
    ax.xaxis.set_tick_params(pad = 3)
    ax.yaxis.set_tick_params(pad = 5)
    
    #adds numerical data to end of bars
    for i in ax.patches:
        plt.text(i.get_width()+0.2, i.get_y()+0.4,
                 str(round((i.get_width()), 1)), fontsize = 10, color = "black")
        
    #labels the x and y axes as well as the graph
    plt.ylabel("Stations with highest " + centralityType, fontsize = 12)
    plt.xlabel(centralityType, fontsize = 12)
    ax.set_title("Top " + str(numOfBars) + " stations with the highest " + centralityType, 
                 loc = "Left", fontsize = 16 )
    plt.show()

#calculates the mean and standard deviation of a given dataset
def meanAndStandardDeviation(dataset):
    total = 0
    for value in dataset:
        total = total + value
    mean = total/len(dataset)
    standardDeviation = np.std(dataset)
    return mean, standardDeviation

#creates a set of synced lists for betweeness and closeness
def sycnedLists(betweeness, closeness):
    betweenessValues = []
    closenessValues = []
    stations = []
    
    #matches betweeness and closeness values, adding each to sepreate lists at the same index within the list 
    for node in betweeness:
        i = 0 
        match = False
        while match == False:
            if node[0] == closeness[i][0]:
                match = True 
                betweenessValues.append(node[1])
                closenessValues.append(closeness[i][1])
                stations.append(node[0])
            i = i + 1
    return betweenessValues, closenessValues, stations
                               
#generates a graph which will be used as the basis for the model
tubeNet = nx.Graph()

#adds edges to the graph from a prepared edge list dataset    
tubeNet = nx.read_edgelist("tubeNetworkEdges.txt",delimiter="\t",
                            data=(("weight",float),("line",int)));

#adds node data to each node from the graph, taking data from a prepared dataset
nodeFile = open("tubeNetworkNodes.txt")
totalPop = 0
for line in nodeFile:
    lineAsList = line.split("\t")
    currentNode = lineAsList[0]
    currentPopIn = float(lineAsList[1])
    currentPopOut = float(lineAsList[2])
    tubeNet.add_node(currentNode, popIn=float(currentPopIn), popOut = float(currentPopOut))
    totalPop = totalPop + currentPopIn
nodeFile.close()

#generates two lists of nodes which are used for entrance and exit nodes
entranceList = list(tubeNet.nodes)
exitNodes = list(tubeNet.nodes) 

#dictionary used to store the number of times a node is visited across all shortest paths
visitCount = {}

#dictionary used to store the total length between each node and all other nodes on the shortest paths
sumOfLengths = {}

#useful values for calculating closeness and betweeness centrality
numOfNodes = len(entranceList)
numJournies = (numOfNodes - 1) * (numOfNodes - 2)

#sets all nodes initial values to zero
for node in entranceList:
    visitCount[node] = 0
    sumOfLengths[node] = 0

#runs dijkstra's algorith for every node
for entrance in entranceList:
    visitedNodePaths, shortestPaths = dijkstraShortest(tubeNet, entrance)
    
    #removes the visited entrances from the set of exit nodes to ensure no duplication of paths
    exitNodes.remove(entrance)
    for exits in exitNodes:
        
        #adds the shortest length between the entrance and exit nodes, and adds this to the total sum of lengths for those nodes
        sumOfLengths[entrance] = sumOfLengths[entrance] + shortestPaths[exits]
        sumOfLengths[exits] = sumOfLengths[exits] + shortestPaths[exits]
        
        #calculates the significance of the route based on the entrance and exit nodes population and adds this value to each node on the shortest path
        path = pathFinder(entrance, exits, visitedNodePaths)
        popEntering = tubeNet.nodes[entrance]["popIn"]
        popExiting = tubeNet.nodes[exits]["popOut"]
        popModifiedPathValue = ((popEntering/(numOfNodes-1)) * (popExiting/(numOfNodes - 1)))
        for visitedNode in path:
            visitCount[visitedNode] = visitCount[visitedNode] + popModifiedPathValue

betweeness = orderedList(visitCount, "betweeness")
file("tubeNetworkBetweeness.txt", "betweeness", betweeness)
closeness = orderedList(sumOfLengths, "closeness",)
file("tubeNetworkCloseness.txt", "closeness", closeness)
betweenessValues, closenessValues, stations = sycnedLists(betweeness, closeness)

#calculates the mean and standard deviation for both closeness and betweeness
meanBetweeness, betweenessSD = meanAndStandardDeviation(betweenessValues)
meanCloseness, closenessSD = meanAndStandardDeviation(closenessValues)

#calculates the importance of every node based on mean and standard deviation values
importance = {}
for i in range (0, len(stations)):
    b = (betweenessValues[i])/(betweenessSD)
    c = (closenessValues[i])/(closenessSD)
    a = (np.sqrt(b ** 2 + c ** 2))
    importance[stations[i]] = a
importanceList = orderedList(importance, "importance")
file("tubeNetworkImportance.txt","importance", importanceList)
barPlot(betweeness, 10, "betweeness centrality")
barPlot(closeness, 10, "closeness centrality")
barPlot(importanceList, 10, "importance rank")
importanceValues = []
for node in importance:
    importanceValues.append(importance[node])
total = 0
for value in importanceValues:
    total = total + value
mean = total/len(importanceValues)
standardDeviation = np.std(importanceValues)
twoDeviations = mean + 2 * standardDeviation
importantStations = []
importantBetweeness = []
importantCloseness = []
for i in range (0, len(betweenessValues)):
    if importance[stations[i]] > twoDeviations:
        importantStations.append(stations[i])
        importantBetweeness.append(betweenessValues[i])
        importantCloseness.append(closenessValues[i])
fig = plt.figure(figsize = (16,9))
scatterPlot = fig.add_subplot()
scatterPlot.scatter(betweenessValues,closenessValues)
plt.ylabel("Closeness centrality", fontsize = 14, color = "black")
plt.xlabel("Betweeness centrality", fontsize = 14, color = "black")
scatterPlot = [scatterPlot.annotate(txt,(importantBetweeness[x],
        importantCloseness[x]), xytext=(importantBetweeness[x]+1.5,importantCloseness[x]+4.5),
        arrowprops=dict(arrowstyle="->")) for x, txt in enumerate(importantStations)]
adjust_text(scatterPlot)
plt.plot

            



