from gpiozero import Button
from subprocess import call

class PowerButton:
    def __init__(self, button=Button(4)):
        self.button = button
    
    def shutdown(self):
        call("systemctl poweroff")
    
    def reboot(self):
        call("systemctl reboot")
    
    def monitor(self):
        self.button.when_held = self.shutdown
