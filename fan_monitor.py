from time import sleep
from subprocess import Popen, PIPE
import smbus

class FanMonitor:
    def __init__(self, config):
        self.fanconfig = config
        try:
            self.bus = smbus.SMBus(1)
        except:
            self.bus = smbus.SMBus(0)
        
    def compare_fanspeed(self, temperature, fanconfig):
        for temp in fanconfig['temperatures']:
            if temperature >= temp:
                return fanconfig['temperatures'][temp]
        return 0
    
    def read_temperature(self):
        try:
            p1 = Popen(['vcgencmd', 'measure_temp'], stdout=PIPE)
            data = p1.communicate()
        except Exception as e:
            print(f"Error running vcgencmd measure_temp: {e}")
        if data[1] is not None:
            print(f"Error running vcgencmd measure_temp: {data[1]}")

        str_tempC = data[0].decode('utf-8')
        str_tempC = str_tempC.replace("\\n","")
        str_tempC = str_tempC.replace("temp=","")
        return float(str_tempC.replace("\'C",""))

    def fan_monitor(self, db):
        address = 0x1a
        block = 0
        while True:
            tempC = self.read_temperature()
            block = self.compare_fanspeed(tempC, self.fanconfig)
            print(f"Current CPU temperature\n\tC:{tempC}\n\tF:{tempC * 1.8 + 32}\nSetting Fan speed to: {block}")
            try:
                self.bus.write_byte(address, block)
            except IOError as e:
                print(f"Unable to set fan speed: {e}")
            db.insert_into_temperatures(tempC, block)
            sleep(30)