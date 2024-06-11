#!/usr/bin/python3.8

NUM_OF_SIGNATURES = 40

import sys, csv
import numpy as np
from pathlib import Path
import matplotlib.pyplot as plt
from universalHashFunctions import create_random_hash_function

import time #TODO: delete it, only used for debugging purposes

# Set numpy options to print full array
np.set_printoptions(threshold = sys.maxsize)

# Command-line input check
if len(sys.argv) != 5:
    print("Invalid number of arguments.")
    print("Please, type: 'python main.py <name>.csv <s> <n> <i>'\n")
    print("Parameters:")
    print("\t<s>: threshold between 0 and 1")
    print("\t<n>: number of movies to compare")
    print("\t<i>: 1 for creating new SIG.csv file, 0 to keep the same")
    exit()

if float(sys.argv[2]) < 0 or float(sys.argv[2]) > 1:
    print("Invalid parameter <s>. Please, input threshold between 0 and 1.0 .")
    exit()

if int(sys.argv[4]) != 0 and int(sys.argv[4]) != 1:
    print("Invalid parameter <i>.\n<i>: 1 for creating new SIG.csv file, 0 to keep the same")
    exit()

inputFileName = sys.argv[1]
inputFileNameSplit = inputFileName.split(".")
inputThreshold = float(sys.argv[2])
inputNumOfMoviesToCompare = int(sys.argv[3])

userList = {}
movieMap = {}
movieList = {}

# Jaccard similarities between the pairs of first numOfMoviesToCompare movies
JSims = {}
relevantElements = 0
lstOfPairs = []


# Read .csv files from EXPERIMENTS folder and load them to dictionaries
def loadDictionariesFromCSV():
    # Load user_list.csv to userList dict
    pathStr = "../EXPERIMENTS/" + inputFileNameSplit[0] + "_user_list.csv"
    path = Path(__file__).parent / pathStr

    with path.open(mode = 'r') as csvFile:
        csvReader = csv.reader(csvFile, delimiter = ',')
        lineCounter = 0

        for row in csvReader:
            lineCounter += 1

            if lineCounter != 1:
                userList[row[0]] = []

                for i in range(1, len(row)):
                    userList[row[0]].append(row[i])

    # Load movie_map.csv to movieMap dict
    pathStr = "../EXPERIMENTS/" + inputFileNameSplit[0] + "_movie_map.csv"
    path = Path(__file__).parent / pathStr

    with path.open(mode = 'r') as csvFile:
        csvReader = csv.reader(csvFile, delimiter = ',')
        lineCounter = 0

        for row in csvReader:
            lineCounter += 1

            if lineCounter != 1:
                movieMap[row[0]] = int(row[1])

    # Load movie_list.csv to movieList dict
    pathStr = "../EXPERIMENTS/" + inputFileNameSplit[0] + "_movie_list.csv"
    path = Path(__file__).parent / pathStr

    with path.open(mode = 'r') as csvFile:
        csvReader = csv.reader(csvFile, delimiter = ',')
        lineCounter = 0

        for row in csvReader:
            lineCounter += 1

            if lineCounter != 1:
                movieList[row[0]] = []

                for i in range(1, len(row)):
                    movieList[row[0]].append(row[i])


# ---------- Question (1b) ----------
def jaccardSimilarity(movieId1, movieId2):
    s1 = set(movieList[movieId1])
    s2 = set(movieList[movieId2])

    JACCARD = ( len(s1.intersection(s2)) / len(s1.union(s2)))

    return JACCARD

# ---------- Question (1c) ----------
def minHash(numberOfPermutations):
    SIG = np.matrix(np.ones((numberOfPermutations, len(movieList))) * np.inf)

    for i in range(numberOfPermutations):
        hashFunction = create_random_hash_function(m = len(userList))

        for userId in userList:
            for movieId in userList[userId]:
                hashValue = hashFunction(int(userId) - 1)

                if hashValue < SIG.item((i, movieMap[movieId] - 1)):
                    SIG.itemset((i, movieMap[movieId] - 1), hashValue)

    # Cast SIG to int type
    SIG = SIG.astype(int)

    return SIG

