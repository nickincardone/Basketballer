import json
import os

folderName = "games"
listOfGames = []
masterDict = []
players = {}
quarterStarters = []
final = {}
hawks = []
pacers = []


def main():
	global masterDict

	getGames()
	#TODO see if list is empty or if something invalid
	#for game in listOfGames:
	#	convert(game)
	for game in listOfGames:
		playByPlay = scrub(game)
		quarterStarters = getSubs(playByPlay, game[-7:len(game)-5])
		convert(playByPlay, quarterStarters, game[-7:len(game)-5])

	finalize()


	for player in players.keys():
		with open(player +'.json', 'w') as outfile:
	  			json.dump(final[player], outfile)

	with open('hawks.json', 'w') as outfile:
	  			json.dump(hawks, outfile)
	with open('pacers.json', 'w') as outfile:
	  			json.dump(pacers, outfile)

	#convertToFiles()
	#convert(listOfGames)
	#convert(playByPlay, listOfGames[0][-7:len(listOfGames[0])-5])




def finalize():
	for player in players.keys():
		final[player] = []
	for shot in masterDict:
		final[shot["player"]["id"]].append(shot)
		if (shot["team"] == 1):
			hawks.append(shot)
		else:
			pacers.append(shot)


	

def getGames():
	#creates a list of all the games in the file
	#folderName is the date you want to convert to json
	global listOfGames
	listOfGames = os.listdir("./" + folderName)
	print str(listOfGames)

#gets the substitutions at the start of each quarter
#the play by play only has the starting lineup and doesn't include subs between quarters
def getSubs(pbp, homeTeamId):
	global masterDict
	global quarterStarters

	index = 0
	homePlayers = {}
	awayPlayers = {}
	curHome = []
	curAway = []
	homeTeam = homeTeamId
	quarterEnders = []
	quarterIndex = []

	currentQuarter = 1
	for x in range(0,len(pbp)):

		if (int(pbp[x]["event-id"]) == 15):
			quarterIndex[currentQuarter-1][1] = x
			currentQuarter += 1

		if (int(pbp[x]["event-id"]) == 14):
			quarterStarters.append([[],[]])
			quarterIndex.append([0,0])
			#print "quarter " + str(currentQuarter)
			#print "blah " + str(quarterIndex)
			quarterIndex[currentQuarter-1][0] = x



		if (pbp[x]["global-player-id-1"] not in players):

			if (int(pbp[x]["team-code-1"]) == int(homeTeam)):
				homePlayers[pbp[x]["global-player-id-1"]] = pbp[x]["first-name-1"] + " " + pbp[x]["last-name-1"]
				players[pbp[x]["global-player-id-1"]] = pbp[x]["first-name-1"] + " " + pbp[x]["last-name-1"]
			else:
				awayPlayers[pbp[x]["global-player-id-1"]] = pbp[x]["first-name-1"] + " " + pbp[x]["last-name-1"]
				players[pbp[x]["global-player-id-1"]] = pbp[x]["first-name-1"] + " " + pbp[x]["last-name-1"]



	#gets starting lineup
	#only quarter given
	for x in range(10):

		#makes sures theres nothing fishy
		if (pbp[x]["textual-description"] != "Starting Lineup"):
			print "Some Error"
			continue
		#print x

		#see if on home team else away team
		if (int(pbp[x]["team-code-1"]) == int(homeTeam)):
			curHome.append(pbp[x]["global-player-id-1"])
		else:
			#on away team
			#puts player in on court array
			curAway.append(pbp[x]["global-player-id-1"])

	for x in curHome:
		quarterStarters[0][0].append(x)
	for x in curAway:
		quarterStarters[0][1].append(x)



	

	for x in range(11,quarterIndex[0][1]):
		if (int(pbp[x]["event-id"]) == 10):
			#subsitituion 
			oldPlayer = pbp[x]["global-player-id-2"]
			newPlayer = pbp[x]["global-player-id-1"]
			#checks to see if in players
			if (newPlayer not in players):
				players[newPlayer] = pbp[x]["first-name-1"] + " " + pbp[x]["last-name-1"]
			if (int(pbp[x]["team-code-1"]) == int(homeTeam)):
				#on home team
				curHome[curHome.index(oldPlayer)] = newPlayer
			else:
				#on away team
				curAway[curAway.index(oldPlayer)] = newPlayer
			continue
	

	i = 1
	print "quarterIndex " + str(quarterIndex)
	for y in quarterIndex[1:]:
		quarterStarters[i] = getQuarterStarters(pbp[y[0]:y[1]], [curHome,curAway], homeTeamId)
		#print "quarter: " + str(i+1)
		#print "quarterStarters "
		#for x in quarterStarters[i][0]:
			#print players[x]
		curHome = quarterStarters[i][0][:]
		curAway = quarterStarters[i][1][:]
		#print "quarter starters " + str(quarterStarters)
		#print "home " + str(curHome)
		for x in pbp[y[0]:y[1]]:

			if (int(x["event-id"]) == 10):
				#subsitituion 
				oldPlayer = x["global-player-id-2"]
				newPlayer = x["global-player-id-1"]
				#checks to see if in players
				if (newPlayer not in players):
					players[newPlayer] = x["first-name-1"] + " " + x["last-name-1"]
				if (int(x["team-code-1"]) == int(homeTeam)):
					#on home team
					#print str(x)
					curHome[curHome.index(oldPlayer)] = newPlayer
				else:
					#on away team
					curAway[curAway.index(oldPlayer)] = newPlayer
		i += 1
	



	return quarterStarters, homePlayers, awayPlayers, players
	


	


