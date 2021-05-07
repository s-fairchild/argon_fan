from time import sleep
import smbus, gpiozero as gpio

class FanMonitor:
    def __init__(self, config, address=0x1a):
        self.fanconfig = config
        self.address = address
        try:
            self.bus = smbus.SMBus(1)
        except Exception as e:
            print(f"Failed to set SMBus(1), {e}\nTrying SMBus(0)")
            try:
                self.bus = smbus.SMBus(0)
            except Exception as e:
                print(f"Failed to set SMBus(1): {e}\nIs i2c enabled?\nFan cannot be accessed without enabling i2c.")
        
    def compare_fanspeed(self, temperature, fanconfig):
        for temp in fanconfig['temperatures']:
            if temperature >= temp:
                return fanconfig['temperatures'][temp]
        return 0

    def fan_monitor(self):
        while True:
            tempC = round(gpio.CPUTemperature().temperature, 1)
            block = self.compare_fanspeed(tempC, self.fanconfig)
            print(f"Current CPU temperature\n\tC:{tempC}\n\tF:{tempC * 1.8 + 32}\nSetting Fan speed to: {block}")
            try:
                self.bus.write_byte(self.address, block)
            except IOError as e:
                print(f"Unable to set fan speed: {e}")
            sleep(30)