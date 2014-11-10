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
                self.export_pbp(pbp, game_id, date)

    def get_pbp(self, game, date):
        game_id = date + self.teams[game.split('@')[1]]
        #if os.path.exists('data/games/' + str(date) + "/" + str(game_id) + ".json"):
        #    with open('data/games/' + str(date) + "/" + str(game_id) + ".json") as data_file:
        #        return json.load(data_file)
        r = requests.get(self.api+game_id)
        pbp = json.loads(r.text)
        return pbp["pbp"]["sports-scores"]["nba-scores"]["nba-playbyplay"]["play"], game_id

    def export_pbp(self, pbp, game_id, date):
        with open('data/games/' + str(date) + "/" + str(game_id) + ".json", "wb") as f:
            json.dump(pbp, f)


class Game(object):

    def __init__(self, arg):
        self.home = ''
        self.away = ''
        self.date = ''
        self.home_players = []
        self.away_players = []
        self.home_quarter_starters = []
        self.away_quarter_starters = []


        


if __name__ == "__main__":
    crawler = ScheduleBuilder()
    schedule = crawler.get_schedule()
    gameData = Basketballer(schedule)
    gameData.get_games()
