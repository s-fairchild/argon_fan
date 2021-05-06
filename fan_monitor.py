from time import sleep
import smbus, gpiozero as gpio

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

    def fan_monitor(self):
        address = 0x1a
        while True:
            tempC = round(gpio.CPUTemperature.temperature, 1)
            block = self.compare_fanspeed(tempC, self.fanconfig)
            print(f"Current CPU temperature\n\tC:{tempC}\n\tF:{tempC * 1.8 + 32}\nSetting Fan speed to: {block}")
            try:
                self.bus.write_byte(address, block)
            except IOError as e:
                print(f"Unable to set fan speed: {e}")
            sleep(30)