import requests
from bs4 import BeautifulSoup
import json
from datetime import date, timedelta
import os


class ScheduleBuilder(object):

    cbs = 'http://www.cbssports.com/nba/scoreboard/'
    first_day = date(2014, 10, 28)

    def __init__(self):
        self.schedule = {}
        self.today = date.today()

    def build_schedule(self):
        current_date = self.first_day
        while current_date < self.today:
            self.__get_games(self.__date(current_date))
            current_date = current_date + timedelta(days=1)

    def __get_games(self, date):
        games = []
        r = requests.get(self.cbs + date)
        soup = BeautifulSoup(r.text)
        for game in soup.find_all(class_="scoreLinks"):
            temp = game.a.get('href').split('_')[2]
            games.append(temp)
        self.schedule[date] = games

    def export_schedule(self):
        with open("data/schedule.json", "wb") as f:
            json.dump(self.schedule, f)

    def pull_schedule(self):
        with open('data/schedule.json') as data_file:
            self.schedule = json.load(data_file)

    def get_schedule(self):
        if os.path.exists('data/schedule.json'):
            self.pull_schedule()
        else:
            self.build_schedule()
        return self.schedule

    def __date(self, date):
        if (date.day < 10):
            return str(date.year) + str(date.month) + '0' + str(date.day)
        return str(date.year) + str(date.month) + str(date.day)


class Basketballer(object):

    api = "http://api.nba.onetwosee.com/update/"
    teams = {
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

    def __init__(self, schedule):
        self.schedule = schedule

    def get_games(self):
        for date in self.schedule:
            if not os.path.exists('data/games/' + date):
                os.makedirs('data/games/' + date)
            for game in self.schedule[date]:
                pbp, game_id = self.get_pbp(game, date)
                #only when fresh
                #pbp["pbp"] = pbp["pbp"]["sports-scores"]["nba-scores"]["nba-playbyplay"]["play"]
                self.export_pbp(pbp, game_id, date)
                cur_game = Game(date, pbp)
                cur_game.generate_data()
                print 'checking'

    def get_pbp(self, game, date):
        game_id = date + self.teams[game.split('@')[1]]
        if os.path.exists('data/games/' + str(date) + "/" + str(game_id) + ".json"):
            with open('data/games/' + str(date) + "/" + str(game_id) + ".json") as data_file:
                return json.load(data_file), game_id
        r = requests.get(self.api+game_id)
        return json.loads(r.text), game_id

    def export_pbp(self, pbp, game_id, date):
        with open('data/games/' + str(date) + "/" + str(game_id) + ".json", "wb") as f:
            json.dump(pbp, f)


class Game(object):

    def __init__(self, date, game_data):
        self.home = game_data["personalInfo"]["home_team"]["team-code"]["global-id"]
        self.away = game_data["personalInfo"]["away_team"]["team-code"]["global-id"]
        self.date = date
        self.game_data = game_data
        self.num_quarters = int(game_data["gameInfo"]["total-quarters"]["total"])

        self.export = []

        self.home_players, self.away_players = self.get_players(game_data)
        self.home_quarter_starters = []
        self.away_quarter_starters = []

    def get_players(self, game_info):
        home_team = []
        away_team = []

        for playerData in self.game_data["personalInfo"]["home_team"]["nba-player"]:
            home_team.append(int(playerData["player-code"]["global-id"]))

        for playerData in self.game_data["personalInfo"]["away_team"]["nba-player"]:
            away_team.append(int(playerData["player-code"]["global-id"]))

        return home_team, away_team

    def generate_data(self):
        play_index = 0
        for quarter in range(self.num_quarters):
            play_index = self.get_quarter_starters(quarter, play_index)



    def get_quarter_starters(self, quarter, play_index):
        quarterStarters = [[], []]
        pbp = self.game_data["pbp"][play_index:]

        # first quarter starters are given
        if quarter == 0:
            quarterStarters.append([[], []])
            for starter in range(10):
                if int(pbp[starter]["global-player-id-1"]) in self.home_players:
                    quarterStarters[0].append(int(pbp[starter]["global-player-id-1"]))
                else:
                    quarterStarters[1].append(int(pbp[starter]["global-player-id-1"]))
            self.home_quarter_starters.append(quarterStarters[0])
            self.away_quarter_starters.append(quarterStarters[1])

            for i, play in enumerate(pbp[11:]):
                if play['event-id'] == '14':
                    return i


        # every other quarter
        subbedPlayers = []
        homeStarters = []
        awayStarters = []
        homeTeamId = self.home
        for i, play in enumerate(pbp):
            if play["event-id"] == '10':
                oldPlayer = int(play["global-player-id-2"])
                newPlayer = int(play["global-player-id-1"])
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


            if play['event-id'] == '14':
                self.home_quarter_starters.append(homeStarters)
                self.away_quarter_starters.append(awayStarters)
                return play_index + i
                

        


class Player(object):
    #TODO

    def __init__(self, pid, first, last, team):
        self.pid = pid
        self.first = first
        self.last = last
        self.team = team




        


if __name__ == "__main__":
    crawler = ScheduleBuilder()
    schedule = crawler.get_schedule()
    gameData = Basketballer(schedule)
    gameData.get_games()
