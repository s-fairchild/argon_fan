from time import sleep
from datetime import datetime
import sqlite3 as db

readings = {
    'tempC_avg' : 0,
    'tempC_max' : 0,
    'tempC_min' : 0
    }

class Sqlite3:
    def __init__(self, config, filedb='fand.db'):
        self.filedb = filedb
        self.table = config['database']['sqlite']['table']
        self.query_avg = f""" SELECT avg(cpu_tempC) from {self.table}; """
        self.query_min = f""" SELECT min(cpu_tempC) from {self.table}; """
        self.query_max = f""" SELECT max(cpu_tempC) from {self.table}; """
        self.insert_row = f"""INSERT INTO {self.table}(cpu_tempC, fanspeed) VALUES(?, ?);"""
        self.create_table = f""" CREATE TABLE IF NOT EXISTS {self.table}(
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            created DATETIME DEFAULT CURRENT_TIMESTAMP,
                            cpu_tempC REAL,
                            fanspeed
                            ); """
        self.init_database()
    
    def create_connection(self):
        try:        
            conn = db.connect(self.filedb)
            return conn
        except Exception as e:
            print(f"Unable to connect to sqlite3 database {self.filedb}, {e}")
    
    def init_database(self):
        conn = self.create_connection()
        cursor = conn.cursor()
        cursor.execute(self.create_table)
        conn.commit()
        cursor.close()

    def save_data(self, cpu_tempC, fanspeed):
        conn = self.create_connection(); cursor = conn.cursor()
        data_tuple = (round(cpu_tempC, 2), fanspeed)
        cursor.execute(self.insert_row, data_tuple)
        conn.commit()
        conn.close()
    
    def query_data(self):
        conn = self.create_connection(); cursor = conn.cursor()
        cursor.execute(self.query_avg)
        row = cursor.fetchone()
        if row[0] is not None:
            readings['tempC_avg'] = row[0]
        cursor.execute(self.query_min)
        row2 = cursor.fetchone()
        if row2[0] is not None:
            readings['tempC_min'] = row2[0]
        cursor.execute(self.query_max)
        row3 = cursor.fetchone()
        if row3[0] is not None:
            readings['tempC_max'] = row3[0]
        return readings