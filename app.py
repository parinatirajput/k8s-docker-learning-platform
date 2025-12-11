#!/usr/bin/env python3
from flask import Flask, render_template, request
import subprocess

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/run", methods=["POST"])
def run_command():
    cmd = request.form.get("command")

    try:
        result = subprocess.check_output(
            cmd,
            stderr=subprocess.STDOUT,
            shell=True,
            text=True   # Python 3.7+ (same as universal_newlines=True)
        )
    except subprocess.CalledProcessError as e:
        result = e.output

    return render_template("index.html", output=result)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

