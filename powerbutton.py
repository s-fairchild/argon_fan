from gpiozero import Button
import subprocess

class PowerButton:
    def __init__(self, button=Button(4)):
        self.button = button
    
    def shutdown(self):
        subprocess.call("systemctl poweroff")
    
    def reboot(self):
        subprocess.call("systemctl reboot")
    
    def monitor(self):
        self.button.when_held = self.shutdown
