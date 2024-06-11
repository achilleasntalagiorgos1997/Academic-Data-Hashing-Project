#!/usr/bin/python3.8

import sys, csv
from pathlib import Path


# Command-line input check
if len(sys.argv) != 2:
    print("Invalid number of arguments.\nPlease, type 'python preprocess.py <name>.csv'. \n")
    exit()

inputFileName = sys.argv[1]
inputFileNameSplit = inputFileName.split(".")
userList = {}
movieMap = {}
movieList = {}

# One pass of csv file
with open(inputFileName) as csvFile:
    csvReader = csv.reader(csvFile, delimiter=',')
    lineCounter = 0
    movieCounter = 0
        
    for row in csvReader:
        lineCounter += 1

        if lineCounter == 1:
            print("Columns names are: {}\n".format(row))
        else:
            # If userId row[0] not in userList, put a new entry
            # with key: userId, value: empty list
            if row[0] not in userList:
                userList[row[0]] = []

            # Append movieId row[1] to user's list of movies
            userList[row[0]].append(row[1])

            # If movieId row[1] not in movieMap, put a new entry
            # with key: movieId, value: next sequence number (movieCounter)
            if row[1] not in movieMap:
                movieCounter += 1
                movieMap[row[1]] = movieCounter

            # If movieId row[1] not in movieList, put a new entry
            # with key: movieId, value: empty list
            if row[1] not in movieList:
                movieList[row[1]] = []

            # Append userId row[0] to movie's list of users
            movieList[row[1]].append(row[0])

    print("{} lines were processed from file '{}'\n".format(lineCounter, inputFileName))

# Export dictionaries in csv files
pathStr = "../EXPERIMENTS/" + inputFileNameSplit[0] + "_user_list.csv"
path = Path(__file__).parent / pathStr
with path.open(mode = 'w', newline = '') as user_list_file:
    user_list_writer = csv.writer(user_list_file, delimiter = ',')

    user_list_writer.writerow(["userId", "moviesIds"])

    for entry in userList:
        rowToWrite = [entry] + userList[entry]
        
        user_list_writer.writerow(rowToWrite)

pathStr = "../EXPERIMENTS/" + inputFileNameSplit[0] + "_movie_map.csv"
path = Path(__file__).parent / pathStr
with path.open(mode = 'w', newline = '') as movie_map_file:
    movie_map_writer = csv.writer(movie_map_file, delimiter = ',')

    movie_map_writer.writerow(["movieId", "SequenceNumber"])

    for entry in movieMap:
        movie_map_writer.writerow([entry, movieMap[entry]])


pathStr = "../EXPERIMENTS/" + inputFileNameSplit[0] + "_movie_list.csv"
path = Path(__file__).parent / pathStr
with path.open(mode = 'w', newline = '') as movie_list_file:
    movie_list_writer = csv.writer(movie_list_file, delimiter = ',')

    movie_list_writer.writerow(["movieId", "usersIds"])

    for entry in movieList:
        rowToWrite = [entry] + movieList[entry]

        movie_list_writer.writerow(rowToWrite)







