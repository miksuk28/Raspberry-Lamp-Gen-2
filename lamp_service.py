from flask import Flask, json, request, jsonify, abort
import operations as ops

pins = {"r": 17, "g": 22, "b": 24, "btn": 27}

def setup():
    import pigpio
    pi = pigpio.pi()

    return pi

def _set_led(r, g, b):
    pi.set_PWM_dutycycle(pins["r"], r)
    pi.set_PWM_dutycycle(pins["g"], g)
    pi.set_PWM_dutycycle(pins["b"], b)

app = Flask(__name__)

@app.route("/set_led", methods=["POST"])
def set_led():
    if request.method == "POST":
        data = request.get_json()
        
        if ops.validate(("r", "g", "b"), data):
            _set_led(data["red"], data["green"], data["blue"])

            return jsonify({"message": "LEDs changed"})

        else:
            abort(400, "Bad params")
    else:
        abort(405)


if __name__ == "__main__":
    pi = setup()
    app.run(debug=True, host="0.0.0.0", port=6969)