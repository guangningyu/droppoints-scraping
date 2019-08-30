import os
import time
import pandas as pd
import requests
from bs4 import BeautifulSoup

class DropPointScraper:
    def __init__(self, output_dir):
        self.session = requests.Session()
        self.token = None
        self.cities_file_path = 'input/cities.csv'
        self.output_dir = output_dir
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

    def set_token(self):
        url = 'http://www.jet.co.id/droppoint'
        res = self.session.get(url)
        soup = BeautifulSoup(res.text, "lxml")
        self.token = soup.find('input', attrs = {'name' : '_token'})['value']

    def get_cities(self):
        with open(self.cities_file_path, 'r') as f:
            cities = [line.strip() for line in f.readlines()]
        return cities

    def get_areas(self, city):
        url = 'http://www.jet.co.id/droppoint/area'
        headers = {
            'X-CSRF-TOKEN': self.token,
        }
        data = {
            'city': city,
        }
        res = self.session.post(url, headers=headers, json=data)
        areas = [key for key in res.json().keys()]
        return areas

    def get_droppoints(self, city, area):
        url = 'http://www.jet.co.id/droppoint'
        data = {
            '_token': self.token,
            'droppoint-city': city,
            'droppoint-area': area,
        }
        res = self.session.post(url, json=data)

        # extract data from table
        droppoints = []
        soup = BeautifulSoup(res.text, "lxml")
        for row in soup.find('tbody').findAll('tr'):
            cols = row.findAll('td')
            cols = [ele.text.strip() for ele in cols][:-1]
            droppoints.append(cols)
        return droppoints

    def process_city(self, city):
        print ('Scrape {}...'.format(city))

        # scrape
        self.set_token()
        rows = []
        for area in self.get_areas(city):
            try:
                for droppoint in self.get_droppoints(city, area):
                    droppoint.insert(0, area)
                    droppoint.insert(0, city)
                    rows.append(droppoint)
            except Exception as e:
                    print (city, area, e)
                    pass

        # save output
        file_path = os.path.join(self.output_dir, '{}.csv'.format(city))
        df = pd.DataFrame(rows)
        df.to_csv(file_path, index=False, header=False, sep='~')

    def run(self):
        for city in self.get_cities():
            try:
                self.process_city(city)
            except Exception as e:
                print (e)
                pass
            time.sleep(1)

if __name__ == '__main__':
    DropPointScraper(
        output_dir='/Users/guangning.yu/Workspace/20190829_web_crawl/output'
    ).run()
