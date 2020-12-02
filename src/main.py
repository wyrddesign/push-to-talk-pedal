import time
import board
import digitalio
import usb_hid
import adafruit_dotstar
from adafruit_hid.keyboard import Keyboard
from adafruit_hid.keycode import Keycode
 

class FootPedal:

    def __init__(self, callbacks, *, pin=board.A1):
        self.callbacks = callbacks
        switch = digitalio.DigitalInOut(pin)
        switch.direction = digitalio.Direction.INPUT
        switch.pull = digitalio.Pull.UP
        self.switch = switch
        self.updater = self.make_updater()

    def make_updater(self):
        is_pressed = False
        while True:
            if not self.switch.value:
                if not is_pressed:
                    for callback in self.callbacks:
                        callback.on_press()
                is_pressed = True
            else:
                for callback in self.callbacks:
                    callback.on_release()
                is_pressed = False    
            yield

    def on_update(self):
        next(self.updater)
        

class LedIndicatorCallback:
    def __init__(self):
        led = adafruit_dotstar.DotStar(board.APA102_SCK, board.APA102_MOSI, 1)
        led[0] = (0, 255, 0)
        led.brightness = 0
        self.led = led
    
    def on_press(self):
        self.led.brightness = 1

    def on_release(self):
        self.led.brightness = 0.25


class DiscordCallback:

    PUSH_TO_TALK_KEY = Keycode.F12

    def __init__(self):
        self.keyboard = Keyboard(usb_hid.devices)

    def on_press(self):
        self.keyboard.press(self.PUSH_TO_TALK_KEY)
    
    def on_release(self):
        self.keyboard.release_all()


foot_pedal = FootPedal([DiscordCallback(), LedIndicatorCallback()])
while True:
    foot_pedal.on_update()
    time.sleep(0.05)