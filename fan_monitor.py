from yaml import safe_load
from vcgencmd import Vcgencmd
from time import sleep
import smbus

class FanMonitor:
    def __init__(self):
        self.fanconfig = {
            65: 100,
            60: 55,
            55: 10
        }
        self.vcgm = Vcgencmd()
        try:        
            self.bus = smbus.SMBus(1)
        except:
            self.bus = smbus.SMBus(0)

    def parse_config(self):
        try:
            print("Reading fand.yaml.")
            with open('fand.yaml', 'r') as file:
                config = safe_load(file)
            print("Successfully read fand.yaml.")
            if len(config) == 0:
                return self.fanconfig
            else:
                return config
        except Exception as e:
            print(f"Could not read fand.yaml, error message: {e}")
            print("Using values of 65=100, 60=55, 55=10")
            return self.fanconfig
        
    def compare_fanspeed(self, temperature, fanconfig):
        for temp in fanconfig:
            if temp >= temperature:
                return temp
        return 0

    def fan_monitor(self):
        address = 0x1a
        block = 0
        self.fanconfig = self.parse_config()

        while True:
            current_temp = self.vcgm.measure_temp()
            block = self.compare_fanspeed(current_temp, self.fanconfig)
            try:
                self.bus.write_byte(address, block)
            except IOError as e:
                print(f"Unable to set fan speed: {e}")
            sleep(30)