import requests
from bs4 import BeautifulSoup
import json
from datetime import date, timedelta


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


    def __date(self, date):
        if (date.day<10):
            return str(date.year) + str(date.month) + '0' + str(date.day)
        return str(date.year) + str(date.month) + str(date.day)

if __name__ == "__main__":
    crawler = ScheduleBuilder()
    crawler.build_schedule()
    crawler.export_schedule()
