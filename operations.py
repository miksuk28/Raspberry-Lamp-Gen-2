### FUNCTIONS, NON ENDPOINTS ###

import time
import multiprocessing
import threading
from validation import *
import ctypes

pins = {"r": 17, "g": 22, "b": 24, "btn": 27}
current_state = [0, 0, 0]
lamp_thread_busy = False
debug = True

def setup():
    global debug
    if not debug:
            import pigpio
            pi = pigpio.pi()
            debug = False
            print("Running on ARM")
    else:
        pi = "DEBUG"
        debug = True
        print(f"Not running in Raspi: Enabling debug mode: {debug}")


    return pi


def change_state(r, g ,b):
    current_state[0] = r
    current_state[1] = g
    current_state[2] = b


def set_led(r, g, b):
    global debug
    change_state(r,g,b)

    if not debug:
        pi.set_PWM_dutycycle(pins["r"], int(r))
        pi.set_PWM_dutycycle(pins["g"], int(g))
        pi.set_PWM_dutycycle(pins["b"], int(b))
    else:
        print(f"{r}\t{g}\t{b}")
        
class FadeWithException(threading.Thread):
    def __init__(self, start, end, fade_time, steps=255):
        threading.Thread.__init__(self)
        self.start = start
        self.end = end
        self.fade_time = fade_time
        self.steps = steps

    def run(self):
        self.fade(self.start, self.end, self.fade_time, self.steps)

    def fade(start, end, fade_time, steps=255):
        global lamp_thread_busy
        lamp_thread_busy = True

        if start == end:
            return

        step_R = (end[0] - start[0]) / steps
        step_G = (end[1] - start[1]) / steps
        step_B = (end[2] - start[2]) / steps

        r = start[0]
        g = start[1]
        b = start[2]

        step_time = fade_time / steps

        print(f"Step time: {step_time}")
        print(f"Locked fading: {lamp_thread_busy}")
        print(f"Fading: ({start[0]}, {start[1]}, {start[2]}) -> ({end[0]}, {end[1]}, {end[2]})")

        for i in range(steps):
            #print(f"{i}\t{r}\t{g}\t{b}")
            set_led(r, g, b)

            r += step_R
            g += step_G
            b += step_B

            time.sleep(step_time)

        print("Fading finished")
        lamp_thread_busy = False

    def get_id(self):
        if hasattr(self, "_thread_id"):
            return self._thread_id
        for id, thread in threading._active.items():
            if thread is self:
                return id

    def raise_exception(self):
        thread_id = self.get_id()
        res = ctypes.pythonapi.PyThreadState_SetAsyncExc(thread_id, 
            ctypes.py_object(SystemExit))
        if res > 1:
            ctypes.pythonapi.PyThreadState_SetAsyncExt(thread_id, 0)
            print("Exception raise failure")


def create_fade_thread(start, end, fade_time, steps=255):
    global lamp_thread_busy
    print(f"\nFade thread: {lamp_thread_busy}\n")

    if not lamp_thread_busy:
        global fade_thread

        fade_thread = FadeWithException(start, end, fade_time)
        fade_thread.start()
        time.sleep(2)
        fade_thread.raise_exception()

        return True
    else:
        return False