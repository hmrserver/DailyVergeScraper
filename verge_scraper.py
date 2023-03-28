import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime
from database import Database
from csv_file import CSV

class VergeScraper(Database, CSV):
    def __init__(self, url, db_filename="articles.db", csv_filename=None):
        Database.__init__(self, db_filename)
        CSV.__init__(self, csv_filename or datetime.now().strftime("%d%m%Y") + "_verge.csv")
        self.url = url
        self.data = None
        self.unique_articles = {}
    
    def scrape(self):
        print("Getting data from " + self.url + "...")
        self.get_data()
        print("Data retrieved.\nExtracting articles...")
        self.__get_community_articles()
        self.__get_entry_group_articles()
        self.__get_hub_pages_articles()
        self.__get_most_popular_articles()
        print("Articles extracted.\nSaving articles...")
        self.save_articles()
        print("Articles saved.\nThere are " + str(len(self.unique_articles)) + " articles.")
    
    def get_data(self):
        response = requests.get(self.url)
        soup = BeautifulSoup(response.content, 'html.parser')
        script_tag = soup.find('script', {'id': '__NEXT_DATA__'})
        json_text = script_tag.string.strip()
        self.data = json.loads(json_text)
    
    def __get_community_articles(self):
        community = self.data['props']['pageProps']['hydration']['responses'][0]['data']['community']['frontPage']['placements']
        for article in community:
            article = article['placeable']
            if article is None:
                continue
            self.__add_article(article)
    
    def __get_entry_group_articles(self):
        entryGroup = self.data['props']['pageProps']['hydration']['responses'][0]['data']['entryGroup']['recentEntries']['results']
        for article in entryGroup:
            self.__add_article(article)
    
    def __get_hub_pages_articles(self):
        hubPages = self.data['props']['pageProps']['hydration']['responses'][0]['data']['hubPages']
        for category in hubPages:
            articles = category['placeables']
            for article in articles:
                self.__add_article(article)
    
    def __get_most_popular_articles(self):
        mostPopularData = self.data['props']['pageProps']['mostPopularData']
        for article in mostPopularData:
            self.__add_article(article)
    
    def __add_article(self, article):
        self.unique_articles[article['url']] = {
            'title': article['title'],
            'url': article['url'],
            'author': article['author']['fullName'],
            'publishDate': datetime.strptime(article['publishDate'].split('T')[0], '%Y-%m-%d').strftime('%Y/%m/%d')
        }
    
    def save_articles(self):
        self.connect()
        self.create_table()
        
        for article in self.unique_articles.values():
            if article['url'] in self.existing_data_df["url"].values and self.count_articles_with_url(article['url']) > 0:
                continue
            
            new_row = {"id": len(self.existing_data_df), "url": article["url"],
                       "headline": article["title"], "author": article["author"],
                       "date": article["publishDate"]}
            self.add_row_to_csv(new_row)
            self.add_article_to_db(new_row["url"], new_row["headline"], new_row["author"], new_row["date"])

        self.close()

    def print_articles_from_db(self):
        self.connect()
        data = self.get_articles_from_db()
        print(data)
        self.close()

    def print_articles_from_csv(self):
        existing_data_df = self.read_csv()
        if existing_data_df.empty:
            print("No articles found")
        else:
            print(existing_data_df)


if __name__ == '__main__':
    url = 'https://www.theverge.com/'
    scraper = VergeScraper(url)
    scraper.scrape()
    # scraper.print_articles_from_db()
    # scraper.print_articles_from_csv()

