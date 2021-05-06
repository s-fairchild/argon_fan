import sqlite3

class Sqlite3Database:
    def __init__(self, filedb='fand_temps.db'):
        self.filedb = filedb
        self.conn = sqlite3.connect("file::memory:?cache=shared", uri=True)
        self.cursor = self.conn.cursor()
        self.create_table_sql = """
        CREATE TABLE temperatures(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            created DATETIME DEFAULT CURRENT_TIMESTAMP,
            tempC,
            fanspeed
        );
        """
        self.cursor.execute(self.create_table_sql)

    def insert_into_temperatures(self, tempC, fanspeed):
        insert_row = f""" INSERT INTO temperatures(tempC, fanspeed) VALUES({tempC}, {fanspeed});"""
        self.cursor.execute(insert_row)
        self.conn.commit()
    
    def query_temp_avg(self):
        query = """ SELECT avg(tempC) from temperatures; """
        self.cursor.execute(query)
        row = self.cursor.fetchone()
        if row[0] is not None:
            tempF_avg = row[0] * 1.8 + 32 # Create tempF avg
            return row[0],tempF_avg
        else:
            print("Not enough data to create averages.")
            return None
    
    def progress(self, status, remaining, total):
        print(f'Copied {total-remaining} of {total} pages...')

    def write_memdb_tofile(self):
        bck = sqlite3.connect('fand_temps.db')
        with bck:
            self.conn.backup(bck, pages=1, progress=self.progress)
        bck.close()
    
    def restore_db(self):
        source = sqlite3.connect(self.filedb)
        dest = sqlite3.connect(':memory:')
        source.backup(dest)
