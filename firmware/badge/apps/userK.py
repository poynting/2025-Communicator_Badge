"""Template app for badge applications. Copy this file and update to implement your own app."""

import uasyncio as aio  # type: ignore

from apps.base_app import BaseApp
from net.net import register_receiver, send, BROADCAST_ADDRESS
from net.protocols import Protocol, NetworkFrame
from ui.page import Page
import ui.styles as styles
import lvgl as lv

"""
All protocols must be defined in their apps with unique ports. Ports must fit in uint8.
Try to pick a protocol ID that isn't in use yet; good luck.
Structdef is the struct library format string. This is a subset of cpython struct.
https://docs.micropython.org/en/latest/library/struct.html
"""
# NEW_PROTOCOL = Protocol(port=<PORT>, name="<NAME>", structdef="!")


class App(BaseApp):
    """Define a new app to run on the badge."""

    def __init__(self, name: str, badge):
        """ Define any attributes of the class in here, after super().__init__() is called.
            self.badge will be available in the rest of the class methods for accessing the badge hardware.
            If you don't have anything else to add, you can delete this method.
        """
        super().__init__(name, badge)
        # You can also set the sleep time when running in the foreground or background. Uncomment and update.
        # Remember to make background sleep longer so this app doesn't interrupt other processing.
        # self.foreground_sleep_ms = 10
        # self.background_sleep_ms = 1000


    def start(self):
        """ Register the app with the system.
            This is where to register any functions to be called when a message of that protocol is received.
            The app will start running in the background.
            If you don't have anything else to add, you can delete this method.
        """
        super().start()
        # register_receiver(NEW_PROTOCOL, self.receive_message)

    def run_foreground(self):
        """ Run one pass of the app's behavior when it is in the foreground (has keyboard input and control of the screen).
            You do not need to loop here, and the app will sleep for at least self.foreground_sleep_ms milliseconds between calls.
            Don't block in this function, for it will block reading the radio and keyboard.
            If the app only runs in the background, you can delete this method.
        """
        # print() goes to the serial terminal not the screen
        if self.badge.keyboard.f1():
            print("Btn F1 ") 
        if self.badge.keyboard.f2():
            print("Btn F2 ") #8 spaces
        if self.badge.keyboard.f3():
            print("Btn F3")
        if self.badge.keyboard.f4():
            print("Btn F4")
        ## Co-op multitasking: all you have to do is get out
        if self.badge.keyboard.f5():
            self.badge.display.clear()
            self.switch_to_background()
        

    def run_background(self):
        """ App behavior when running in the background.
            You do not need to loop here, and the app will sleep for at least self.background_sleep_ms milliseconds between calls.
            Don't block in this function, for it will block reading the radio and keyboard.
            If the app only does things when running in the foreground, you can delete this method.
        """
        super().run_background()

    def switch_to_foreground(self):
        """ Set the app as the active foreground app.
            This will be called by the Menu when the app is selected.
            Any one-time logic to run when the app comes to the foreground (such as setting up the screen) should go here.
            If you don't have special transition logic, you can delete this method.
        """
        
        super().switch_to_foreground()
        p = Page()
        ## Note this order is important: it renders top to bottom that the "content" section expands to fill empty space
        ## If you want to go fully clean-slate, you can draw straight onto the p.scr object, which should fit the full screen.
        p.create_infobar(["K5EM App", "Does whatever an app does"])
        p.create_content()
        p.create_menubar(["Btn F1", "Btn F2", "Btn F3", "Btn F4", "Done"])
        p.replace_screen()

        scr = lv.obj()
        btn = lv.button(scr)
        btn.align(lv.ALIGN.CENTER, 0, 0)
        label = lv.label(btn)
        label.set_text('Hello World!')
        lv.screen_load(scr)

        # Screen
        scr = lv.obj()
        lv.screen_load(scr)

        size = 50

        circle_obj = lv.obj(scr)
        circle_obj.set_size(size, size)
        circle_obj.set_style_radius(lv.RADIUS_CIRCLE, 0)
        circle_obj.set_style_bg_color(lv.color_hex(0xFF0000), 0)

        start_x = 10
        circle_obj.set_pos(start_x, 50)

        width = lv.display_get_default().get_horizontal_resolution()
        end_x = width - size - start_x

        # assume: start_x, end_x, circle_obj already defined
        mid_x  = (start_x + end_x) / 2
        half_w = (end_x - start_x) / 2

        def move_and_fade_cb(anim, v):
            # move
            circle_obj.set_x(v)

            # fade: 0 at ends, 255 at center (linear)
            dist = abs(v - mid_x)          # distance from center
            t = 1.0 - (dist / half_w)      # 1 at center, 0 at ends
            if t < 0: t = 0
            opa = int(255 * t)             # try t**1.6 for a softer curve
            circle_obj.set_style_bg_opa(opa, 0)

        a = lv.anim_t()
        a.init()
        a.set_var(circle_obj)
        a.set_values(start_x, end_x)
        a.set_duration(2000)
        a.set_reverse_duration(2000)       # your port uses the “reverse_*” names
        a.set_repeat_count(lv.ANIM_REPEAT_INFINITE)
        a.set_path_cb(lv.anim_t.path_ease_in_out)
        a.set_custom_exec_cb(move_and_fade_cb)
        a.start()


    def switch_to_background(self):
        """ Set the app as a background app.
            This will be called when the app is first started in the background and when it stops being in the foreground.
            If you don't have special transition logic, you can delete this method.
        """
        self.p = None
        super().switch_to_background()


