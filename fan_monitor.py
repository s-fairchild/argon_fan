from yaml import safe_load
from time import sleep
from subprocess import Popen, PIPE
import smbus

class FanMonitor:
    def __init__(self):
        self.fanconfig = {
            65: 100,
            60: 55,
            55: 10
        }
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
    
    def read_temperature(self):
        try:
            p1 = Popen(['vcgencmd', 'measure_temp'], stdout=PIPE)
            data = p1.communicate()
        except Exception as e:
            print(e)
            
        if data[1] is not None:
            print(f"Error running vcgencmd measure_temp: {data[1]}")
        str_tempC = data[0]
        str_tempC = str_tempC.replace("temp=","")
        return float(str_tempC.replace("\'C",""))

    def fan_monitor(self):
        address = 0x1a
        block = 0
        self.fanconfig = self.parse_config()
        while True:
            tempC = self.read_temperature()
            block = self.compare_fanspeed(tempC, self.fanconfig)
            try:
                self.bus.write_byte(address, block)
            except IOError as e:
                print(f"Unable to set fan speed: {e}")
            sleep(30)