# ---------- Question (1d) ----------
def signatureSimilarity(movieId1, movieId2, SIG, n):
    numOfRows = np.shape(SIG)[0]
    if n < 0 or n > numOfRows:
        print("signatureSimilarity: n should be between 0 and SIG's num of rows.")
        exit()

    counterOfSimSigs = 0
    for i in range(n):
        if SIG.item((i, movieMap[movieId1] - 1)) == SIG.item((i, movieMap[movieId2] - 1)):
            counterOfSimSigs += 1

    return counterOfSimSigs/n

# ---------- Question (1e) ----------
def LSH(n, r, b, SIG, numOfMoviesToCompare):
    candidatePairs = []
    numOfBuckets = 1000000   #TODO: Check 1 million

    # Create a random hash function, m: number of buckets
    # TODO: check which is the suitable value of m
    hashFunction = create_random_hash_function(m = numOfBuckets)

    keys = list(movieMap.keys())
    values = list(movieMap.values())

    for i in range(b):
        buckets = {}

        for col in range(numOfMoviesToCompare):
            sigVectorLst = []
            for row in range(i*r, (i+1)*r):
                #print("col: {}, row: {}".format(col, row))
                # Calculate signature-vector from movie's signature
                if SIG.item((row, col)) < 10:
                    sigVectorLst.append("0" + str(SIG.item((row, col))))
                else:
                    sigVectorLst.append(SIG.item((row, col)))

            sigVectorString = ''.join(map(str, sigVectorLst))
            hashValue = hashFunction(int(sigVectorString))
            
            movieId = keys[col]       # '+1' because movies sequence start from 1 to N
            #movieIdSequenced = col + 1

            # Insert movieId in the corresponding bucket
            if hashValue in buckets:
                # Create pairs
                for entry in buckets[hashValue]:
                    pair = (entry, movieId)
                    candidatePairs.append(pair)

                buckets[hashValue].append(movieId)
            else:
                buckets[hashValue] = [movieId]

        # Clear buckets
        del buckets
        # Remove duplicate pairs
        candidatePairs = list(dict.fromkeys(candidatePairs))
        

    return candidatePairs
    
    

# ---------- Question (1z1) ----------
# s: threshold
def minHashingExperimentation(s, numOfPerms, SIG, numOfMoviesToCompare):
    global relevantElements
    # List with dictionaries, each dictionary list
    # corresponds to values of n' = 5, 10, ..., 40
    sigSims = []
    # falsePositives[i]/falseNegatives[i] corresponds to
    # number of false-positives and false-negatives respectively
    # for i = 0 : n' = 5, i = 1 : n' = 10, ...
    truePositives = []
    falsePositives = []
    falseNegatives = []
    trueNegatives = []

    keys = list(movieMap.keys())
    values = list(movieMap.values())

    print("\t\t #####")
    print("Experimentation: MIN-HASHING")
    print("File: '{}'".format(inputFileName))
    print("First '{}' movies are compared.".format(numOfMoviesToCompare))
    print("Threshold = {}, Number of signatures = {}".format(s, numOfPerms))
    print("\t\t #####\n")
            
    print("Number of relevant elements (ground truth) = {}\n".format(relevantElements))

    for n in range(5, numOfPerms + 5, 5):
        tempDict = {}
        for pair in lstOfPairs:
            tempSigSim = signatureSimilarity(pair[0], pair[1], SIG, n)
            tempDict[pair] = tempSigSim

        sigSims.append(tempDict)

    # Calculate true-pos, false-pos, false-neg, true-neg for each value of n'
    for sigSimsDict in sigSims:
        truePositivesCounter = 0
        falsePositivesCounter = 0
        falseNegativesCounter = 0
        trueNegativesCounter = 0

        for pair in lstOfPairs:
            if sigSimsDict[pair] >= s and JSims[pair] >= s:
                truePositivesCounter += 1
            elif sigSimsDict[pair] >= s and JSims[pair] < s:
                falsePositivesCounter += 1
            elif sigSimsDict[pair] < s and JSims[pair] >= s:
                falseNegativesCounter += 1
            else:
                trueNegativesCounter += 1

        truePositives.append(truePositivesCounter)
        falsePositives.append(falsePositivesCounter)
        falseNegatives.append(falseNegativesCounter)
        trueNegatives.append(trueNegativesCounter)

    # Calculate F1_scores
    PRECISION = []
    RECALL = []
    F1 = []
    numOfLoops = int(numOfPerms/5)
    for i in range(numOfLoops):
        pr = truePositives[i] / (truePositives[i] + falsePositives[i])
        re = truePositives[i] / (truePositives[i] + falseNegatives[i])
        f1 = 2 * re * pr / (re + pr)

        PRECISION.append(pr)
        RECALL.append(re)
        F1.append(f1)

        print("----- F1 scores for n' = {}: -----".format(i*5 + 5))
        print("True-positives = {}, False-positives = {}".format(truePositives[i], falsePositives[i]))
        print("True-negatives = {}, False-negatives = {}".format(trueNegatives[i], falseNegatives[i]))
        print("PRECISION: {}, RECALL: {}, F1: {}".format(PRECISION[i], RECALL[i], F1[i]))
        print("\n")

    # Plot the graphs of false-positives, false-negatives, PRECISION, RECALL, F1 values
    nStepValues = []
    for i in range(5, numOfPerms + 5, 5):
        nStepValues.append(i)

    plt.figure("Min-Hashing")
    plt.subplot(211)
    titleStr = "Min-Hashing\nMetrics for first {} movies of {}".format(numOfMoviesToCompare, inputFileName)
    plt.title(titleStr)
    plt.plot(nStepValues, falsePositives, 'go--', label='False positives')
    plt.plot(nStepValues, falseNegatives, 'co--', label='False negatives')
    plt.xlabel("n' (number of signatures used)")

    plt.legend(loc='best')
    plt.grid(True)

    plt.subplot(212)
    plt.plot(nStepValues, PRECISION, 'mo--', label='PRECISION')
    plt.plot(nStepValues, RECALL, 'yo--', label='RECALL')
    plt.plot(nStepValues, F1, 'bo--', label='F1')
    plt.xlabel("n' (number of signatures used)")

    plt.legend(loc='best')
    plt.grid(True)

    #plt.show()
    
    
