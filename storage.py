import sqlite3
import pandas as pd


class DBStorage:

    def __init__(self):
        self.con = sqlite3.connect('links.db')
        self.setup_tables()

    def setup_tables(self):
        cur = self.con.cursor()
        results_table = r"""
            CREATE TABLE IF NOT EXISTS results (
                id INTEGER PRIMARY KEY,
                query TEXT,
                rank INTEGER,
                link TEXT,
                title TEXT,
                snippet TEXT,
                html TEXT,
                category TEXT,
                created DATETIME,
                relevance INTEGER,
                UNIQUE(query, link)
            );
            """
        cur.execute(results_table)
        self.con.commit()
        cur.close()

    def query_results(self, query):
        df = pd.read_sql(f"select * from results where query='{query}' order by rank asc", self.con)
        return df

    def insert_data(self, data):
        # conn = sqlite3.connect(self.db_file)
        cur = self.con.cursor()

        # Create a string of placeholders for each column in the DataFrame
        placeholders = ", ".join(["?" for _ in data.columns])

        # Insert the data into the table using the placeholders
        for index, row in data.iterrows():
            cur.execute(
                f"INSERT INTO results ({', '.join(data.columns)}) VALUES ({placeholders})",
                tuple(row)
            )

        self.con.commit()
        cur.close()

    def insert_row(self, values):
        cur = self.con.cursor()
        try:
            cur.execute(
                'INSERT INTO results (query, rank, link, title, snippet, html,category, created) VALUES(?, ?, ?, ?, '
                '?, ? , ?, ?)',
                values)
            self.con.commit()
        except sqlite3.IntegrityError:
            pass
        cur.close()

    def update_relevance(self, query, link, relevance):
        cur = self.con.cursor()
        cur.execute('UPDATE results SET relevance=? WHERE query=? AND link=?', [relevance, query, link])
        self.con.commit()
        cur.close()
