from flask import Flask, request, jsonify, abort
import operations as ops


app = Flask(__name__)
# Flask config
app.config["JSON_SORT_KEYS"] = False


@app.route("/set_led", methods=["POST"])
def set_led_endpoint():
    if request.method == "POST":
        data = request.get_json()

        if ops.validate(("red", "green", "blue", "fade_time"), data):
            if not ops.within_pwm_range((data["red"], data["green"], data["blue"])):
                return jsonify({"message": "RGB range must be 0-255"}), 400

            if ops.create_fade_thread(ops.current_state, (data["red"], data["green"], data["blue"]), data["fade_time"]):
                return jsonify({"message": "LEDs changing"})
            else:
                return jsonify({"message": "Busy - Fading already in progress"})

        else:
            return jsonify({"message": "Bad request"}), 400
    else:
        return jsonify({"message": "Method now allowed - Use POST"}), 405


@app.route("/fade", methods=["POST"])
def fade_between_endpoint():
    data = request.get_json()

    if request.method == "POST":
        if ops.validate(("red_start", "green_start", "blue_start", "red_end", "green_end", "blue_end", "fade_time"), data):
            if not ops.within_pwm_range((data["red_start"], data["green_start"], data["blue_start"], data["red_end"], data["green_end"], data["blue_end"])):
                return jsonify({"message": "RGB range range must be 0-255"}), 400
            else:
                if ops.create_fade_thread((data["red_start"], data["green_start"], data["blue_start"]), (data["red_end"], data["green_end"], data["blue_end"]), data["fade_time"]):
                    return jsonify({"message": "LEDs changing"})
                else:
                    return jsonify({"message": "Busy - Fading already in progress"}), 503

        else:
            return jsonify({"message": "Bad request"}), 400
    else:
        return jsonify({"message": "Method now alowed - Use POST"})


@app.route("/get_color", methods=["GET"])
def get_colour():
    if request.method == "GET":
        data = {"red": ops.current_state[0], "green": ops.current_state[1], "blue": ops.current_state[2]}
        return jsonify(data), 200
    else:
        return jsonify({"message": "Method not allowed - Use GET"}), 405


@app.route("/stop_fade", methods=["POST"])
def stop_fading():
    if request.method == "POST":
        if not ops.lamp_thread_busy:
            return jsonify({"message": "Thread is not running: nothing to stop"}), 412
        else:
            ops.kill_thread()
            return jsonify({"message": "Fading thread has been killed", "red": int(ops.current_state[0]), "green": int(ops.current_state[1]), "blue": int(ops.current_state[2])})
    else:
        return jsonify({"Method not allowed - Use POST"}), 405


if __name__ == "__main__":
    pi = ops.setup()
    app.run(debug=True, host="127.0.0.1", port=6969)
