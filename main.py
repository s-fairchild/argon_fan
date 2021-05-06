from threading import Thread
from fan_monitor import FanMonitor
from powerbutton import PowerButton
from signal import signal, SIGINT
from sys import exit
from yaml import safe_load
from database import Sqlite3Database

default_fanconfig = {
        'temperatures': {
            65: 100,
            60: 55,
            55: 10
        },
    }

def handler(signal_received, frame):
    db.write_memdb_tofile()
    db.conn.close()
    fan_monitor.bus.write_byte(fan_monitor.address, 0) # Set fanspeed to 0
    print('SIGINT or CTRL-C detected. Exiting gracefully')
    exit(0)

def parse_config():
    try:
        print("Reading fand.yaml.")
        with open('fand.yaml', 'r') as file:
            config = safe_load(file)
        print("Successfully read fand.yaml.")
        if len(config) == 0:
            return default_fanconfig
        else:
            return config
    except Exception as e:
        print(f"Could not read fand.yaml, error message: {e}")
        print("Using values of 65=100, 60=55, 55=10")
        return default_fanconfig

if __name__=="__main__":
    db = Sqlite3Database()
    signal(SIGINT, handler)
    config = parse_config()
    fan_monitor = FanMonitor(config)
    power_button = PowerButton()
    th_fan_monitor = Thread(target=fan_monitor.fan_monitor(db), daemon=True)
    th_power_button = Thread(target=power_button.monitor(), daemon=True)
    try:
        print("Starting fan monitoring thread now.")
        th_fan_monitor.start()
        print("Starting powerbutton monitoring thread now.")
        th_power_button.start()
    except Exception as e:
        print(f"An Exception occured while starting threads: {e}")
        print("Stopping threads now...")