# ---------- Question (1z2) ----------
def LSHExperimentation(numOfMoviesToCompare, s, SIG):
    rbValuesToTest = [(2, 20),
                      (4, 10),
                      (5, 8),
                      (8, 5),
                      (10, 4),
                      (20, 2)]
    truePositives = []
    falsePositives = []
    falseNegatives = []
    trueNegatives = []
    
    PRECISION = []
    RECALL= []
    F1 = []
    movieKeys = list(movieMap.keys())

    print("\t\t #####")
    print("Experimentation: LSH")
    print("File: '{}'".format(inputFileName))
    print("First '{}' movies are compared.".format(numOfMoviesToCompare))
    print("Threshold = {}, Number of signatures = {}".format(s, np.shape(SIG)[0]))
    print("\t\t #####\n")

    print("Number of relevant elements (ground truth) = {}\n".format(relevantElements))

    for entry in rbValuesToTest:
        truePositivesCounter = 0
        falsePositivesCounter = 0
        falseNegativesCounter = 0
        trueNegativesCounter = 0

        candidatePairs = LSH(np.shape(SIG)[0], entry[0], entry[1], SIG, numOfMoviesToCompare)

        # Calculate true-pos, false-pos
        for pair in candidatePairs:
            if JSims[pair] >= s:
                truePositivesCounter += 1
            elif JSims[pair] < s:
                falsePositivesCounter += 1

        # Calculate false-neg, true-neg
        for pair in lstOfPairs:
            if (pair not in candidatePairs):
                if JSims[pair] >= s:
                    falseNegativesCounter += 1
                else:
                    trueNegativesCounter += 1

        truePositives.append(truePositivesCounter)
        falseNegatives.append(falseNegativesCounter)
        falsePositives.append(falsePositivesCounter)
        trueNegatives.append(trueNegativesCounter)

        if truePositivesCounter == 0 and falsePositivesCounter == 0:
            pr = 0
        else:
            pr = truePositivesCounter / (truePositivesCounter + falsePositivesCounter)

        if truePositivesCounter == 0 and falseNegativesCounter == 0:
            re = 0
        else:
            re = truePositivesCounter / (truePositivesCounter + falseNegativesCounter)

        if pr == 0 and re == 0:
            f1 = 0
        else:
            f1 = 2 * re * pr / (re + pr)

        PRECISION.append(pr)
        RECALL.append(re)
        F1.append(f1)

        # Print the output
        print("----- r = {}, b = {} -----".format(entry[0], entry[1]))
        print("Number of candidate pairs found = {}".format(len(candidatePairs)))
        print("True-positives = {}, False-positives = {}".format(truePositivesCounter, falsePositivesCounter))
        print("True-negatives = {}, False-negatives = {}".format(trueNegativesCounter, falseNegativesCounter))
        print("PRECISION = {}, RECALL = {}, F1 = {}".format(pr, re, f1))
        print()

    # Plot the graphs of false-positives, false-negatives, PRECISION, RECALL, F1 values
    bValues = []
    for entry in rbValuesToTest:
        bValues.append(entry[1])

    plt.figure("LSH")
    plt.subplot(211)
    titleStr = "LSH\nMetrics for first {} movies of {}".format(numOfMoviesToCompare, inputFileName)
    plt.title(titleStr)

    plt.plot(bValues, falsePositives, 'go--', label='False positives')
    plt.plot(bValues, falseNegatives, 'co--', label='False negatives')
    plt.xlabel("b (number of bands)")

    plt.legend(loc='best')
    plt.grid(True)

    plt.subplot(212)
    plt.plot(bValues, PRECISION, 'mo--', label='PRECISION')
    plt.plot(bValues, RECALL, 'yo--', label='RECALL')
    plt.plot(bValues, F1, 'bo--', label='F1')
    plt.xlabel("b (number of bands)")

    plt.legend(loc='best')
    plt.grid(True)

    #plt.show()

