from flask import Flask, json, request, jsonify, abort
from threading import Timer, Thread
import operations as ops

import time

pins = {"r": 17, "g": 22, "b": 24, "btn": 27}
current_state = {"red": 0, "green": 0, "blue": 0}


def setup():
    import pigpio
    pi = pigpio.pi()

    return pi


def _change_state(r, g, b):
    current_state["red"] = int(r)
    current_state["green"] = int(g)
    current_state["blue"] = int(b)


def _set_led(r, g, b):
    colors = [r, g, b]

    for i in range(len(colors)):
        if colors[i] > 255:
            colors[i] = 255
        elif colors[i] < 0:
            colors[i] = 0


    _change_state(colors[0], colors[1], colors[2])

    pi.set_PWM_dutycycle(pins["r"], colors[0])
    pi.set_PWM_dutycycle(pins["g"], colors[1])
    pi.set_PWM_dutycycle(pins["b"], colors[2])


def fade(start, end, fade_time, steps=255):
    r_step = (end["red"] -   start["red"])   / steps
    g_step = (end["green"] - start["green"]) / steps
    b_step = (end["blue"] -  start["blue"])  / steps

    step_time = fade_time / steps

    _r = start["red"]
    _g = start["green"]
    _b = start["green"]

    for i in range(steps):
        _r += r_step
        _g += g_step
        _b += b_step

        print(_r, _g, _b)
        _set_led(_r, _g, _b)

        time.sleep(step_time)
    
    print(current_state)
        

app = Flask(__name__)


@app.route("/set_led", methods=["POST"])
def set_led():
    if request.method == "POST":
        data = request.get_json()

        if ops.validate(("red", "green", "blue"), data):
            #_set_led(data["red"], data["green"], data["blue"])
            fade(current_state, {"red": data["red"], "green": data["green"], "blue": data["blue"]}, 10)

            return jsonify({"message": "LEDs changed"})

        else:
            abort(400, "Bad params")
    else:
        abort(405)


if __name__ == "__main__":
    pi = setup()
    _set_led(255,255,255)
    app.run(debug=True, host="0.0.0.0", port=6969)
