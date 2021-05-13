import unittest
from fan_monitor import FanMonitor
from main import parse_config

config = parse_config()
fan_monitor = FanMonitor(config)

class TestFanSpeed(unittest.TestCase):
    def test_fanspeed(self):
        for i in range(0, 55):
            print('testing', i)
            assert fan_monitor.compare_fanspeed(i) == 0
        print('Done with 0 speed tests.')
        for i in range(55, 60):
            print('testing', i)
            assert fan_monitor.compare_fanspeed(i) == 10
        print('Done with 10 speed tests.')
        for i in range(60, 65):
            print('testing', i)
            assert fan_monitor.compare_fanspeed(i) == 55
        print('Done with 55 speed tests.')
        for i in range(65, 121):
            print('testing', i)
            assert fan_monitor.compare_fanspeed(i) == 100
        print('Done with 100 speed tests.')


if __name__ == '__main__':
    unittest.main()