def getQuarterStarters(pbp, curPlayers, homeTeamId):

	curHome = curPlayers[0][:]
	curAway = curPlayers[1][:]

	startHome = []
	startAway = []

	subbedInPlayers = []

	#if (pbp[0]["quarter"] == "2"):
	#	i = 116
	#	for y in curHome:
	#		print players[y]
	#else:
	#	i = -2000
	



	
	for x in pbp:
		#print x["textual-description"]
		#sub
		#TODO check if already been sub for

		#if (i>0):
			#print x["textual-description"]
		if (int(x["event-id"]) == 10):
			oldPlayer = x["global-player-id-2"]
			newPlayer = x["global-player-id-1"]
			#checks to see if in players
			
			subbedInPlayers.append(newPlayer)
			if (x["global-player-id-2"] not in startHome and x["global-player-id-2"] not in startAway):
				if (x["global-player-id-2"] not in subbedInPlayers):
					if (int(x["team-code-1"]) == int(homeTeamId)):
						#on home team
						startHome.append(x["global-player-id-2"])
						#print "in here"
						#print "homePlayer added:" + players[x["global-player-id-2"]]
						
					else:
						#print "in here"
						startAway.append(x["global-player-id-2"])
						#print "awayPlayer added:" + players[x["global-player-id-2"]]
					
				continue




			#if (int(x["team-code-1"]) == int(homeTeamId)):
			#	#on home team
			#	curHome[curHome.index(oldPlayer)] = newPlayer
			#else:
			#	#on away team
			#	curAway[curAway.index(oldPlayer)] = newPlayer


		if (x["global-player-id-1"] not in startHome and x["global-player-id-1"] not in startAway):
			if (x["global-player-id-1"] == ""):
				continue
			if (x["global-player-id-1"] not in subbedInPlayers):
				if (int(x["team-code-1"]) == int(homeTeamId)):
					#on home team
					startHome.append(x["global-player-id-1"])
					#print "homePlayer added:" + players[x["global-player-id-1"]]
				else:
					startAway.append(x["global-player-id-1"])
					#print "awayPlayer added:" + players[x["global-player-id-1"]]


		if (len(startAway) == 5 and len(startHome) == 5):
			break
	


	if (int(pbp[0]["quarter"]) == 2):
		print "quarter 2222"
		for y in startHome:
			print players[y]
	print (pbp[0]["quarter"])
	print "returning"
	for x in startHome:
		print players[x]
	return [startHome,startAway]








