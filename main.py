from threading import Thread
from fan_monitor import FanMonitor
from powerbutton import PowerButton
from signal import signal, SIGINT
from sys import exit

def handler(signal_received, frame):
    print('SIGINT or CTRL-C detected. Exiting gracefully')
    exit(0)

if __name__=="__main__":
    signal(SIGINT, handler)
    fan_monitor = FanMonitor()
    power_button = PowerButton()
    th_fan_monitor = Thread(target=fan_monitor.fan_monitor(), daemon=True)
    th_power_button = Thread(target=power_button.monitor(), daemon=True)
    try:
        print("Starting fan monitoring thread now.")
        th_fan_monitor.start()
        print("Starting powerbutton monitoring thread now.")
        th_power_button.start()
    except Exception as e:
        print(e)
        print("Stopping threads now...")