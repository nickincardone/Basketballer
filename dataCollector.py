import urllib2
import json
import sys
import os

#constants

#edit dates to get games you want
dates = ["20140419","20140422","20140424","20140426","20140428","20140501","20140503"]
team1 = "01"
team2 = "11"

#example=http://www.cbssports.com/nba/gametracker/shotchart/NBA_20140117_GS@OKC
#cbsShotchartUrl = 'http://www.cbssports.com/nba/gametracker/shotchart/NBA_'+str(date)+'_'
#example=http://www.cbssports.com/nba/scoreboard/20140117
cbsScorboardUrl = 'http://www.cbssports.com/nba/scoreboard/'
homePlayers = {}
awayPlayers = {}
gameId = ""

apiUrl = "http://api.nba.onetwosee.com/update/" #append date 20140419 and home team id


#teams and there respective ids
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
	"GS":  "09",
	"HOU": "10",
	"IND": "11",
	"LAC": "12",
	"LAL": "13",
	"MEM": "29",
	"MIA": "14",
	"MIL": "15",
	"MIN": "16",
	"NO":  "03",
	"NY":  "18",
	"OKC": "25",
	"ORL": "19",
	"PHI": "20",
	"PHO": "21",
	"POR": "22",
	"SAC": "23",
	"SA":  "24",
	"TOR": "28",
	"UTA": "26",
	"WAS": "27"
}

def getDaysGames(date):
	games = []
	#opens the cbs sports nba scoreboard for the date
	cbs_scoreboard = urllib2.urlopen(cbsScorboardUrl  + str(date))
	html = cbs_scoreboard.read()
	cbs_scoreboard.close()

	#print html

	#initializes loc1 to first game of the day
	loc1 = html.find("recap/NBA_"+str(date)+"_")+19

	#loops over all the games to extract the teams playing
	#stops at 18 because I am adding 19 to the beginning of the
	#string I am trying to find to get the string I want, so
	#if the string doesn't exist it will return -1 + 19 = 18
	while loc1 != 18:
		loc2 = loc1 + 7

		#this is a raw string of the two teams abbreviations playing a game
		temp = html[loc1:loc2]
		
		#this loop takes care of shorter team abbr like NO@SA
		for x in range(3,len(temp)):
			if temp[x] == '"':
				temp = temp[0:x]
		
		#adds the game to the global game list
		games.append(temp)

		#sets loc1 to the next game instance
		loc1 = html.find("recap/NBA_"+str(date)+"_",loc2)+19

	return games

def do():
	if not os.path.exists("games"):
		os.makedirs("games")

	for date in dates:
		gameList = getDaysGames(date)
		for game in gameList:
			if teamDict[game[game.find("@")+1:]] == team1 or teamDict[game[game.find("@")+1:]] == team2:
				print "here"
				gameId = date + teamDict[game[game.find("@")+1:]]
				try:	
					bloop = urllib2.urlopen(apiUrl + gameId)
					html = bloop.read()
					bloop.close()

					#tempUrl.close()
				except urllib2.HTTPError, e:
				    print e.code
				    print e.msg
				    print e.headers
				    print e.fp.read()


				
				f=open("games/" + gameId + ".json","w")
				f.write(html)
				f.close()

if __name__ == "__main__":
    print "main running in csvToJson.py"
    do()