def scrub(game):
	global masterDict

	#f = open("./" + folderName + "/" + game)
	#shots = f.readlines()
	#f.close()
	with open("./" + folderName + "/" + game) as data_file:
		data = json.load(data_file)

	jsonDict = {}
	jsonHomeDict = {}
	jsonAwayDict = {}

	play = data["pbp"]["sports-scores"]["nba-scores"]["nba-playbyplay"]["play"]
	return play


def convert(pbp, quarterStarters, homeTeamId):
	index = 0 #index of the current play
	players = quarterStarters[3]
	homePlayers = quarterStarters[1]
	awayPlayers = quarterStarters[2]
	curHome = []
	curAway = []
	homeTeam = homeTeamId
	shots = []
	qs = quarterStarters[0]
	
	#first 10 plays are starting lineup

	#for x in range(10):
	#	if (pbp[x]["textual-description"] != "Starting Lineup"):
	#		print "Not Starting lineup"
	#		continue
	#	#print x
#
#	#	#see if on home team else away team
#	#	if (int(pbp[x]["team-code-1"]) == int(homeTeam)):
#	#		#on home team
#
#	#		#puts the player in teams dict id:name
#	#		homePlayers[pbp[x]["global-player-id-1"]] = pbp[x]["first-name-1"] + " " + pbp[x]["last-name-1"]
#	#		players[pbp[x]["global-player-id-1"]] = pbp[x]["first-name-1"] + " " + pbp[x]["last-name-1"]
#	#		#puts player in on court array
#	#		curHome.append(pbp[x]["global-player-id-1"])
#	#	else:
#	#		#on away team
#
#	#		#puts the player in teams dict id:name
#	#		awayPlayers[pbp[x]["global-player-id-1"]] = pbp[x]["first-name-1"] + " " + pbp[x]["last-name-1"]
#	#		players[pbp[x]["global-player-id-1"]] = pbp[x]["first-name-1"] + " " + pbp[x]["last-name-1"]
#	#		#puts player in on court array
	#		curAway.append(pbp[x]["global-player-id-1"])

	#start of game
	index = 10
	print str(qs)
	b = 1
	for y in qs:
		print "quarterrr:" + str(int(b))
		for j in y[0]:
			print players[j]
		b += 1


	for x in range(10,len(pbp)):
		#checks to see if shot, event id is 3 for make 4 for miss
		event = {}
		#print x
		#if (x == 11):
		#	for y in curHome:
		#		print players[y]

		if (int(pbp[x]["event-id"]) == 14):
			quarter = int(pbp[x]["quarter"])
			curHome = qs[quarter-1][0]
			curAway = qs[quarter-1][1]

		if (x == 116):
			for y in curHome:
				print players[y]

		if (int(pbp[x]["event-id"]) == 3):
			#TODO made shot

			#player info
			event["player"] = {}
			event["player"]["id"] = pbp[x]["global-player-id-1"]
			event["player"]["name"] =  players[pbp[x]["global-player-id-1"]]

			event["team"] = int(pbp[x]["team-code-1"])

			#shot info
			event["shot"] = {}

			event["shot"]["xCord"] = int(float(pbp[x]["x-shot-coord"]) * 10)
			event["shot"]["yCord"] = int(float(pbp[x]["y-shot-coord"]) * 10 + 30)

			event["shot"]["time"] = {}
			event["shot"]["time"]["quarter"] = int(pbp[x]["quarter"])
			event["shot"]["time"]["min"] = int(pbp[x]["time-minutes"])
			event["shot"]["time"]["sec"] = float(pbp[x]["time-seconds"])

			#0=missed 1=made free throw 2=made two 3=made three
			event["shot"]["result"] = pbp[x]["points-type"]

			#event["shot"]["assist"] = {}
			#event["shot"]["assist"]["assisted"]
			#event["shot"]["assist"]["teammate"] = {}
			#event["shot"]["assist"]["teammate"]["id"] 
			#event["shot"]["assist"]["teammate"]["name"]

			#event["shot"]["blocked"] 

			event["teammates"] = []
			event["opponents"] = []

			if (int(pbp[x]["team-code-1"]) == int(homeTeam)):
				#on home team
				for y in curHome:
					tm = {}
					#checks to see if teammate is himself
					if(y != pbp[x]["global-player-id-1"]):
						tm["id"] = y
						tm["name"] = players[y]
						event["teammates"].append(tm)
				for y in curAway:
					op = {}
					op["id"] = y
					op["name"] = players[y]
					event["opponents"].append(op)
			else:
				#on away team
				for y in curAway:
					tm = {}
					#checks to see if teammate is himself
					if(y != pbp[x]["global-player-id-1"]):
						tm["id"] = y
						tm["name"] = players[y]
						event["teammates"].append(tm)
				for y in curHome:
					op = {}
					op["id"] = y
					op["name"] = players[y]
					event["opponents"].append(op)
			shots.append(event)

			#teammates on court

			#opponents on court

			continue
		if (int(pbp[x]["event-id"]) == 4):
			#TODO missed shot
			#TODO made shot

			#player info
			event["player"] = {}
			event["player"]["id"] = pbp[x]["global-player-id-1"]
			event["player"]["name"] =  players[pbp[x]["global-player-id-1"]]

			#shot info
			event["shot"] = {}

			event["team"] = int(pbp[x]["team-code-1"])

			event["shot"]["xCord"] = int(float(pbp[x]["x-shot-coord"]) * 10)
			event["shot"]["yCord"] = int(float(pbp[x]["y-shot-coord"]) * 10 + 30)

			event["shot"]["time"] = {}
			event["shot"]["time"]["quarter"] = int(pbp[x]["quarter"])
			event["shot"]["time"]["min"] = int(pbp[x]["time-minutes"])
			event["shot"]["time"]["sec"] = float(pbp[x]["time-seconds"])

			#0=missed 1=made free throw 2=made two 3=made three
			event["shot"]["result"] = 0

			#event["shot"]["assist"] = {}
			#event["shot"]["assist"]["assisted"]
			#event["shot"]["assist"]["teammate"] = {}
			#event["shot"]["assist"]["teammate"]["id"] 
			#event["shot"]["assist"]["teammate"]["name"]

			#event["shot"]["blocked"] 

			event["teammates"] = []
			event["opponents"] = []

			if (int(pbp[x]["team-code-1"]) == int(homeTeam)):
				#on home team
				for y in curHome:
					tm = {}
					#checks to see if teammate is himself
					if(y != pbp[x]["global-player-id-1"]):
						tm["id"] = y
						tm["name"] = players[y]
						event["teammates"].append(tm)
				for y in curAway:
					op = {}
					op["id"] = y
					op["name"] = players[y]
					event["opponents"].append(op)
			else:
				#on away team
				for y in curAway:
					tm = {}
					#checks to see if teammate is himself
					if(y != pbp[x]["global-player-id-1"]):
						tm["id"] = y
						#print str(players)
						tm["name"] = players[y]
						event["teammates"].append(tm)
				for y in curHome:
					op = {}
					op["id"] = y
					op["name"] = players[y]
					event["opponents"].append(op)
			shots.append(event)

			continue


		if (int(pbp[x]["event-id"]) == 10):
			#subsitituion 
			oldPlayer = pbp[x]["global-player-id-2"]
			#print players[oldPlayer]
			newPlayer = pbp[x]["global-player-id-1"]
			#checks to see if in players
			if (newPlayer not in players):
				players[newPlayer] = pbp[x]["first-name-1"] + " " + pbp[x]["last-name-1"]
			if (int(pbp[x]["team-code-1"]) == int(homeTeam)):
				#on home team
				curHome[curHome.index(oldPlayer)] = newPlayer
			else:
				#on away team
				curAway[curAway.index(oldPlayer)] = newPlayer
			continue

			


	#print str(homePlayers)
	#print str(awayPlayers)
	#print str(curHome)
	#print str(curAway)
	#print str(shots)
	for x in players.keys():
		print x + ":" + players[x]
	
  	masterDict.extend(shots)





if __name__ == "__main__":
    print "main running in csvToJson.py"
    main()


#event ids
#0
#1 
#2
#3 made shot
#4 missed shot
#5
#6
#7
#8
#9
#10 substitution
#11
#12
#13
#14 start period
#15 end period