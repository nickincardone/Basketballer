import os
import json

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


def main():
    listOfGames = os.listdir("./games")
    if ".DS_Store" in listOfGames:
        listOfGames.remove(".DS_Store")
    for game in listOfGames:
        gameData = getData(game)
        shotData = getShotData(gameData)


def getData(game):
    with open("./games/" + game) as data_file:
        data = json.load(data_file)
    data["pbp"] = data["pbp"]["sports-scores"][
        "nba-scores"]["nba-playbyplay"]["play"]
    return data


def getShotData(gameData):
    shotData = {}
    shotData["players"] = {}
    shotData["teams"] = {}

    shotData["players"]["home"], shotData[
        "players"]["away"] = getPlayers(gameData)
    shotData["date"] = gameData["gameInfo"]["local-game-date"]
    shotData["teams"]["home"] = gameData["personalInfo"][
        "home_team"]["team-code"]["global-id"]
    shotData["teams"]["away"] = gameData["personalInfo"][
        "away_team"]["team-code"]["global-id"]

    shotData["pbp"] = []

    numOfQuarters = int(gameData["gameInfo"]["total-quarters"]["total"])

    playIndex = 0
    for quarter in range(numOfQuarters):
        quarterStarters = getQuarterStarters(
            quarter, gameData, shotData, playIndex)
        quarterShotData, playIndex = getQuarterData(quarterStarters, gameData['pbp'][playIndex:])
        shotData['pbp'].append(quarterShotData)


def getPlayers(gameData):
    homeTeam = []
    awayTeam = []

    for playerData in gameData["personalInfo"]["home_team"]["nba-player"]:
        homeTeam.append(playerData["player-code"]["global-id"])

    for playerData in gameData["personalInfo"]["away_team"]["nba-player"]:
        awayTeam.append(playerData["player-code"]["global-id"])

    return homeTeam, awayTeam


def getQuarterStarters(quarter, gameData, shotData, playIndex):
    quarterStarters = [[], []]
    pbp = gameData["pbp"][playIndex:]

    # first quarter starters are given
    if quarter == 0:
        quarterStarters.append([[], []])
        for starter in range(10):
            if pbp[starter]["global-player-id-1"] in shotData["players"]["home"]:
                quarterStarters[0].append(pbp[starter]["global-player-id-1"])
            else:
                quarterStarters[1].append(pbp[starter]["global-player-id-1"])
        return quarterStarters

    # every other quarter
    subbedPlayers = []
    homeStarters = []
    awayStarters = []
    homeTeamId = shotData['teams']['home']
    for play in pbp:
        if play["event-id"] == '10':
            oldPlayer = play["global-player-id-2"]
            newPlayer = play["global-player-id-1"]
            # checks to see if in players

            subbedPlayers.append(newPlayer)
            if (oldPlayer not in homeStarters and oldPlayer not in awayStarters):
                if (oldPlayer not in subbedPlayers):
                    if (int(play["team-code-1"]) == int(homeTeamId)):
                        homeStarters.append(oldPlayer)
                    else:
                        awayStarters.append(oldPlayer)
                continue

        if (newPlayer not in homeStarters and newPlayer not in awayStarters):
            if (newPlayer == ""):
                continue
            if (newPlayer not in subbedPlayers):
                if (int(play["team-code-1"]) == int(homeTeamId)):
                    homeStarters.append(newPlayer)
                else:
                    awayStarters.append(newPlayer)

        if (len(awayStarters) == 5 and len(homeStarters) == 5):
            break
    quarterStarters.append(homeStarters)
    quarterStarters.append(awayStarters)
    return quarterStarters







if __name__ == "__main__":
    print "main running in csvToJson.py"
    main()
