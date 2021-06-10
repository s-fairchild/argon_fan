from time import sleep
import smbus, gpiozero as gpio
from random import randint

class FanMonitor:
    def __init__(self, config, address=0x1a, usedatabase=False):
        if config['dev_debug_mode'] is False:
            try:
                self.bus = smbus.SMBus(1)
            except Exception as e:
                print(f"Failed to set SMBus(1), {e}\nTrying SMBus(0)")
                try:
                    self.bus = smbus.SMBus(0)
                except Exception as e:
                    print(f"Failed to set SMBus(1): {e}\nIs i2c enabled?\nFan cannot be accessed without enabling i2c.")
        self.fanconfig = config
        self.address = address

    def dummy_smbus(self, address, block):
        print(f"USING DUMMY SMBus interface! - No real hardware changes were made. \
            \nWrote address: {address} and block: {block} to dummy smbus.")

    def compare_fanspeed(self, temperature):
        for temp in self.fanconfig['temperatures']:
            if temperature >= temp:
                return self.fanconfig['temperatures'][temp]
        return 0

    def fan_monitor(self):
        old_block, block = 0, 0
        while True:
            if self.fanconfig['dev_debug_mode'] is False:
                cpu_tempC = round(gpio.CPUTemperature().temperature, 1)
                block = self.compare_fanspeed(cpu_tempC)
                try:
                    self.bus.write_byte(self.address, block)
                except IOError as e:
                    print(f"Unable to set fan speed: {e}")
            else:
                cpu_tempC = round(float(randint(30, 70)), 1)
                block = self.compare_fanspeed(cpu_tempC)
                self.dummy_smbus(self.address, block)
            
            if block < old_block:
                sleep(30) # Run fan for an additional 30 seconds if the fan speed is being set lower
            if block != old_block:
                print(f"Current CPU temperature\n\tC:{cpu_tempC}\n\tF:{cpu_tempC * 1.8 + 32}\nSetting Fan speed to: {block}\n")
            sleep(30)