from flask import Flask, json, request, jsonify, abort
from threading import Timer, Thread
import operations as ops

import time

pins = {"r": 17, "g": 22, "b": 24, "btn": 27}
current_state = [0, 0, 0]


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
    step_R = end[0] - start[0] / steps
    step_G = end[1] - start[1] / steps
    step_B = end[2] - start[2] / steps

    r = int(start[0])
    g = int(start[1])
    b = int(start[2])

    step_time = fade_time / steps

    for i in range(steps):
        set_led(r, g, b)

        r += step_R
        g += step_G
        b += step_B

        time.sleep(step_time)


app = Flask(__name__)


@app.route("/set_led", methods=["POST"])
def set_led_endpoint():
    if request.method == "POST":
        data = request.get_json()

        if ops.validate(("red", "green", "blue"), data):
            #_set_led(data["red"], data["green"], data["blue"])
            fade(current_state, (data["red"], data["green"], data["blue"]), 1)

            return jsonify({"message": "LEDs changed"})

        else:
            abort(400, "Bad params")
    else:
        abort(405)


if __name__ == "__main__":
    pi = setup()
    set_led(255,255,255)
    app.run(debug=True, host="0.0.0.0", port=6969)
