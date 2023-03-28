import sqlite3

class Database:
    def __init__(self, db_filename):
        self.db_filename = db_filename
        self.conn = None
        self.c = None
    
    def connect(self):
        self.conn = sqlite3.connect(self.db_filename)
        self.c = self.conn.cursor()
    
    def create_table(self):
        self.c.execute('''CREATE TABLE IF NOT EXISTS articles
                            (id INTEGER PRIMARY KEY AUTOINCREMENT, url TEXT, headline TEXT,
                            author TEXT, date TEXT)''')
        self.conn.commit()
    
    def count_articles_with_url(self, url):
        self.c.execute("SELECT COUNT(*) FROM articles WHERE url=?", (url,))
        return self.c.fetchone()[0]
    
    def add_article_to_db(self, url, headline, author, date):
        self.c.execute("INSERT INTO articles (url, headline, author, date) VALUES (?, ?, ?, ?)",
                          (url, headline, author, date))
        self.conn.commit()
    
    def get_articles_from_db(self):
        self.c.execute("SELECT * FROM articles")
        return self.c.fetchall()
    
    def close(self):
        self.conn.close()