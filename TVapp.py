# Created by Ryan van Huuksloot
# Current Version: Version 3


############################################################
#   This section is for imports.
############################################################
import os
import json
import urllib
from pprint import pprint
import contextlib
import datetime
import time
############################################################

# Insert API Key here between quotations
api_key = "7c6236e26fc916c4b61a16869aed366d"

############################################################

###########################################################
#   This section is for Object Oriented Programming.
###########################################################
class Show:

    def __init__(self, id_tag, name, currentSeason, currentEpisode):
        """This function stores object variables."""
        self.name = name
        self.id_tag = id_tag
        self.currentSeason = currentSeason
        self.currentEpisode = currentEpisode

    def retrieveActualStatistics(self):
        """This function retrieves the latest season and episode number from the movie database."""
        url_TMDB = mergeURL_ID(self.id_tag)
        JSONText = readWebPage(url_TMDB)
        today = datetime.date.today().isoformat()
        self.actualSeason = JSONText["number_of_seasons"]
        i = 0
        for item in JSONText["seasons"]:
            if item["air_date"] <= today and item["air_date"] != None and item["season_number"] != 0:
                i += 1
        self.actualSeason = i
        if JSONText["status"] == "Returning Series":
            returning = True
        elif JSONText["status"] == "Canceled":
            returning = False
            print "Cancelled : " + JSONText["name"]
        else:
            returning = False
        url_TMDB = mergeURL_ID_Season(self.id_tag, self.actualSeason)
        JSONText = readWebPage(url_TMDB)
        self.actualEpisode = 1
        for item in JSONText["episodes"]:
            if item["air_date"] <= today and item["air_date"] != None:
                self.actualEpisode = item["episode_number"]
                try:
                    self.actualEpisode = JSONText["episodes"][self.actualEpisode]["episode_number"]
                except IndexError:
                    if returning:
                        self.actualEpisode += 1

    def compareStatistics(self):
        """This function compares the statistics of the shows that have been added to data to the
        movie database and returns the episode that you have to watch."""
        check = True
        while check:
            if int(self.currentSeason) == self.actualSeason:
                if int(self.currentEpisode) < self.actualEpisode:
                    print self.displayToWatch()
                check = False
            #change checkEpisode
            elif int(self.currentSeason) < self.actualSeason:
                if checkEpisode(self.id_tag, self.currentSeason, self.currentEpisode):
                    print self.displayToWatch()
                    check = False
                else:
                    self.currentSeason = int(self.currentSeason) + 1
                    self.currentEpisode = 1
##                url_TMDB = mergeURL_ID_Season(self.id_tag, self.currentSeason)
##                JSONText = readWebPage(url_TMDB)
##                today = datetime.date.today().isoformat()
##                for item in JSONText["episodes"]:
##                    if item["air_date"] <= today and item["air_date"] != None:
##                        tempEpisode = item["episode_number"]
##                if self.currentEpisode <= tempEpisode:
##                    print self.displayToWatch()
##                    check = False
##                else:
##                    self.currentSeason = int(self.currentSeason) + 1
##                    self.currentEpisode = 1
##                    filename = os.path.abspath(os.path.join("data\shows", self.id_tag))+".json"
##                    updateJSONFile(filename, self.id_tag)
            else:
                check = False

    def watched(self):
        self.currentEpisode = int(self.currentEpisode) + 1
        self.compareStatistics()
        filename = os.path.abspath(os.path.join("data\shows", self.id_tag))+".json"
        updateJSONFile(filename, self.id_tag)

    def displayToWatch(self):
        """This function displays the current season and episode you have to watch."""
        return "ID : " + str(self.id_tag) + " Name : " + self.name + " Season : " + str(self.currentSeason) + " Episode : " + str(self.currentEpisode)

    def displayShowCurrent(self):
        """This function displays the current season and episode you are on."""
        return self.name + " [" + str(self.currentSeason) + "|" + str(self.currentEpisode) + "]"

    def displayShowActual(self):
        """This function displays the actual season and episode that the show is on."""
        return self.name + " [" + str(self.actualSeason) + "|" + str(self.actualEpisode) + "]"
###########################################################
#   End of Object Oriented Programming Section.
###########################################################


