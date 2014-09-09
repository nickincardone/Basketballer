import urllib2
import os

# constants

# dates of playoff games
dates = [
    "20140419", "20140420", "20140421", "20140422", "20140424", "20140425",
    "20140426", "20140427", "20140428", "20140429", "20140430", "20140501",
    "20140502", "20140503", "20140504", "20140505", "20140506", "20140507",
    "20140508", "20140509", "20140510", "20140511", "20140512", "20140513",
    "20140514", "20140515", "20140518", "20140519", "20140520", "20140521",
    "20140524", "20140525", "20140526", "20140527", "20140528", "20140529",
    "20140530", "20140531", "20140605", "20140608", "20140610", "20140612",
    "20140615"]

cbsScorboardUrl = 'http://www.cbssports.com/nba/scoreboard/'
gameId = ""

# append date 20140419 and home team id
apiUrl = "http://api.nba.onetwosee.com/update/"


# teams and there respective ids
teamDict = {
    "ATL": "01",
    "BOS": "02",
    "BKN": "17",
    "CHA": "30",
    "CHI": "04",
    "CLE": "05",
    "DAL": "06",
    "DEN": "07",
    "DET": "08",
    "GS": "09",
    "HOU": "10",
    "IND": "11",
    "LAC": "12",
    "LAL": "13",
    "MEM": "29",
    "MIA": "14",
    "MIL": "15",
    "MIN": "16",
    "NO": "03",
    "NY": "18",
    "OKC": "25",
    "ORL": "19",
    "PHI": "20",
    "PHO": "21",
    "POR": "22",
    "SAC": "23",
    "SA": "24",
    "TOR": "28",
    "UTA": "26",
    "WAS": "27"
}


def getDaysGames(date):
    games = []
    # opens the cbs sports nba scoreboard for the date
    cbs_scoreboard = urllib2.urlopen(cbsScorboardUrl + str(date))
    html = cbs_scoreboard.read()
    cbs_scoreboard.close()

    # print html

    # initializes loc1 to first game of the day
    loc1 = html.find("recap/NBA_" + str(date) + "_") + 19

    # loops over all the games to extract the teams playing
    # stops at 18 because I am adding 19 to the beginning of the
    # string I am trying to find to get the string I want, so
    # if the string doesn't exist it will return -1 + 19 = 18
    while loc1 != 18:
        loc2 = loc1 + 7

        # this is a raw string of the two teams abbreviations playing a game
        temp = html[loc1:loc2]

        # this loop takes care of shorter team abbr like NO@SA
        for x in range(3, len(temp)):
            if temp[x] == '"':
                temp = temp[0:x]

        # adds the game to the global game list
        games.append(temp)

        # sets loc1 to the next game instance
        loc1 = html.find("recap/NBA_" + str(date) + "_", loc2) + 19

    return games


def do():
    if not os.path.exists("games"):
        os.makedirs("games")

    for date in dates:
        gameList = getDaysGames(date)
        for game in gameList:

            gameId = date + teamDict[game[game.find("@") + 1:]]
            try:
                shotJsonData = urllib2.urlopen(apiUrl + gameId)
                html = shotJsonData.read()
                shotJsonData.close()
            except urllib2.HTTPError, e:
                print e.code
                print e.msg
                print e.headers
                print e.fp.read()

            f = open("games/" + gameId + ".json", "w")
            f.write(html)
            f.close()

if __name__ == "__main__":
    print "running scraper function"
    do()
