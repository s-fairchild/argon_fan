from time import sleep
import smbus, gpiozero as gpio

class FanMonitor:
    def __init__(self, config, address=0x1a):
        self.fanconfig = config
        self.address = address
        self.tempC = 0
        try:
            self.bus = smbus.SMBus(1)
        except:
            self.bus = smbus.SMBus(0)
        
    def compare_fanspeed(self, temperature, fanconfig):
        for temp in fanconfig['temperatures']:
            if temperature >= temp:
                return fanconfig['temperatures'][temp]
        return 0

    def fan_monitor(self, db=None):
        prev_block = 0
        while True:
            self.tempC = round(gpio.CPUTemperature().temperature, 1)
            block = self.compare_fanspeed(self.tempC, self.fanconfig)
            if block != prev_block:
                print(f"Current CPU temperature\n\tC:{self.tempC}\n\tF:{self.tempC * 1.8 + 32}\nSetting Fan speed to: {block}")
            if prev_block > block:
                sleep(30) # Run fan at higher speed for an additional 30 seconds
            try:
                self.bus.write_byte(self.address, block)
            except IOError as e:
                print(f"Unable to set fan speed: {e}")
            if db is not None:
                db.insert_into_temperatures(self.tempC, block)
            prev_block = block
            sleep(30)