###########################################################
#   This section is for JSON File Manipulation.
###########################################################
def updateJSONFile(filename, id_tag = 1):
    """This function updates the JSON files that stores all of the data."""
    JSONFile = open(filename, "r")
    data = json.load(JSONFile)
    JSONFile.close()

    if id_tag != 1:
        data["currentEpisode"] = Shows[id_tag].currentEpisode
        data["currentSeason"] = Shows[id_tag].currentSeason

    JSONFile = open(filename, "w+")
    JSONFile.write(json.dumps(data))
    JSONFile.close()

def readJSONFile(filename):
    """This function reads the data from the JSON files."""
    JSONFile = open(filename, "r")
    data = json.load(JSONFile)
    JSONFile.close()
    return data

def writeJSONFile(id_tag, data):
    filename = os.path.abspath(os.path.join("data\shows", id_tag))+".json"
    jsonFile = open(filename, "w+")
    jsonFile.write(json.dumps(data))
    jsonFile.close()
###########################################################
#   End of JSON File Manipulation Section.
###########################################################

Shows = {}
def main():
    try:
        print "Updating your TV Shows. One moment please!"
        print "="*50
        i = 0
        for filename in os.listdir('data\shows'):
            if i == 20:
                time.sleep(5.5)
                i = 0
            else:
                i+=1
            filename = os.path.abspath(os.path.join("data\shows", filename))
            data = readJSONFile(filename)
            id_tag = data["id_tag"]
            name = data["name"]
            currentSeason = data["currentSeason"]
            currentEpisode = data["currentEpisode"]
            Shows[id_tag] = Show(id_tag, name, currentSeason, currentEpisode)
            try:
                Shows[id_tag].retrieveActualStatistics()
            except KeyError:
                pass
            try:
##                print Shows[id_tag].displayShowCurrent(), Shows[id_tag].displayShowActual()
                Shows[id_tag].compareStatistics()
            except AttributeError:
                pass
        print "All your shows are updated!"
        print "="*50
        check = True
        print "Which episodes have you watched? Input the ID Number one at a time. Type Esc to escape."
        while check:
            checkWatched = raw_input("ID Number : ").title()
            if checkWatched == "Esc":
                check = False
            elif checkWatched.isdigit():
                try:
                    Shows[checkWatched].watched()
                except KeyError:
                    print "You didn't enter a valid ID!"
    except IOError:
        print "You currently don't have internet. Try again once you have internet!"


def RyanUpdate():
    """This function takes the data from a txt file in a very specific format and creates a
    JSON structure for the data within data coding the files based on their id_tag. The function
    then updates and compares the statistics."""
    file_name = "shows.txt"
    full_file = os.path.abspath(os.path.join("data", file_name))
    content = readData(full_file)
    print "Updating your TV Shows. One moment please!"
    for item in content:
        id_tag = item[:item.index(":")-1]
        name = item[item.index(":")+2:item.index("[")-1]
        currentSeason = item[item.index("[")+1:item.index("|")]
        currentEpisode = item[item.index("|")+1:item.index("]")]

        data = {"id_tag":id_tag, "name":name, "currentSeason":currentSeason, "currentEpisode":currentEpisode}
        writeJSONFile(id_tag, data)

        Shows[id_tag] = Show(id_tag, name, currentSeason, currentEpisode)
        Shows[id_tag].retrieveActualStatistics()
        Shows[id_tag].compareStatistics()
    print "All your shows have been updated!"


def readData(filename):
    """This function opens and read the file required to get all the data to make the bingo cards (the individual items that will be called later.
These items are added to an allData database."""
    fileIn = open(filename, 'r')
    allData = []
    line = fileIn.readline().strip()
    while line != "":
        # Checks to make sure the line isn't empty
        if line != "":
              allData.append(line)
        line = fileIn.readline().strip()
    fileIn.close()
    return allData

def writeData(filename, data):
    """This function opens and writes to the file specified."""
    fileIn = open(filename, 'w')
    for item in data:
        fileIn.write(item + " : " + data[item])
    fileIn.close()
    print "ids are written to target location"

###########################################################
#   This section is for merging URLS.
###########################################################
def mergeURL_Search(name, page=1):
    """This function takes a TV show name and a page number if provided and returns the
    corresponding TMDB url."""
    url_TMDB = "http://api.themoviedb.org/3/search/tv?api_key="
    url_query = "&query="
    url_page = "&page="
    return (url_TMDB + str(api_key) + url_query + name + url_page + str(page))

