
# Barad-DF Local Web App

from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

# Default target frequency: 146.520 MHz, stored in Hz
selected_frequency = 146_520_000


@app.route("/")
def index():
    return render_template(
        "index.html",
        selected_frequency=selected_frequency,
        rssi_threshold_dbfs=None,
        lob_deg=None,
        rssi_dbm=None
    )


@app.route("/set-frequency", methods=["POST"])
def set_frequency():
    global selected_frequency

    try:
        # The HTML form submits frequency in MHz
        frequency_mhz = float(request.form["frequency_mhz"])

        # Supported frequency bands
        supported_bands = [
            (88.0, 108.0),    # FM broadcast
            (144.0, 148.0),   # 2m amateur radio
            (420.0, 450.0),   # 70cm amateur radio
            (902.0, 928.0),   # 915 MHz ISM
        ]

        if not any(low <= frequency_mhz <= high
                   for low, high in supported_bands):
            return (
                "Unsupported frequency. Choose FM 88–108 MHz, "
                "2m 144–148 MHz, 70cm 420–450 MHz, "
                "or 915 MHz ISM 902–928 MHz.",
                400
            )

        # Store frequency in Hz
        selected_frequency = round(frequency_mhz * 1_000_000)

        # TODO: Connect this to your RTL-SDR tuning function.

        # Return to the home page after submitting the form
        return redirect(url_for("index"))

    except (ValueError, KeyError):
        return "Invalid frequency value.", 400


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
