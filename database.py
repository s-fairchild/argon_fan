import sqlite3

class Sqlite3Database:
    def __init__(self, filedb='fand_temps.db'):
        self.filedb = filedb
        self.conn = sqlite3.connect("file::memory:?cache=shared", uri=True)
        self.cursor = self.conn.cursor()
        self.readings = { 
            'tempC_avg' : 0,
            'tempC_max' : 0,
            'tempC_min' : 0
        }
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
    
    def CtoF(self, tempC):
        return tempC * 1.8 + 32
    
    def query_temp_avg(self):
        query_avg = """ SELECT avg(tempC) from temperatures; """
        query_min = """ SELECT min(tempC) from temperatures; """
        query_max = """ SELECT max(tempC) from temperatures; """
        self.cursor.execute(query_avg)
        row = self.cursor.fetchone()
        if row[0] is not None:
            self.readings['tempC_avg'] = row[0]
        self.cursor.execute(query_min)
        row2 = self.cursor.fetchone()
        if row2[0] is not None:
            self.readings['tempC_min'] = row2[0]
        self.cursor.execute(query_max)
        row3 = self.cursor.fetchone()
        if row3[0] is not None:
            self.readings['tempC_max'] = row3[0]
        return self.readings
    
    def show_values_pretty(self):
        self.query_temp_avg
        print(f"Average CPU temperature\n\tC:{self.readings['tempC_avg']}\n\tF:{self.CtoF(self.readings['tempC_avg'])}")
        print(f"Minimum CPU temperature\n\tC:{self.readings['tempC_min']}\n\tF:{self.CtoF(self.readings['tempC_min'])}")
        print(f"Maximum CPU temperature\n\tC:{self.readings['tempC_max']}\n\tF:{self.CtoF(self.readings['tempC_max'])}")
    
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