def mergeURL_ID(id_tag):
    """This function takes a TV show id and returns the basic url."""
    url_TMDB = "http://api.themoviedb.org/3/tv/"
    url_api = "?api_key="
    return (url_TMDB + str(id_tag) + url_api + str(api_key))

def mergeURL_ID_Season(id_tag, season):
    """This function takes a TV show id and season and returns the basic url including season."""
    url_TMDB = "http://api.themoviedb.org/3/tv/"
    url_season = "/season/"
    url_api = "?api_key="
    return (url_TMDB + str(id_tag) + url_season + str(season) + url_api + str(api_key))
############################################################
#   End of merging URLs section.
############################################################

def readWebPage(url_TMDB):
    with contextlib.closing(urllib.urlopen(url_TMDB)) as htmlFileIn:
        JSONText = json.load(htmlFileIn)
    return JSONText

def chooseShow(name):
    """This function allows the user to view all of the results of the url search and choose
    which TV show is the correct one based on the search parameter name.
    This function returns the name and the TMDB id tag."""
    url_TMDB = mergeURL_Search(name)
    singlePage = False
    while not singlePage:
        JSONText = readWebPage(url_TMDB)
        i = 0
        for item in JSONText["results"]:
            print "="*50
            print item["name"]
            if item["overview"] != "":
                print "-"*len(item["name"])
                print item["overview"]
                print "="*50
            userInput = raw_input("Is this your show? (Y/N): ").upper()
            if userInput == "Y":
                return item["name"], item["id"]
            i += 1
        if i == 20 and (int(JSONText["page"]) < int(JSONText["total_pages"])):
            url_TMDB = mergeURL_Search(name, int(JSONText["page"]) + 1)
            singlePage = False
        else:
            singlePage = True
            return "name", "id"

def checkSeason(id_tag, season):
    url_TMDB = mergeURL_ID(id_tag)
    JSONText = readWebPage(url_TMDB)
    if JSONText["number_of_seasons"] >= int(season):
        return True, False
    elif (JSONText["number_of_seasons"] + 1) == int(season) and JSONText["status"] == "Returning Series":
        return True, True
    else:
        return False, False


def checkEpisode(id_tag, season, episode):
    url_TMDB = mergeURL_ID(id_tag)
    JSONText = readWebPage(url_TMDB)
    try:
        if JSONText["seasons"][int(season)-1]["episode_count"] >= int(episode):
            return True
        else:
            return False
    except KeyError:
        pass

def addShow():
    """This function adds a TV show to your current list of TV shows."""
    # Checks TV Show name
    nameOK = False
    while not nameOK:
        name, id_tag = chooseShow(str(raw_input("Name of the show: ")).title())
        if name != "name" and id_tag != "id":
            nameOK = True
        else:
            print "You didn't enter a valid show name or we could not find your TV show."
    # Checks to make sure that the show has this valid season
    seasonOK = False
    while not seasonOK:
        season = raw_input("What season are you currently on: ")
        if season.isdigit() and int(season) > 0:
            seasonOK, newSeason = checkSeason(id_tag, season)
            if not seasonOK:
                print "You didn't enter a valid season silly!"
        else:
            print "You didn't enter a valid number."
    # Checks to make sure that the TV show has this valid episode in this season
    if newSeason:
        episode = 1
        print "You are on a new season. You will start with episode 1 when it comes out!"
    else:
        episodeOK = False
        while not episodeOK:
            episode = raw_input("What episode are you currently on: ")
            if episode.isdigit():
                episodeOK = checkEpisode(id_tag, season, episode)
                if not episodeOK:
                    print "You didn't enter a valid episode number."
            else:
                print "You didn't enter a valid episode number."
    data = {"id_tag":str(id_tag), "name":name, "currentSeason":season, "currentEpisode":episode}
    writeJSONFile(str(id_tag), data)

def removeShow():
    nameOK = False
    while not nameOK:
        name, id_tag = chooseShow(str(raw_input("Name of the show: ")).title())
        if name != "name" and id_tag != "id":
            nameOK = True
        else:
            print "You didn't enter a valid show name or we could not find your TV show."
    filename = str(id_tag) + ".json"
    filename = os.path.abspath(os.path.join("data\shows", filename))
    os.remove(filename)

main()