def calculateJacSims(numOfMoviesToCompare):
    global JSims
    global lstOfPairs

    keys = list(movieMap.keys())

    # Make a list with the pairs of the first numOfMoviesToCompare movies
    for i in range(numOfMoviesToCompare):
        for j in range(i+1, numOfMoviesToCompare):
            lstOfPairs.append((keys[i], keys[j]))

    # Calculate Jaccard similarity between the pairs of numOfMoviesToCompare first movies
    for pair in lstOfPairs:
        tempJacSim = jaccardSimilarity(pair[0], pair[1])
        JSims[pair[0], pair[1]] = tempJacSim

    
def main():
    global relevantElements
    
    loadDictionariesFromCSV()
    
    # Calculate ONCE the Jaccard similarities
    calculateJacSims(inputNumOfMoviesToCompare)

    # Calculate the number of relevant elements
    for pair in JSims:
        if JSims[pair] >= inputThreshold:
            relevantElements += 1

    # Command-line input check
    if inputNumOfMoviesToCompare < 0 or inputNumOfMoviesToCompare > len(movieMap):
        print("Invalid parameter <n>.")
        exit()

    # If parameter <i> is 1 create new SIG file, else load the existing one
    if int(sys.argv[4]) == 1:
        SIG = minHash(NUM_OF_SIGNATURES)

        # Export SIG to .csv file in EXPERIMENTS folder
        pathStr = "../EXPERIMENTS/" + inputFileNameSplit[0] + "_SIG" + str(NUM_OF_SIGNATURES) + ".csv"
        path = Path(__file__).parent / pathStr
        with path.open(mode = 'w', newline = '') as SIG_file:
            SIG_writer = csv.writer(SIG_file, delimiter = ',')

            SIG_writer.writerow(["rows: i-th permutation", "columns: userIds for j-th movieId"])

            for i in range(NUM_OF_SIGNATURES):
                rowToWrite = []
                for j in range(np.shape(SIG)[1]):
                    rowToWrite.append(SIG.item((i, j)))
                SIG_writer.writerow(rowToWrite)

        print("SIG file was created successfully!\n")
    else:
        SIG = np.matrix(np.ones((NUM_OF_SIGNATURES, len(movieList))))

        # Import SIG matrix from EXPERIMENTS folder
        pathStr = "../EXPERIMENTS/" + inputFileNameSplit[0] + "_SIG" + str(NUM_OF_SIGNATURES) + ".csv"
        path = Path(__file__).parent / pathStr
        with path.open(mode = 'r') as csvFile:
            csvReader = csv.reader(csvFile, delimiter = ',')
            lineCounter = 0

            for row in csvReader:
                lineCounter += 1
                
                if lineCounter != 1:
                    for j in range(len(row)):
                        SIG.itemset((lineCounter - 2, j), row[j])

        # Cast SIG to int type
        SIG = SIG.astype(int)

    minHashingExperimentation(inputThreshold, NUM_OF_SIGNATURES, SIG, inputNumOfMoviesToCompare)

    LSHExperimentation(inputNumOfMoviesToCompare, inputThreshold, SIG)

    plt.show()

# Call main as the first access point
main()









