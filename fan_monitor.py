from time import sleep
import smbus, gpiozero as gpio
from database import MariaDB

class FanMonitor:
    def __init__(self, config, address=0x1a, usedatabase=False):
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
        self.usedatabase = config['database']['enabled']
        
    def compare_fanspeed(self, temperature, fanconfig):
        for temp in fanconfig['temperatures']:
            if temperature >= temp:
                return fanconfig['temperatures'][temp]
        return 0
    
    def show_data_pretty(self, readings):
        print(f"Average CPU temperature\n\tC:{readings['tempC_avg']}\n\tF:{readings['tempC_avg'] * 1.8 + 32}")
        print(f"Minimum CPU temperature\n\tC:{readings['tempC_min']}\n\tF:{readings['tempC_min'] * 1.8 + 32}")
        print(f"Maximum CPU temperature\n\tC:{readings['tempC_max']}\n\tF:{readings['tempC_max'] * 1.8 + 32}")

    def fan_monitor(self):
        if self.usedatabase:
            db = MariaDB(user=self.fanconfig['database']['username'], password=self.fanconfig['database']['password'], host=self.fanconfig['database']['host'], port=self.fanconfig['database']['port'], database=self.fanconfig['database']['database'], table=self.fanconfig['database']['table'])
        while True:
            cpu_tempC = round(gpio.CPUTemperature().temperature, 1)
            block = self.compare_fanspeed(cpu_tempC, self.fanconfig)
            print(f"Current CPU temperature\n\tC:{cpu_tempC}\n\tF:{cpu_tempC * 1.8 + 32}\nSetting Fan speed to: {block}")
            try:
                self.bus.write_byte(self.address, block)
            except IOError as e:
                print(f"Unable to set fan speed: {e}")
            if 'db' in locals():
                db.save_data(cpu_tempC, block)
                if self.fanconfig['database']['showdata']:
                    self.show_data_pretty(db.query_data())
            sleep(30)