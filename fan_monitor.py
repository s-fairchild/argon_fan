from time import sleep
import smbus, gpiozero as gpio
from random import randint

class FanMonitor:
    def __init__(self, config, address=0x1a, usedatabase=False):
        if config['dev_debug_mode'] is False:
            try:
                self.bus = smbus.SMBus(config["i2c_bus"])
            except Exception as e:
                print(f"Failed to set SMBus({config[i2c_bus]}): {e}")
        self.fanconfig = config
        self.address = address
        self.sqlite = config['database']['sqlite']['enabled']
        self.filedb = config['database']['sqlite']['file']

    def dummy_smbus(self, address, block):
        print(f"USING DUMMY SMBus interface! - No real hardware changes were made. \
            \nWrote address: {address} and block: {block} to dummy smbus.")

    def compare_fanspeed(self, temperature):
        for temp in self.fanconfig['temperatures']:
            if temperature >= temp:
                return self.fanconfig['temperatures'][temp]
        return 0
    
    def show_data_pretty(self, readings):
        print(f"Average CPU temperature\n\tC:{readings['tempC_avg']}\n\tF:{readings['tempC_avg'] * 1.8 + 32}\n")
        print(f"Minimum CPU temperature\n\tC:{readings['tempC_min']}\n\tF:{readings['tempC_min'] * 1.8 + 32}\n")
        print(f"Maximum CPU temperature\n\tC:{readings['tempC_max']}\n\tF:{readings['tempC_max'] * 1.8 + 32}\n")

    def fan_monitor(self):
        if self.sqlite:
            from database import Sqlite3
            db = Sqlite3(self.fanconfig)
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
                
            print(f"Current CPU temperature\n\tC:{cpu_tempC}\n\tF:{round(cpu_tempC * 1.8 + 32, 1)}\nSetting Fan speed to: {block}\n")
            
            if 'db' in locals():
                db.save_data(cpu_tempC, block)
                if self.fanconfig['database']['showdata']:
                    self.show_data_pretty(db.query_data())
            sleep(30)