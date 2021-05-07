import mariadb as db
from time import sleep

class MariaDB:
    def __init__(self, user="rpi4", password="password", host="127.0.0.1", port=3306, database="hardware_readings", table="cputemps"):
        self.user = user
        self.password = password
        self.host = host
        self.port = port
        self.database = database
        self.table = table
    
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
                    user = self.user,
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
        insert_statement = f"""INSERT INTO sensors(cpu_tempC, fanspeed) VALUES({cpu_tempC}, {fanspeed});"""
        conn = self.db_connect()
        cur = conn.cursor()
        cur.execute(insert_statement)
        conn.commit(); conn.close()

    def query_data(self):
        readings = {
            'cpu' : {
                'tempC_avg' : 0,
                'tempC_max' : 0,
                'tempC_min' : 0
            },
            'videocore' : {
                'tempC_avg' : 0,
                'tempC_max' : 0,
                'tempC_min' : 0
            }
        }
        query_avg = """ SELECT avg(tempC) from hardware_readings; """
        query_min = """ SELECT min(tempC) from hardware_readings; """
        query_max = """ SELECT max(tempC) from hardware_readings; """
        conn = db.connect()
        cursor = conn.cursor()
        cursor.execute(query_avg)
        row = cursor.fetchone()
        if row[0] is not None:
            readings['cpu']['tempC_avg'] = row[0]
        cursor.execute(query_min)
        row2 = cursor.fetchone()
        if row2[0] is not None:
            readings['cpu']['tempC_min'] = row2[0]
        cursor.execute(query_max)
        row3 = cursor.fetchone()
        if row3[0] is not None:
            readings['cpu']['tempC_max'] = row3[0]
        return readings
