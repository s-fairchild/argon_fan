import mariadb as db
from time import sleep
from datetime import datetime
import sqlite3

query_avg = """ SELECT avg(cpu_tempC) from temperatures; """
query_min = """ SELECT min(cpu_tempC) from temperatures; """
query_max = """ SELECT max(cpu_tempC) from temperatures; """
insert_row = f"""INSERT INTO temperatures(cpu_tempC, fanspeed) VALUES(?, ?);"""
readings = {
    'tempC_avg' : 0,
    'tempC_max' : 0,
    'tempC_min' : 0
    }

class MariaDB:
    def __init__(self, config):
        self.username = config['database']['mariadb']['username']
        self.password = config['database']['mariadb']['password']
        self.host = config['database']['mariadb']['host']
        self.port = config['database']['mariadb']['port']
        self.database = config['database']['mariadb']['database']
        self.table = config['database']['mariadb']['table']
    
    def init_database(self):
        create_db = f""" CREATE DATABASE IF NOT EXISTS {self.database}; """
        create_table = f""" CREATE TABLE IF NOT EXISTS {self.database}.{self.table}(
                        ID BIGINT NOT NULL PRIMARY KEY AUTO_INCREMENT,
                        created TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        cpu_tempC DECIMAL(6,2) NOT NULL,
                        fanspeed INT(100)             
                        );"""
        conn = self.db_connect()
        cursor = conn.cursor()
        cursor.execute(create_db); conn.commit()
        cursor.execute(create_table); conn.commit()
        conn.close()

    def db_connect(self):
        for i in range(1, 4): # Retry 3 times increasing delay by 10 seconds each time
            delay = i * 10
            try:
                conn = db.connect(
                    user = self.username,
                    password = self.password,
                    host = self.host,
                    port = self.port,
                    database = self.database
                )
                return conn
            except db.Error as e:
                print(f"Error connecting to MariaDB Server: {e}\n\t Retry number {i}\n\t Retrying in {delay} seconds...")
                sleep(delay)
                continue

    def save_data(self, cpu_tempC, fanspeed):
        conn = self.db_connect()
        cur = conn.cursor()
        data_tuple = (cpu_tempC, fanspeed)
        cur.execute(insert_row, data_tuple)
        conn.commit(); conn.close()

    def query_data(self):
        conn = db.connect()
        cursor = conn.cursor()
        cursor.execute(query_avg)
        row = cursor.fetchone()
        if row[0] is not None:
            readings['tempC_avg'] = row[0]
        cursor.execute(query_min)
        row2 = cursor.fetchone()
        if row2[0] is not None:
            readings['tempC_min'] = row2[0]
        cursor.execute(query_max)
        row3 = cursor.fetchone()
        if row3[0] is not None:
            readings['tempC_max'] = row3[0]
        return readings

class Sqlite3:
    def __init__(self, filedb='fand.db'):
            self.filedb = filedb
            self.init_database()
    
    def create_connection(self):
        try:        
            conn = sqlite3.connect(self.filedb)
            return conn
        except Exception as e:
            print(f"Unable to connect to sqlite3 database {self.filedb}, {e}")
    
    def init_database(self):
        conn = self.create_connection()
        cursor = conn.cursor()
        create_table_sql = """
            CREATE TABLE IF NOT EXISTS temperatures(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                created DATETIME DEFAULT CURRENT_TIMESTAMP,
                cpu_tempC REAL,
                fanspeed
            );
            """
        cursor.execute(create_table_sql)
        conn.commit()
        cursor.close()

    def save_data(self, tempC, fanspeed):
        conn = self.create_connection(); cursor = conn.cursor()
        data_tuple = (tempC, fanspeed)
        cursor.execute(insert_row, data_tuple)
        conn.commit()
        conn.close()
    
    def query_data(self):
        conn = self.create_connection(); cursor = conn.cursor()
        cursor.execute(query_avg)
        row = cursor.fetchone()
        if row[0] is not None:
            readings['tempC_avg'] = row[0]
        cursor.execute(query_min)
        row2 = cursor.fetchone()
        if row2[0] is not None:
            readings['tempC_min'] = row2[0]
        cursor.execute(query_max)
        row3 = cursor.fetchone()
        if row3[0] is not None:
            readings['tempC_max'] = row3[0]
        return readings