# Barad-DF Local Web App
from flask import Flask, render_template, request, redirect, url_for, jsonify
import config
from shared import state, state_lock

app = Flask(__name__)


def _num(x):
    return None if x is None else float(x)


def status_snapshot():
    """Copy what the page needs out of the shared state, holding the lock only briefly."""
    with state_lock:
        freq_hz = state["freq_hz"]
        threshold = state["rssi_threshold_dbfs"]
        result = state["result"]
    out = {"freq_hz": freq_hz, "rssi_threshold_dbfs": threshold, "valid": False, "lob_deg": None,
           "std_deg": None, "rssi_dbfs": None, "contrast_db": None, "method": None, "reason": "waiting for data"}
    if result is not None:
        out.update(valid=bool(result["valid"]), lob_deg=_num(result.get("smoothed_bearing_deg")),
                   std_deg=_num(result.get("bearing_std_deg")), rssi_dbfs=_num(result.get("rssi_db")),
                   contrast_db=_num(result.get("contrast_db")), method=result.get("method"),
                   reason=result.get("reason", ""))
    return out


@app.route("/")
def index():
    s = status_snapshot()
    return render_template("index.html", selected_frequency=s["freq_hz"],
                           rssi_threshold_dbfs=s["rssi_threshold_dbfs"],
                           lob_deg=s["lob_deg"], rssi_dbfs=s["rssi_dbfs"])


@app.route("/api/status")
def api_status():
    return jsonify(status_snapshot())


@app.route("/set-frequency", methods=["POST"])
def set_frequency():
    try:
        # the form sends MHz
        frequency_hz = round(float(request.form["frequency_mhz"]) * 1_000_000)
        # raises ValueError if out of band
        config.get_band(frequency_hz)
    except (ValueError, KeyError, OverflowError):
        return ("Unsupported frequency. Choose FM 88-108 MHz, 2m 144-148 MHz, "
                "70cm 420-450 MHz, or 915 MHz ISM 902-928 MHz.", 400)
    with state_lock:
        state["freq_hz"] = frequency_hz
    return redirect(url_for("index"))


@app.route("/set-threshold", methods=["POST"])
def set_threshold():
    try:
        value = int(request.form["rssi_threshold_dbfs"])
    except (ValueError, KeyError):
        return "Invalid threshold.", 400
    if not -120 <= value <= -30:
        return "Threshold out of range.", 400
    with state_lock:
        state["rssi_threshold_dbfs"] = value
    return "", 204


def run_server():
    # debug=False and no reloader: the reloader would start a second copy of the program and a second capture loop
    app.run(host=config.WEB_HOST, port=config.WEB_PORT,
            debug=False, use_reloader=False)


if __name__ == "__main__":
    run_server()
