### FUNCTIONS, NON ENDPOINTS ###

import time
from threading import Timer, Thread

from validation import *

debug = True

pins = {"r": 17, "g": 22, "b": 24, "btn": 27}
current_state = [0, 0, 0]
lamp_thread_busy = False


def setup():
    if not debug:
        import pigpio
        pi = pigpio.pi()
    else:
        pi = "DEBUG"

    return pi


def change_state(r, g ,b):
    current_state[0] = r
    current_state[1] = g
    current_state[2] = b


def set_led(r, g, b):
    change_state(r,g,b)

    if not debug:
        pi.set_PWM_dutycycle(pins["r"], r)
        pi.set_PWM_dutycycle(pins["g"], g)
        pi.set_PWM_dutycycle(pins["b"], b)
    else:
        print(f"{r}\t{g}\t{b}")
        

def fade(start, end, fade_time, steps=255):
    global lamp_thread_busy
    lamp_thread_busy = True

    if start == end:
        return

    step_R = (end[0] - start[0]) / steps
    step_G = (end[1] - start[1]) / steps
    step_B = (end[2] - start[2]) / steps

    r = int(start[0])
    g = int(start[1])
    b = int(start[2])

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


def create_fade_thread(start, end, fade_time, steps=255):
    print(lamp_thread_busy)
    if not lamp_thread_busy:
        global fade_thread

        fade_thread = Thread(target=fade, args=(start, (end[0], end[1], end[2]), fade_time, steps))
        fade_thread.start()

        return True
    else:
        return False