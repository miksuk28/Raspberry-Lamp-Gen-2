from flask import Flask, json, request, jsonify, abort
from threading import Timer, Thread
import operations as ops

import time

pins = {"r": 17, "g": 22, "b": 24, "btn": 27}
current_state = [0, 0, 0]
lamp_thread_busy = False

def setup():
    import pigpio
    pi = pigpio.pi()

    return pi


def change_state(r, g ,b):
    current_state[0] = r
    current_state[1] = g
    current_state[2] = b


def set_led(r, g, b):
    change_state(r,g,b)

    pi.set_PWM_dutycycle(pins["r"], r)
    pi.set_PWM_dutycycle(pins["g"], g)
    pi.set_PWM_dutycycle(pins["b"], b)
        

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

app = Flask(__name__)


@app.route("/set_led", methods=["POST"])
def set_led_endpoint():
    if request.method == "POST":
        data = request.get_json()

        if ops.validate(("red", "green", "blue", "fade_time"), data):
            #_set_led(data["red"], data["green"], data["blue"])
            #fade(current_state, (data["red"], data["green"], data["blue"]), data["fade_time"])

            if create_fade_thread(current_state, (data["red"], data["green"], data["blue"]), data["fade_time"]):
                return jsonify({"message": "LEDs changing"})
            else:
                abort(503, {"message": "Fading already in progress"})

        else:
            abort(400, "Bad params")
    else:
        abort(405)

@app.route("/get_colour", methods=["GET"])
def get_colour():
    if request.method == "GET":
        data = {"red": current_state[0], "green": current_state[1], "blue": current_state[2]}
        return jsonify(data), 200
    else:
        abort(405)

@app.route("/stop_fade", methods=["POST"])
def stop_fading():
    if request.method == "POST":
        if not lamp_thread_busy:
            return jsonify({"message": "Thread is not running: nothing to stop"}), 412
        else:
            fade_thread.kill()
            print("Fading thread killed")
            return jsonify({"message": "Fading thread has been killed", "red": current_state[0], "green": current_state[1], "blue": current_state[2]})
    else:
        abort(405)


if __name__ == "__main__":
    pi = setup()
    set_led(255,255,255)
    app.run(debug=True, host="0.0.0.0", port=6969)
