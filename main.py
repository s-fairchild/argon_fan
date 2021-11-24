from threading import Thread
from fan_monitor import FanMonitor
from yaml import safe_load

default_fanconfig = {
        'temperatures': {
            65: 100,
            60: 55,
            55: 10
        },
    }

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
    config = parse_config()
    fan_monitor = FanMonitor(config)
    th_fan_monitor = Thread(target=fan_monitor.fan_monitor, daemon=True)
    try:
        print("Starting fan monitoring thread now.")
        th_fan_monitor.start()
    except Exception as e:
        print(f"An Exception occured while starting threads: {e}")
        print("Stopping threads now...")
    
    th_fan_monitor.join()