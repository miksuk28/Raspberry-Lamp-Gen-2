### FUNCTIONS, NON ENDPOINTS ###

import time
import threading
import os

from validation import *

pins = {"r": 17, "g": 22, "b": 24, "btn": 27}
current_state = [0, 0, 0]
lamp_thread_busy = False
debug = None
exit_thread = False

def setup():
    global debug
    try:
        if os.uname()[4].startswith("arm"):
            import pigpio
            pi = pigpio.pi()
            debug = False
            print("Running on ARM")
    except:
        pi = "DEBUG"
        debug = True
        print("Not running on Raspi: Enabling debug mode")


    return pi


def change_state(r, g ,b):
    current_state[0] = r
    current_state[1] = g
    current_state[2] = b


def set_led(r, g, b):
    global debug
    change_state(r,g,b)

    if not debug:
        pi.set_PWM_dutycycle(pins["r"], r)
        pi.set_PWM_dutycycle(pins["g"], g)
        pi.set_PWM_dutycycle(pins["b"], b)
    else:
        print(f"{r}\t{g}\t{b}")


def kill_thread():
    global exit_thread
    exit_thread = True


def fade_timer(step_r, step_g, step_b, time_between_steps, i=0, steps=255):
    start_time = time.time()

    global lamp_thread_busy, exit_thread
    global cur_r, cur_g, cur_b
    if i >= steps or exit_thread:
        print("Fading finished")

        lamp_thread_busy = False
        exit_thread = False

        if debug:
            print(f"Fading took {time.time() - fade_start} seconds")
        return
    else:
        i += 1
        print(f"i = {i}")
        cur_r += step_r
        cur_g += step_g
        cur_b += step_b

        set_led(cur_r, cur_g, cur_b)
        
        print(f"Actual step time: {time.time() - start_time}")
        timer = threading.Timer(time_between_steps, fade_timer, args=(step_r, step_g, step_b, (time_between_steps - (start_time - time.time())), i, steps))
        timer.start()


def fade(start, end, fade_time, steps=255):
    global lamp_thread_busy
    global cur_r, cur_g, cur_b

    if debug:
        global fade_start
        fade_start = time.time()

    lamp_thread_busy = True

    if start == end:
        return

    step_R = (end[0] - start[0]) / steps
    step_G = (end[1] - start[1]) / steps
    step_B = (end[2] - start[2]) / steps

    cur_r = start[0]
    cur_g = start[1]
    cur_b = start[2]

    step_time = fade_time / steps

    print(f"Step time: {step_time}")

    fade_timer(step_R, step_G, step_B, step_time)
    '''
    print(f"Step time: {step_time}")

    print(f"Step time: {step_time}")
    print(f"Locked fading: {lamp_thread_busy}")
    print(f"Fading: ({start[0]}, {start[1]}, {start[2]}) -> ({end[0]}, {end[1]}, {end[2]})")
    '''


def create_fade_thread(start, end, fade_time, steps=255):
    print(lamp_thread_busy)
    if not lamp_thread_busy:
        global fade_thread

        fade(start, end, fade_time, steps)

        return True
    else:
        return False